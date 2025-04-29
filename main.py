import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
from function import initialize_db, join_raffle, choose_pidor, choose_krasavchik

# Загрузка токена
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здарова Работяги!1\n"
        "Готовы проверить удачу на вкус? а х*й?\n"
        "регайся если не сыкун /join \n\n"
        "Я КО-КО-КО Конор.\nПосмотрим кто вы на самом деле..."
    )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id  # Получаем идентификатор чата
    result = join_raffle(
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        user.full_name,
        user.language_code,
        chat_id
    )
    await update.message.reply_text(result)


async def pidor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f" {choose_pidor()}")


async def krasavchik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✨ {choose_krasavchik()}")


# === Запуск без asyncio.run() ===
if __name__ == "__main__":
    initialize_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("pidor", pidor))
    app.add_handler(CommandHandler("krasavchik", krasavchik))

    logger.info("Бот запущен.")
    app.run_polling()  # ← теперь просто так, без await
