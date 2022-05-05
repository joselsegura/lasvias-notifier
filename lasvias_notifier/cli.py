"""Submodule containing the CLI handlers."""

import argparse

from lasvias_notifier.web_parser import check_available
from lasvias_notifier.notifier import telegram_notify


def check()-> None:
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