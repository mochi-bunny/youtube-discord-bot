import os
import re
import asyncio
import discord
from google import genai
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

FALLBACK_QUERIES = [
    "did you know facts #shorts",
    "random facts #shorts",
    "amazing facts #shorts",
    "life hacks #shorts",
    "fun facts you didn't know #shorts",
]

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="yt.", intents=intents, help_command=None)


class QuotaExceededError(Exception):
    pass


def generate_search_queries() -> list[str]:
    prompt = (
        "Generate 5 unique and creative YouTube search queries for finding "
        "interesting short-form fact videos (YouTube Shorts). Each query should "
        "target a DIFFERENT topic area. Pick randomly from areas like: science, "
        "history, movies, psychology, space, ocean, animals, human body, geography, "
        "technology, food, ancient civilizations, inventions, optical illusions, "
        "world records, language, music theory, math, architecture, weather, "
        "mythology, medicine, economics, sports science, etc.\n\n"
        "Add '#shorts' to each query.\n"
        "Return ONLY the 5 queries, one per line, no numbering or bullets."
    )
    try:
        response = gemini_client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
        if len(lines) >= 3:
            return lines[:5]
    except Exception as e:
        print(f"Gemini query generation failed, using fallbacks: {e}")
    return FALLBACK_QUERIES


async def get_posted_video_ids(channel: discord.TextChannel, limit: int = 200) -> set[str]:
    posted_ids: set[str] = set()
    async for message in channel.history(limit=limit):
        if message.author != bot.user:
            continue
        for embed in message.embeds:
            if embed.url:
                match = re.search(r"(?:shorts/|watch\?v=)([\w-]+)", embed.url)
                if match:
                    posted_ids.add(match.group(1))
    return posted_ids


def search_youtube(query: str, max_results: int = 5, duration: str = "any") -> list[dict]:
    try:
        response = (
            youtube.search()
            .list(
                q=query,
                part="snippet",
                type="video",
                videoDuration=duration,
                order="relevance",
                maxResults=max_results,
            )
            .execute()
        )
    except HttpError as e:
        if e.resp.status == 403:
            raise QuotaExceededError("YouTube API daily quota exceeded. Try again tomorrow.")
        raise

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        if duration == "short":
            url = f"https://www.youtube.com/shorts/{video_id}"
        else:
            url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append(
            {
                "id": video_id,
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "channel": snippet["channelTitle"],
                "url": url,
                "thumbnail": snippet["thumbnails"]["high"]["url"],
            }
        )
    return videos


def fetch_daily_shorts(posted_ids: set[str], max_results_per_query: int = 5) -> list[dict]:
    queries = generate_search_queries()
    print(f"Search queries: {queries}")

    seen_ids: set[str] = set()
    videos: list[dict] = []

    for query in queries:
        try:
            for v in search_youtube(query, max_results=max_results_per_query, duration="short"):
                vid = v["id"]
                if vid in seen_ids or vid in posted_ids:
                    continue
                seen_ids.add(vid)
                videos.append(v)
        except QuotaExceededError:
            print(f"Quota exceeded during query: {query}")
            break

    return videos[:10]


def build_embed(video: dict, index: int = 0) -> discord.Embed:
    embed = discord.Embed(
        title=f"{index}. {video['title']}" if index else video["title"],
        url=video["url"],
        description=video["description"][:200] or "Watch this!",
        color=discord.Color.red(),
    )
    embed.set_thumbnail(url=video["thumbnail"])
    embed.set_footer(text=f"Channel: {video['channel']}")
    return embed


QUOTA_MESSAGE = (
    "⚠️ **YouTube API daily quota exceeded.**\n"
    "The free tier allows ~100 searches per day. "
    "Quota resets at midnight Pacific Time. Try again tomorrow!"
)


# --- Commands ---

@bot.command(name="vid")
async def yt_vid(ctx: commands.Context, *, query: str = None):
    if not query:
        await ctx.send("Please provide a search query. Usage: `yt.vid <search terms>`")
        return

    await ctx.send(f"🔍 Searching YouTube for **{query}**...")
    try:
        videos = search_youtube(query, max_results=5, duration="any")
    except QuotaExceededError:
        await ctx.send(QUOTA_MESSAGE)
        return

    if not videos:
        await ctx.send("No videos found for that query.")
        return

    header = f"🎬 **Top 5 YouTube Videos for:** {query}\n"
    await ctx.send(header)
    for i, video in enumerate(videos, 1):
        await ctx.send(embed=build_embed(video, index=i))
        await asyncio.sleep(0.3)


@bot.command(name="short")
async def yt_short(ctx: commands.Context, *, query: str = None):
    if not query:
        await ctx.send("Please provide a search query. Usage: `yt.short <search terms>`")
        return

    await ctx.send(f"🔍 Searching YouTube Shorts for **{query}**...")
    try:
        videos = search_youtube(query, max_results=5, duration="short")
    except QuotaExceededError:
        await ctx.send(QUOTA_MESSAGE)
        return

    if not videos:
        await ctx.send("No shorts found for that query.")
        return

    header = f"🎬 **Top 5 YouTube Shorts for:** {query}\n"
    await ctx.send(header)
    for i, video in enumerate(videos, 1):
        await ctx.send(embed=build_embed(video, index=i))
        await asyncio.sleep(0.3)


@bot.command(name="help")
async def yt_help(ctx: commands.Context):
    embed = discord.Embed(
        title="📖 YouTube Bot — Help",
        description="I curate YouTube videos and Shorts for you!",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="yt.vid <search terms>",
        value="Search YouTube and get the top 5 video links.\n"
              "Example: `yt.vid python tutorial for beginners`",
        inline=False,
    )
    embed.add_field(
        name="yt.short <search terms>",
        value="Search YouTube Shorts and get the top 5 short links.\n"
              "Example: `yt.short amazing science facts`",
        inline=False,
    )
    embed.add_field(
        name="yt.help",
        value="Show this help message.",
        inline=False,
    )
    embed.add_field(
        name="📅 Daily Auto-Post",
        value="Every 24 hours I automatically post the top 10 'Did You Know?' "
              "fact Shorts — powered by Gemini for varied topics daily.",
        inline=False,
    )
    embed.set_footer(text="Prefix: yt.  •  Powered by YouTube Data API + Gemini")
    await ctx.send(embed=embed)


# --- Daily auto-post ---

async def post_daily_shorts(channel: discord.TextChannel):
    posted_ids = await get_posted_video_ids(channel)
    print(f"Found {len(posted_ids)} previously posted videos")

    videos = fetch_daily_shorts(posted_ids)
    if not videos:
        await channel.send("No new shorts found today. Check back tomorrow!")
        return

    header = (
        "🎬 **Daily YouTube Shorts — Random Facts & Life Hacks**\n"
        f"Here are today's top {len(videos)} picks:\n"
    )
    await channel.send(header)
    for i, video in enumerate(videos, 1):
        await channel.send(embed=build_embed(video, index=i))
        await asyncio.sleep(0.5)

    print(f"Posted {len(videos)} videos")


@tasks.loop(hours=24)
async def daily_post():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(DISCORD_CHANNEL_ID)
    await post_daily_shorts(channel)


@daily_post.before_loop
async def before_daily_post():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not daily_post.is_running():
        daily_post.start()


# --- Run once mode for GitHub Actions ---

async def run_once():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(DISCORD_CHANNEL_ID)
    await post_daily_shorts(channel)
    await bot.close()


if __name__ == "__main__":
    run_mode = os.environ.get("RUN_MODE", "loop")

    if run_mode == "once":
        @bot.event
        async def on_ready():
            print(f"Logged in as {bot.user}")
            await run_once()

        bot.run(DISCORD_BOT_TOKEN)
    else:
        bot.run(DISCORD_BOT_TOKEN)
