import os
import re
import sys


def get_app_dir(app_name):
    """Get the most appropriate config folder for the operating system"""
    # Windows 2000, XP, Vista, 7, 8, ...
    if sys.platform.startswith('win'):
        folder = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.path.expanduser('~')))
    # MacOSX
    elif sys.platform == 'darwin':
        folder = os.path.expanduser('~/Library/Application Support')
    # Linux, UNIX, BSD, ...
    else:
        folder = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

    return os.path.join(folder, app_name)


# Useful regex patterns
RE_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
RE_USERNAME = re.compile(r"^@?(?:[a-zA-Z]|[a-zA-Z]\w*[a-zA-Z0-9]+)$")


def _validate_with_re(pattern, string, exception, message):
    if not pattern.match(string):
        if exception:
            raise exception(message % string)
        else:
            return False
    return True


def validate_username(username, exception=None):
    return _validate_with_re(RE_USERNAME, username, exception, "'%s' is not a valid username")


def validate_email_address(address, exception=None):
    return _validate_with_re(RE_EMAIL, address, exception, "'%s' is not a valid e-mail address")
