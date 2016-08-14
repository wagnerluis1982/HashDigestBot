import os
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
