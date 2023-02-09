"""Submodule containing the CLI handlers."""

import argparse
import asyncio
import json
import logging
from threading import Timer

import requests

from lasvias_notifier.bot import Bot
from lasvias_notifier.parser_handler import ParserHandler
from lasvias_notifier.web_parser import check_available, LasViasHTMLParser, LasViasFilmsParser
from lasvias_notifier.notifier import telegram_notify


def check() -> None:
    """Handle the lasvias-check CLI command."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=True,
        help="Telegram API token for the bot",
    )
    parser.add_argument(
        "--chat-id",
        dest="chat_id",
        type=str,
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default="http://www.cineslasvias.es/Sesion"
    )
    parser.add_argument(
        "--last-known",
        dest="last_known",
        type=int,
    )
    args = parser.parse_args()

    if url := check_available(args.base_url, args.last_known):
        print("Algo se cuece")
        telegram_notify(args.token, args.chat_id, url)

    print("Bye!")


def parse_films() -> None:
    """Handle the lasvias-films CLI command."""

    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "-t",
    #     "--token",
    #     type=str,
    #     required=True,
    #     help="Telegram API token for the bot",
    # )
    # parser.add_argument(
    #     "--chat-id",
    #     dest="chat_id",
    #     type=str,
    # )
    parser.add_argument(
        "--url",
        dest="url",
        default="http://www.cineslasvias.es"
    )
    # parser.add_argument(
    #     "--send-first",
    #     dest="send_first",
    #     action="store_true",
    # )


    args = parser.parse_args()

    response = requests.get(args.url)
    # html_parser = LasViasHTMLParser()
    html_parser = LasViasFilmsParser()
    html_parser.feed(response.text)
    for title in sorted(html_parser.titles):
        print(title)

    # if not args.send_first:
    #     msg = "Current films:\n"
    #     for image in html_parser.images:
    #         msg += f"[{image}]({image})\n"

    #     telegram_notify(args.token, args.chat_id, msg)

    # def check():
    #     print("Checking again...")
    #     response = requests.get(args.url)
    #     html_parser.feed(response.text)
    #     msg = ""
    #     for image in html_parser.get_new_images():
    #         msg += f"[{image}]({image})\n"
    #     if msg:
    #         telegram_notify(args.token, args.chat_id, msg)
        
    #     t = Timer(60.0, check)
    #     t.start()

    # t = Timer(60.0, check)
    # t.start()

    # t.join()


def lasvias_bot():
    """Handle the lasvias-bot CLI command."""
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Launch")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=True,
        help="Telegram API token for the bot",
    )
    parser.add_argument(
        "--url",
        default="http://www.cineslasvias.es"
    )
    parser.add_argument(
        "-c",
        "--config",
        default="lasvias_bot.json",
    )
    args = parser.parse_args()

    html_parser = LasViasFilmsParser()
    handler = ParserHandler(html_parser)

    with open(args.config, "r") as config_file:
        config = json.load(config_file)
    
    bot = Bot(args.token, handler, config)
    bot.register_callbacks()
    
    try:
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(
                bot.start(),
                handler.parse_loop(args.url),
            )
        )
    
    except KeyboardInterrupt:
        pass

    bot.persist()
    logging.info("Bye!")

    return 0
