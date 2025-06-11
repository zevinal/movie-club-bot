import aiosqlite

DB_PATH = "movies.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year TEXT NOT NULL,
                suggester INTEGER NOT NULL,
                UNIQUE(title, year)
            )
        """)
        await db.commit()

async def add_movie(title, year, suggester):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO suggestions (title, year, suggester) VALUES (?, ?, ?)", 
                             (title, year, suggester))
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False

async def get_all_movies():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT title, year, suggester FROM suggestions")
        return await cursor.fetchall()

async def delete_movie(title, year):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM suggestions WHERE title = ? AND year = ?", (title, year))
        await db.commit()

async def get_random_movie():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT title, year, suggester FROM suggestions ORDER BY RANDOM() LIMIT 1")
        return await cursor.fetchone()

async def remove_suggestion(title_query, user):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT title, year FROM suggestions 
            WHERE LOWER(title) LIKE ? AND suggester = ?
            LIMIT 1
        """, (f"%{title_query.lower()}%", user))
        result = await cursor.fetchone()
        if result:
            await db.execute("DELETE FROM suggestions WHERE title = ? AND year = ?", result)
            await db.commit()
            return result
        else:
            return None
