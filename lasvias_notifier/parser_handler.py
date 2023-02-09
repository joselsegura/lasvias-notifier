import asyncio
import logging

import requests

from lasvias_notifier.web_parser import LasViasFilmsParser


class ParserHandler:
    def __init__(self, parser):
        self.logger = logging.getLogger(__class__.__name__)
        self.parser = parser
        self.subscribers = list()

    def subscribe(self, notify_cb):
        self.subscribers.append(notify_cb)

    async def notify(self, change):
        for sub in self.subscribers:
            await sub(change)

    async def feed_parser(self, text):
        old_titles = self.parser.titles
        self.parser.feed(text)

        diff = self.parser.titles - old_titles
        if diff:
            change = f"New films!\n"
            change += "\n".join(diff)
            await self.notify(change)

    async def parse_loop(self, url):
        while True:
            self.logger.info("Updating films list...")
            response = requests.get(url)
            await self.feed_parser(response.text)

            await asyncio.sleep(30)