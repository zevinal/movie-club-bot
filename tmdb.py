import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

async def search_movies(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            results = [
                {
                    "title": movie["title"],
                    "year": movie.get("release_date", "????")[:4],
                    "id": movie["id"] # Adding the movie ID helps avoid crashes when 2 movies with the same name were released in the same year e.g. Mulan(2020) - Disney, and Mulan(2020) - China
                }
                for movie in data.get("results", [])[:5]
            ]
            return results