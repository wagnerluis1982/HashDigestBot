import re
from typing import Sequence, Tuple, FrozenSet, Iterator, Union

import telegram

from .model.database import connect, HashMessage

HASHTAG_RE = re.compile(
    r"(?:^|\W+)"    # Ignore begin or non-words before '#'.
    r"#+(\w+"       # Match the hashtag,
    r"(?!#+.*))\b"  # but don't match if we have #two#tags
)


def hashtags(text: str) -> FrozenSet[str]:
    return frozenset(HASHTAG_RE.findall(text))


class Digester:
    def __init__(self):
        self.db = connect("sqlite:///")

    def feed(self, message: Union[HashMessage, telegram.Message]) -> bool:
        """Give a message to process tags

        The message will be added to the digest if has tags or is a reply to a
        previous message with tags.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        # Normalize the type
        if isinstance(message, telegram.Message):
            reply_msgid = message.reply_to_message.id if message.reply_to_message else None
            message = HashMessage(
                id=message.message_id,
                text=message.text,
                chat_id=message.chat_id,
                reply_to=reply_msgid,
            )
        # Extract tags from the message
        tags = hashtags(message.text)
        # Tags found in the message? So, mark them and return.
        if tags:
            self.db.add_message(message, tags)
            return True
        # Otherwise, check if message is a reply to a previous tagged message.
        # In that case, we mark them, but asking for don't register variations.
        elif message.reply_to:
            tags = self.db.get_tags(message.reply_to)
            if tags:
                self.db.add_message(message, tags, is_variations=False)
                return True
        return False

    def digest(self, chat_id: int) -> Iterator[Tuple[str, Sequence[str], Sequence[HashMessage]]]:
        """The digest

        Returns:
            A generator over the digest giving tuples as ``(tag, forms, messages)``
        """
        for tag in self.db.get_chat_tags(chat_id):
            yield tag.id, tuple(tag.forms), tuple(tag.messages)
