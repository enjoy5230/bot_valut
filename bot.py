import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import require_bot_token
from database import get_recent_rates, init_db, save_rates
from parser import CurrencyRateError, fetch_currency_rate

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Привет! Я бот для отслеживания курса валют.\n\n"
        "📊 Команды:\n"
        "/rate - показать текущий курс USD/EUR\n"
        "/history - показать последние 5 записей\n"
        "/subscribe - подписаться на уведомления (в разработке)"
    )


# Команда /rate — парсим и сохраняем
@dp.message(Command("rate"))
async def rate_command(message: Message):
    await message.answer("🔄 Загружаю актуальные курсы...")

    try:
        rates = await fetch_currency_rate()
        save_rates({"USD": float(rates["USD"]), "EUR": float(rates["EUR"])})

        response = (
            f"💰 Курс валют на {rates['updated_at']}:\n\n"
            f"🇺🇸 USD: {_format_rate(float(rates['USD']))} ₽\n"
            f"🇪🇺 EUR: {_format_rate(float(rates['EUR']))} ₽"
        )
        await message.answer(response)
    except CurrencyRateError as exc:
        logger.warning("Currency rate loading failed: %s", exc)
        await message.answer(f"❌ {exc}")
    except Exception:
        logger.exception("Unexpected error while processing /rate")
        await message.answer("❌ Не удалось получить и сохранить курс. Попробуйте позже.")


# Команда /history — последние 5 курсов
@dp.message(Command("history"))
async def history_command(message: Message):
    rates = get_recent_rates(limit=5)

    if not rates:
        await message.answer("📭 Нет сохраненных данных. Используйте /rate")
        return

    lines = ["📈 Последние сохраненные курсы:"]
    for rate in rates:
        icon = "🇺🇸" if rate.currency == "USD" else "🇪🇺"
        created_at = rate.created_at.strftime("%d.%m.%Y %H:%M")
        lines.append(f"{icon} {rate.currency}: {_format_rate(rate.rate)} ₽ ({created_at})")

    response = "\n".join(lines)
    await message.answer(response)


@dp.message(Command("subscribe"))
async def subscribe_command(message: Message):
    await message.answer("🔔 Подписки пока в разработке. Сейчас можно смотреть курс через /rate.")


def _format_rate(rate: float) -> str:
    return f"{rate:.4f}".rstrip("0").rstrip(".")


# Запуск
async def main():
    try:
        token = require_bot_token()
    except RuntimeError as exc:
        logger.error("%s", exc)
        print(f"❌ {exc}")
        return

    bot = Bot(token=token)
    init_db()
    logger.info("Bot started")
    print("✅ Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
