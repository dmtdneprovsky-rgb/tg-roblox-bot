import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from db import init_db, add_user, get_user, get_all, update_status

BOT_TOKEN = "8971497036:AAFUUj81LBtBqEGzKadA8AkZM8-HFLxaU0Y"
ADMIN_ID = 8409703144  # ТВОЙ Telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_temp = {}


# ---------------- START ----------------
@dp.message(Command("start"))
async def start(message: types.Message):
    user = await get_user(message.from_user.id)

    if user:
        status = user[3]

        if status == "blocked":
            await message.answer("⛔ Вы заблокированы.")
            return

        if status == "pending":
            await message.answer("⏳ Ваша заявка уже на проверке.")
            return

        if status == "approved":
            await message.answer("✅ Вы уже одобрены.")
            return

    user_temp[message.from_user.id] = {}
    await message.answer("👋 Введите ваш Roblox ник (@name):")


# ---------------- ANKETA ----------------
@dp.message()
async def handle(message: types.Message):
    uid = message.from_user.id

    if uid not in user_temp:
        return

    data = user_temp[uid]

    if "roblox" not in data:
        data["roblox"] = message.text
        await message.answer("🎮 Теперь введите ваш YouTube ник:")
        return

    if "youtube" not in data:
        data["youtube"] = message.text

        await add_user(uid, data["roblox"], data["youtube"])

        await message.answer("⏳ Заявка отправлена на проверку!")

        await bot.send_message(
            ADMIN_ID,
            f"📥 Новая заявка!\nID: {uid}\nRoblox: {data['roblox']}\nYouTube: {data['youtube']}"
        )

        user_temp.pop(uid)


# ---------------- ADMIN LIST ----------------
@dp.message(Command("list"))
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = await get_all()

    text = "📋 Заявки:\n\n"

    for u in users:
        text += f"ID: {u[0]}\nRoblox: {u[1]}\nYT: {u[2]}\nStatus: {u[3]}\n\n"

    await message.answer(text)


# ---------------- APPROVE ----------------
@dp.message(Command("approve"))
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.text.split()[1])
    await update_status(uid, "approved")
    await message.answer("✅ Одобрено")


# ---------------- REJECT ----------------
@dp.message(Command("reject"))
async def reject(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.text.split()[1])
    await update_status(uid, "rejected")
    await message.answer("❌ Отклонено")


# ---------------- BAN ----------------
@dp.message(Command("ban"))
async def ban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.text.split()[1])
    await update_status(uid, "blocked")
    await message.answer("⛔ Заблокирован")


# ---------------- RUN ----------------
async def main():
    await init_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
