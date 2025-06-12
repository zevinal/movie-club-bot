import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
import os
from dotenv import load_dotenv
from db import init_db, add_movie, get_all_movies, get_random_movie, delete_movie, remove_suggestion
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
        
        # Take the first result if only one movie is found with the title
        if len(results) == 1:
            selected = results[0]
            added = await add_movie(selected["title"], selected["year"], interaction.user.id)
            if added:
                await interaction.response.send_message(
                    f"✅ Suggested **{selected['title']} ({selected['year']})** by <@{interaction.user.id}>", allowed_mentions=discord.AllowedMentions.none()
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ Movie **{selected['title']} ({selected['year']})** is already in the draw.", ephemeral=True
                )
            return

        # Show dropdown UI if multiple results have been found for the title
        view = MovieSelectView(interaction, results)
        await interaction.response.send_message(
            "🎬 Multiple matches found. Please choose:",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="draw_movie", description="Randomly pick a movie from the list")
    async def draw_movie(self, interaction: discord.Interaction):
        movie = await get_random_movie()
        if not movie:
            await interaction.response.send_message("No movies in the hat yet!", ephemeral=True)
            return
        
        title, year, suggester = movie
        await delete_movie(title, year)
        await interaction.response.send_message(f"🎬 The movie for this week is **{title} ({year})** - suggested by **<@{suggester}>**!", allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="list_movies", description="List all suggested movies")
    async def list_movies(self, interaction: discord.Interaction):
        movies = await get_all_movies()
        if not movies:
            await interaction.response.send_message("There are no movies in the hat yet!", ephemeral=True)
            return
        
        response = "**🎞️ Movie Suggestions:**\n\n"
        for title, year, suggester in movies:
            response += f"- **{title} ({year})** - suggested by <@{suggester}>\n"

        await interaction.response.send_message(response[:2000], allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="remove_suggestion", description="Remove your own movie suggestion")
    @app_commands.describe(title="Type the partial or full title of the movie you wish to remove from the list")
    async def remove_suggestion(self, interaction: discord.Interaction, title: str):
        removed = await remove_suggestion(title, interaction.user.id)
        if removed:
            await interaction.response.send_message(
                f"🗑️ Removed **{removed[0]} ({removed[1]})** from the list."
            )
        else:
            await interaction.response.send_message(
                f"❌ Could not find a suggestion titled '{title}' made by you.", ephemeral=True
            )

# Dropdown selection UI
class MovieSelect(Select):
    def __init__(self, interaction: discord.Interaction, results: list):
        self.interaction = interaction
        options = [
            discord.SelectOption(
                label=movie["title"],
                description=movie["year"],
                value=f"{movie['title']}|{movie['year']}"
            )
            for movie in results
        ]
        super().__init__(placeholder="Please select the movie you're looking for...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Only <@{interaction.user.id}> can select from this list.", allowed_mentions=discord.AllowedMentions.none())
            return
        
        title, year = self.values[0].split("|")
        added = await add_movie(title, year, self.interaction.user.id)

        if added:
            # Show the user the film they requested has been accepted
            await interaction.response.edit_message(
                content="✅ Suggestion received!", view=None, allowed_mentions=discord.AllowedMentions.none()
            )
            # Show the group the suggestion
            await interaction.followup.send(
                f"✅ Suggested **{title} ({year})** by <@{interaction.user.id}>", allowed_mentions=discord.AllowedMentions.none()
            )
        else:
            await interaction.response.edit_message(
                content=f"⚠️ Movie **{title} ({year})** is already in the draw.", view=None, allowed_mentions=discord.AllowedMentions.none()
            )

class MovieSelectView(View):
    def __init__(self, interaction: discord.Interaction, results: list):
        super().__init__(timeout=30)
        self.add_item(MovieSelect(interaction, results))

bot.tree.add_command(MovieBot().suggest_movie)
bot.tree.add_command(MovieBot().draw_movie)
bot.tree.add_command(MovieBot().list_movies)
bot.tree.add_command(MovieBot().remove_suggestion)

bot.run(TOKEN)