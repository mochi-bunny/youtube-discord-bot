# Discord Bot for Curating YouTube Shorts

This Discord bot automatically curates and shares top YouTube Shorts channels or videos featuring "Did You Know?" facts and life hacks on a daily basis. It retrieves the latest videos using the YouTube Data API, formats them into a user-friendly message, and posts the message to a designated Discord channel.

## Features

- Retrieves top YouTube Shorts channels or videos related to "Did You Know?" facts and life hacks.
- Curates a list of the latest videos based on relevance and popularity.
- Formats the curated list into a user-friendly message with video titles, descriptions, and watch links.
- Posts the curated list to a designated Discord channel on a daily basis.
- Runs automatically using GitHub Actions for continuous operation.

## Prerequisites

- Python 3.x installed
- Discord account and server
- YouTube Data API credentials
- GitHub account and repository

## Setup and Installation

1. Clone the GitHub repository containing the bot script and workflow files.

2. Install the required dependencies by running the following command:

pip install -r requirements.txt


3. Set up a new Discord application and bot account in the Discord Developer Portal.

4. Invite the bot to your Discord server and grant it the necessary permissions.

5. Enable the YouTube Data API in the Google Cloud Console and obtain the API credentials.

6. Configure the bot by setting the following environment variables:
   - `DISCORD_CHANNEL_ID`: The ID of the Discord channel where the bot should post the curated list.
   - `YOUTUBE_API_KEY`: Your YouTube Data API key.
   - `DISCORD_BOT_TOKEN`: The token of your Discord bot.

7. Deploy the bot using GitHub Actions:
   - Create a new workflow file (e.g., `youtube_shorts_bot.yml`) in the `.github/workflows` directory of your GitHub repository.
   - Configure the workflow to run on a daily schedule using the `schedule` event and `cron` syntax.
   - Specify the necessary steps to set up Python, install dependencies, and run the bot script.
   - Add the required environment variables as secrets in your GitHub repository's "Settings" tab.

8. Push the changes to your GitHub repository to trigger the workflow and start the bot.

## Usage

Once the bot is set up and deployed, it will automatically run on a daily basis according to the specified schedule. The bot will perform the following steps:

1. Retrieve the top YouTube Shorts channels or videos related to "Did You Know?" facts and life hacks using the YouTube Data API.
2. Curate a list of the latest videos based on relevance and popularity.
3. Format the curated list into a user-friendly message with video titles, descriptions, and watch links.
4. Post the curated list to the designated Discord channel.

The bot will continue to run daily, providing fresh content to your Discord community.

## Customization

You can customize the bot's behavior and functionality by modifying the `youtube_shorts_bot.py` script:

- Adjust the search query and parameters to retrieve videos based on different criteria.
- Modify the message formatting and layout to suit your preferences.
- Change the scheduling frequency in the GitHub Actions workflow file to post at different intervals.

Make sure to update the environment variables and secrets in your GitHub repository if you modify the bot's configuration.

## Contributing

Contributions to the Discord bot project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Discord.py](https://discordpy.readthedocs.io/) - Python library for interacting with the Discord API.
- [YouTube Data API](https://developers.google.com/youtube/v3) - API for retrieving YouTube video information.
- [GitHub Actions](https://docs.github.com/en/actions) - Automated workflow and deployment tool.