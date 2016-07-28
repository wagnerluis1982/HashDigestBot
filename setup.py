#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name='hashdigestbot',
    version='0.0.1',
    description="Telegram bot to make digests of tagged messages.",
    long_description=readme + '\n\n' + history,
    author="Wagner Macedo",
    author_email='wagnerluis1982@gmail.com',
    url='https://github.com/wagnerluis1982/HashDigestBot',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'hdbot=hashdigestbot.hdbot:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    keywords='hashdigestbot',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat",
    ],
    test_suite='tests',
)
