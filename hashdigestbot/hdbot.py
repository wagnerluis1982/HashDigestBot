import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from . import digester

LOG = logging.getLogger("hdbot")


class HDBot:
    def __init__(self, token, db_url):
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

        # dispatcher methods
        self.get_config = self.digester.get_config
        self.get_chat = self.bot.getChat

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

    # suitable to be used by `contextlib.closing`
    def close(self):
        self.stop()
