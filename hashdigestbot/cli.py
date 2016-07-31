#!/usr/bin/env python3

import logging
from collections import namedtuple
from functools import partial

import click

from . import hdbot

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='HDBOT',
)


options = dict(
    token=click.option('-t', '--token', required=True, help='Telegram bot token'),
    db_url=click.option('-u', '--db-url', required=True, help='Database url'),
    chat=click.option('-c', '--chat', 'chats', required=True, multiple=True, metavar='NAME',
                      help='Allow digesting messages of a desired Telegram group in the format @groupname'),
)
options = namedtuple('options', options.keys())(**options)


@click.group()
def main():
    """Hashtag Digester Bot

    A Telegram bot to make digests of tagged messages
    """
main.command = partial(main.command, context_settings=CONTEXT_SETTINGS)


@main.command()
@options.token
@options.db_url
@options.chat
def start(token, db_url, chats):
    """Initialize the bot"""
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    hdbot.LOG.setLevel(logging.DEBUG)
    try:
        digestbot = hdbot.HDBot(token, db_url, chats)
    except Exception as e:
        raise click.UsageError(e)
    else:
        digestbot.start()


if __name__ == "__main__":
    main()
