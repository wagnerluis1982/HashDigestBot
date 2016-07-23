import re
from typing import Iterator, Union

import telegram

from .model.database import connect, HashMessage, HashTag

HASHTAG_RE = re.compile(
    r"(?:^|\W+)"    # Ignore begin or non-words before '#'.
    r"#+(\w+"       # Match the hashtag,
    r"(?!#+.*))\b"  # but don't match if we have #two#tags
)


def extract_hashtag(text: str) -> str:
    search = HASHTAG_RE.search(text)
    return search.group(1) if search else None


class Digester:
    def __init__(self):
        self.db = connect("sqlite:///")

    def feed(self, message: Union[HashMessage, telegram.Message]) -> bool:
        """Give a message to search for a tag

        The message will be added to the digest if has a tag or is a reply to a
        previous message with tag.

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
        # Extract tag from the message
        tag = extract_hashtag(message.text)
        # A tag was found in the message? So, mark them and return.
        if tag:
            self.db.add_message(message, tag)
            return True
        # Otherwise, check if message is a reply to a previous tagged message.
        # In that case, we mark them, but asking for don't register variations.
        elif message.reply_to:
            tag_obj = self.db.get_tag(message.reply_to)
            if tag_obj:
                self.db.add_message(message, tag_obj)
                return True
        return False

    def digest(self, chat_id: int) -> Iterator[HashTag]:
        """The digest

        Returns:
            A generator over the digest giving tuples as ``(tag, forms, messages)``
        """
        for tag in self.db.get_chat_tags(chat_id):
            yield tag
