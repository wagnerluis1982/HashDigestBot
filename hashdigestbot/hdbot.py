#!/usr/bin/env python3

import logging

import click
from telegram.error import TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from . import digester

LOG = logging.getLogger("hdbot")


class HDBot:
    def __init__(self, token, db_url, chat_names=()):
        # connect to Telegram with the desired token
        self.updater = Updater(token=token)
        self.bot = self.updater.bot

        # configure the bot behavior
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.send_welcome))
        dispatcher.add_handler(MessageHandler([Filters.text], self.filter_tags))

        # create a digester backed by the desired database
        try:
            self.digester = digester.Digester(db_url)
        except Exception as e:
            self.stop()
            raise e
        self.db_url = db_url

        # set the digester to allow digesting the desired chats
        chats = []
        for name in chat_names:
            try:
                chats.append(self.bot.getChat(name))
            except TelegramError as e:
                self.stop()
                raise ValueError("chat '%s' not found" % name) from e
        self.digester.allow_digesting(chats)

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
        LOG.info("Hashtag Digester Bot started")
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("Bot username: %s", self.bot.getMe().name)
            LOG.debug("Digests database: %s", self.db_url)

    def stop(self):
        self.updater.stop()


CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='HDBOT',
)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-t', '--token', required=True, help='Telegram bot token')
@click.option('-u', '--db-url', required=True, help='Database url')
@click.option('-c', '--chat', 'chats', required=True, multiple=True, metavar='NAME',
              help='Allow digesting messages of a desired Telegram group in the format @groupname')
def main(token, db_url, chats):
    """Hashtag Digester Bot

    A Telegram bot to make digests of tagged messages
    """
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    LOG.setLevel(logging.DEBUG)
    try:
        digestbot = HDBot(token, db_url, chats)
    except Exception as e:
        raise click.UsageError(e)
    else:
        digestbot.start()


if __name__ == "__main__":
    main()
