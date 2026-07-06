import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Получить у @BotFather
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///currency_rates.db")


def require_bot_token() -> str:
    """Return bot token or raise a clear startup error."""
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Добавьте токен бота в файл .env")
    return BOT_TOKEN
