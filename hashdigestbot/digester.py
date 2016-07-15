import re
from typing import Sequence, Iterable

HASHTAG_RE = re.compile(
    r"(?:^|\W+)"    # Ignore begin or non-words before '#'.
    r"#+(\w+"       # Match the hashtag,
    r"(?!#+.*))\b"  # but don't match if we have #two#tags
)


def hashtags(text: str) -> Iterable[str]:
    return set(HASHTAG_RE.findall(text))


class HashMessage:
    def __init__(self, id: int, text: str, reply_to: int = None):
        self.id = id
        self.text = text
        self.reply_to = reply_to


class Digester:
    def feed(self, message: HashMessage) -> bool:
        """Give a message to process tags

        The message will be added to the digest if has tags or is a reply to a
        previous message with tags.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        pass

    def get_subject(self, tag: str) -> Sequence[HashMessage]:
        """Sequence of messages related to this tag"""
        pass
