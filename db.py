import aiosqlite

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            roblox TEXT,
            youtube TEXT,
            status TEXT
        )
        """)
        await db.commit()


async def add_user(tg_id, roblox, youtube):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR REPLACE INTO users (telegram_id, roblox, youtube, status)
        VALUES (?, ?, ?, COALESCE((SELECT status FROM users WHERE telegram_id=?), 'pending'))
        """, (tg_id, roblox, youtube, tg_id))
        await db.commit()


async def get_user(tg_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM users WHERE telegram_id=?", (tg_id,))
        return await cur.fetchone()


async def get_all():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM users")
        return await cur.fetchall()


async def update_status(tg_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET status=? WHERE telegram_id=?",
            (status, tg_id)
        )
        await db.commit()