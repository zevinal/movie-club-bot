import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from db import init_db, add_movie, get_all_movies, get_random_movie, delete_movie
from tmdb import search_movies

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await init_db()
    await bot.tree.sync()
    print(f"{bot.user} is now running!")

class MovieBot(commands.Cog):
    @app_commands.command(name="suggest_movie", description="Suggest a movie to add to the list")
    @app_commands.describe(movie="Start typing a movie title...")
    async def suggest_movie(self, interaction: discord.Interaction, movie: str):
        results = await search_movies(movie)
        if not results:
            await interaction.response.send_message("No movies found with that title!", ephemeral=True)
            return
        
        # For simplicity's sake, take the first result for now (will change to dropdown in future)
        selected = results[0]
        added = await add_movie(selected["title"], selected["year"], interaction.user.display_name)
        if added:
            await interaction.response.send_message(
                f"✅ Suggested **{selected['title']} ({selected['year']})** by {interaction.user.display_name}"
            )
        else:
            await interaction.response.send_message(
                f"⚠️ Movie **{selected['title']} ({selected['year']})** is already in the draw.", ephemeral=True
            )

    @app_commands.command(name="draw_movie", description="Randomly pick a movie from the list")
    async def draw_movie(self, interaction: discord.Interaction):
        movie = await get_random_movie()
        if not movie:
            await interaction.response.send_message("No movies in the hat yet!", ephemeral=True)
            return
        
        title, year, suggester = movie
        await delete_movie(title, year)
        await interaction.response.send_message(f"🎬 The movie for this week is **{title} ({year})** - suggested by **{suggester}**!")

bot.tree.add_command(MovieBot().suggest_movie)
bot.tree.add_command(MovieBot().draw_movie)

bot.run(TOKEN)