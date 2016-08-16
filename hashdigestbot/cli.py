#!/usr/bin/env python3
import argparse
import contextlib
import logging
import os

from telegram import TelegramError

from . import hdbot, util

ENVVAR_PREFIX = 'HDBOT'


# A simple specialization of `argparse.ArgumentParser` to also read the values from environment vars.
class ArgumentParserEV(argparse.ArgumentParser):
    def __init__(self, *args, envvar_prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_env = envvar_prefix is not None
        if self.from_env:
            self.envvar_prefix = envvar_prefix+'_' if envvar_prefix else ''

    def add_argument(self, *args, from_env=None, **kwargs):
        # when adding help option, this object hasn't 'from_env' attribute yet
        if not hasattr(self, 'from_env'):
            return super().add_argument(*args, **kwargs)

        # create action and change it if needed
        action = super().add_argument(*args, **kwargs)
        from_env = self.from_env if from_env is None else from_env
        if from_env:
            envname = '%s%s' % (self.envvar_prefix, action.dest.upper())
            if envname in os.environ:
                action.default = os.environ[envname]
                action.required = False
        return action


class OptionValuesAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None,
                 required=False, help=None, metavar=None):
        if not option_strings:
            raise ValueError('at least one option argument must be supplied')
        if nargs == 0:
            raise ValueError('nargs for option-values actions must be > 0')
        if const is not None and nargs != argparse.OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % argparse.OPTIONAL)
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, (option_string, values))


class CLIError(Exception):
    pass


class CLI:
    @staticmethod
    def start(token, db_url):
        """Initialize the bot"""
        try:
            digestbot = hdbot.HDBot(token, db_url)
        except Exception as e:
            raise CLIError(e)
        else:
            digestbot.start()

    @staticmethod
    def config(token, db_url, op_name, values):
        operation, name = op_name

        try:
            digestbot = hdbot.HDBot(token, db_url)
            cfg = digestbot.get_config()
            logging.info("Using configuration at %s", db_url)
        except Exception as e:
            raise CLIError(e)

        with contextlib.closing(digestbot):
            if operation == '--add' and name == 'chat':
                # validation
                if len(values) < 2:
                    raise CLIError("Not enough arguments for --add chat")

                # get values
                name = values[0]
                email = values[1]
                # validations
                util.validate_username(name, exception=CLIError)
                util.validate_email_address(email, exception=CLIError)

                # get extra values if provided
                try:
                    extra = dict(v.split('=') for v in values[2:])
                except ValueError:
                    raise CLIError("Bad format in extra values for --add chat")

                # ensure the format @groupname
                name = '@'+name if name[0] != '@' else name

                # get chat_id
                try:
                    tgchat = digestbot.get_chat(name)
                except TelegramError:
                    raise CLIError("chat '%s' not found" % name)

                # add this chat to the config database
                try:
                    cfg.add_chat(chat_id=tgchat.id, name=name[1:], sendto=email, **extra)
                except TypeError as e:
                    raise CLIError(e)

    @classmethod
    def __run__(cls, parsed_args):
        # dispatch a command
        command = parsed_args.__dict__.pop('_command_')
        getattr(cls, command)(**parsed_args.__dict__)


def main():
    app_dir = util.get_app_dir('hashdigestbot')
    os.makedirs(app_dir, exist_ok=True)

    parser = ArgumentParserEV(
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description="Hashtag Digester Bot\n\n"
                    "A Telegram bot to make digests of tagged messages",
    )

    common = ArgumentParserEV(add_help=False, envvar_prefix=ENVVAR_PREFIX)
    common.add_argument('-t', '--token', required=True, help='Telegram bot token')
    common.add_argument('--db', dest='db_url', help='Database url for the digester',
                        default='sqlite:///' + os.path.join(app_dir, 'digester.db'))

    subparsers = parser.add_subparsers(dest='_command_')

    cmd_start = subparsers.add_parser("start", parents=[common], help="Initialize the bot")

    cmd_config = subparsers.add_parser("config", parents=[common], help="Configure the bot")
    group = cmd_config.add_mutually_exclusive_group(required=True)
    group.add_argument('--add', dest='op_name', help='Adds some new values to the option',
                       choices=['chat'], action=OptionValuesAction)
    cmd_config.add_argument('values', metavar='value', nargs='*')

    # Logging configuration
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    hdbot.LOG.setLevel(logging.DEBUG)

    args = parser.parse_args()
    try:
        CLI.__run__(args)
    except KeyError:
        parser.exit(message=parser.format_help())
    except CLIError as e:
        parser.error(e)


if __name__ == "__main__":
    main()
