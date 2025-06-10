# Movie Club Discord Bot

The movie club bot acts as a sort of raffle or roulette system for picking movie titles out of a user-made database for ease of random selections within movie clubs.

## Features
- `/suggest_movie <title>`: Suggest a film using TMDB API.
- `/draw_movie`: Randomly select a film from the suggestions.
- Prevents duplicate movie suggestions.
- Logs who suggested which film.

## Setup

This bot will help you pick a random movie out of a 'hat' in Discord and allows users to add their own suggestions to the database.

1. Open the [Discord Developer Portal](https://discord.com/developers/applications/)
2. Create a new application
3. Click on the "Bot" tab on the left.
4. Copy your bot's token and save it for later.
5. Make sure you enable `Message Content Intent`
6. In the "OAuth2" tab on the left, go to the URL Generator, add the "bot" and "applications.commands" scopes, and invite the bot to your server.
7. Create a [TMDB](https://www.themoviedb.org/) account and get your [API key](https://www.themoviedb.org/settings/api)

### Setting up the bot

1. Clone the repo
```bash
git clone https://github.com/zevinal/movie-club-bot.git
cd movie-club-bot
```
2. Install dependancies
```bash
pip install -r requirements.txt
```
3. Create a `.env` file from the example
```bash
cp .env.example .env
```
4. Fill in your `.env` file with your Discord bot token and TMDB API key.
5. Run the bot
```bash
python bot.py
```

### Notes

- Uses SQLite for simple storage.
- You can expand this bot to include listing, removing, and tracking past movie draws.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)