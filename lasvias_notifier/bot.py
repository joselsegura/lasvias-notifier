"""Bot class for handling the whole bot."""

import json
import logging

from aiogram import Dispatcher, executor
from aiogram import Bot as AIOBot
from aiogram.types import Message

from lasvias_notifier.parser_handler import ParserHandler


class Bot:
    """Bot handler."""
    def __init__(self, bot_token: str, handler: ParserHandler, config: dict) -> None:
        """Initialize the Bot object and running the dispatcher."""
        self.logger = logging.getLogger(__class__.__name__)
        self.bot = AIOBot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        self.handler = handler

        if config:
            self.subscribed_users = config.get("subscribers", list())
        else:
            self.subscribed_users = list()

    def register_callbacks(self):
        """Add the needed callbacks to the dispatcher."""
        self.dp.register_message_handler(self.films_list, commands=["list"])
        self.dp.register_message_handler(self.subscribe_updates, commands=["subscribe"])

    async def start(self):
        """Make the bot to start waiting for requests from the network."""
        await self.dp.start_polling()

    async def films_list(self, message: Message):
        """Handle the list command from a private."""
        titles = self.handler.parser.titles

        response = "\n".join(sorted(titles))
        await message.answer(response)

    async def subscribe_updates(self, message: Message):
        user_id = message.from_user.id
        self.logger.info(
            "Subscription petition from %s. It will be removed after restart!",
            user_id,
        )
        self.subscribed_users.append(user_id)
        self.handler.subscribe(self.notify_subscribed_users)
        await message.answer("Ok. I will notify you when a new film is added")

    async def notify_subscribed_users(self, message: str):
        for user in self.subscribed_users:
            await self.bot.send_message(user, message)

    def persist(self):
        """Store the subscriber configuration for the next time."""
        config = {
            "subscribers": self.subscribed_users,
        }

        with open("lasvias_bot.json", "w") as config_file:
            json.dump(config, config_file)
