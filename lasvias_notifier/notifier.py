"""Submodule with notification methods."""

from aiogram import Bot, Dispatcher, executor


def telegram_notify(token: str, chat_id: int, text: str) -> None:
    """Send a notification to Telegram."""

    bot = Bot(token=token)
    dp = Dispatcher(bot)
    executor.start(dp, send_telegram_message(bot, chat_id, text))


async def send_telegram_message(bot, chat_id, text):
    try:
        await bot.send_message(chat_id, text, parse_mode="markdown")
    except Exception as ex:
        print(ex)