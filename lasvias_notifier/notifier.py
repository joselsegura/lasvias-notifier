"""Submodule with notification methods."""

from aiogram import Bot, Dispatcher, executor


def telegram_notify(token: str, chat_id: int, url: str) -> None:
    """Send a notification to Telegram."""

    bot = Bot(token=token)
    dp = Dispatcher(bot)
    executor.start(dp, send_telegram_message(bot, chat_id, url))


async def send_telegram_message(bot, chat_id, url):
    try:
        await bot.send_message(chat_id, f"Uh, uh... algo se cuece... {url}")
    except Exception as ex:
        print(ex)