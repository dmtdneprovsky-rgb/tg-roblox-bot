import logging
from aiogram import Bot, Dispatcher, executor, types
from db import init_db, add_user, get_user, get_all, update_status

BOT_TOKEN = "8971497036:AAFUUj81LBtBqEGzKadA8AkZM8-HFLxaU0Y"
ADMIN_ID = 8409703144

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_temp = {}


# ---------------- START ----------------
@dp.message_handler(commands=["start"])
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
@dp.message_handler()
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
            f"📥 Новая заявка!\n\n"
            f"ID: {uid}\n"
            f"Roblox: {data['roblox']}\n"
            f"YouTube: {data['youtube']}"
        )

        user_temp.pop(uid)


# ---------------- LIST ----------------
@dp.message_handler(commands=["list"])
async def list_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = await get_all()

    text = "📋 Заявки:\n\n"

    for u in users:
        text += (
            f"ID: {u[0]}\n"
            f"Roblox: {u[1]}\n"
            f"YT: {u[2]}\n"
            f"Status: {u[3]}\n\n"
        )

    await message.answer(text)


# ---------------- APPROVE ----------------
@dp.message_handler(commands=["approve"])
async def approve(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.get_args())

    await update_status(uid, "approved")

    await message.answer("✅ Одобрено")


# ---------------- REJECT ----------------
@dp.message_handler(commands=["reject"])
async def reject(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.get_args())

    await update_status(uid, "rejected")

    await message.answer("❌ Отклонено")


# ---------------- BAN ----------------
@dp.message_handler(commands=["ban"])
async def ban(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    uid = int(message.get_args())

    await update_status(uid, "blocked")

    await message.answer("⛔ Заблокирован")


# ---------------- START BOT ----------------
async def on_startup(_):
    await init_db()
    print("Бот запущен!")

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
