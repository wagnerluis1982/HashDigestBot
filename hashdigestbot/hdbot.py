#!/usr/bin/env python3

import logging

import click
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from . import digester

LOG = logging.getLogger("hdbot")


class HDBot:
    def __init__(self, token, db_url):
        self.updater = Updater(token=token)

        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.send_welcome))
        dispatcher.add_handler(MessageHandler([Filters.text], self.filter_tags))

        self.digester = digester.Digester(db_url)
        self.db_url = db_url

    @staticmethod
    def send_welcome(bot, update):
        message = update.message
        LOG.info("%s: %s" % (message.from_user.username, message.text))
        bot.sendMessage(chat_id=message.chat_id,
                        text="Hello, I'm a bot who makes digests of messages with hashtags!",
                        reply_to_message_id=message.message_id)

    def filter_tags(self, _, update):
        """Send the message to the digest for processing

        A tagged message will be added to it belonged chat digest
        """
        message = update.message
        if self.digester.feed(message) and LOG.isEnabledFor(logging.DEBUG):
            LOG.info("Message from %s: %s", message.from_user.username, message.text)

    def start(self):
        self.updater.start_polling(clean=True)
        LOG.info("Bot started")
        LOG.info("Using database '%s'" % self.db_url)


@click.command()
@click.option('-t', '--token', required=True, help='Telegram bot token')
@click.option('-u', '--db-url', required=True, help='Database url')
def main(token, db_url):
    """Hashtag Digester Bot

    A Telegram bot to make digests of tagged messages
    """
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    LOG.setLevel(logging.DEBUG)
    try:
        digestbot = HDBot(token, db_url)
    except Exception as e:
        raise click.UsageError(e)
    else:
        digestbot.start()


if __name__ == "__main__":
    main(auto_envvar_prefix='HDBOT')