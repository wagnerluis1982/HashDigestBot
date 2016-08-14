#!/usr/bin/env python3
import argparse
import contextlib
import logging
import os

from telegram import TelegramError

from . import hdbot, util

ENVVAR_PREFIX = 'HDBOT'


class CLIError(Exception):
    pass


#
# Adaptations to `argparse` action classes to also read the values from environment vars.
# Since the adapted classes are private, they are likely to broke in the future.
#

class StoreAction(argparse._StoreAction):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None,
                 required=False, help=None, metavar=None):
        evname = '%s_%s' % (ENVVAR_PREFIX, dest.upper())
        if evname in os.environ:
            default = os.environ[evname]
            required = False
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)


class AppendAction(argparse._AppendAction):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None,
                 required=False, help=None, metavar=None, sep=None):
        evname = '%s_%s' % (ENVVAR_PREFIX, dest.upper())
        if evname in os.environ:
            default = os.environ[evname].split(sep)
            required = False
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)


def run_command(parsed_args):
    def start(token, db_url):
        """Initialize the bot"""
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        hdbot.LOG.setLevel(logging.DEBUG)
        try:
            digestbot = hdbot.HDBot(token, db_url)
        except Exception as e:
            raise CLIError(e)
        else:
            digestbot.start()

    def config(token, db_url, to_add, values):
        try:
            digestbot = hdbot.HDBot(token, db_url)
            cfg = digestbot.get_config()
        except Exception as e:
            raise CLIError(e)

        with contextlib.closing(digestbot):
            if to_add == 'chat':
                # get values
                name = values[0]
                email = values[1]
                extra = dict(v.split('=') for v in values[2:])

                # get chat_id
                try:
                    tgchat = digestbot.get_chat(name)
                except TelegramError:
                    raise CLIError("chat '%s' not found" % name)

                # add this chat to the config database
                cfg.add_chat(chat_id=tgchat.id, name=name[1:], sendto=email, **extra)

    # dispatch command
    command = parsed_args.__dict__.pop('_command_')
    locals()[command](**parsed_args.__dict__)


def main():
    app_dir = util.get_app_dir('hashdigestbot')
    os.makedirs(app_dir, exist_ok=True)

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description="Hashtag Digester Bot\n\n"
                    "A Telegram bot to make digests of tagged messages",
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-t', '--token', required=True, action=StoreAction, help='Telegram bot token')
    common.add_argument('--db', dest='db_url', action=StoreAction, help='Database url for the digester',
                        default='sqlite:///' + os.path.join(app_dir, 'digester.db'))

    subparsers = parser.add_subparsers(dest='_command_')

    cmd_start = subparsers.add_parser("start", parents=[common], help="Initialize the bot")

    cmd_config = subparsers.add_parser("config", parents=[common], help="Configure the bot")
    group = cmd_config.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', dest='to_add', help='Adds some new values to the option',
                       choices=['chat'])
    cmd_config.add_argument('values', metavar='value', nargs='*')

    args = parser.parse_args()
    try:
        run_command(args)
    except KeyError:
        parser.exit(message=parser.format_help())
    except CLIError as e:
        parser.error(e)


if __name__ == "__main__":
    main()
