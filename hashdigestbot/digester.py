import re
from typing import Iterator

import telegram

from .model.database import connect
from .model.entities import HashTag, HashMessage, HashUser

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

    def feed(self, message: telegram.Message) -> bool:
        """Give a telegram message to search for a tag

        The message will be added to the digest if has a tag or is a reply to a
        previous message with tag.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        # Extract tag from the message
        tag = extract_hashtag(message.text)

        # Check early if the message has a tag or can be a reply to a tagged message
        if not (tag or message.reply_to_message):
            return False

        # Create a HashMessage from the telegram message
        reply_id = message.reply_to_message.message_id if message.reply_to_message else None
        hashmessage = HashMessage(
            id=message.message_id,
            text=message.text,
            chat_id=message.chat_id,
            reply_to=reply_id,
        )

        # Associate the hashmessage to the user who sent the message
        hashuser = self.db.get_user(message.from_user.id)
        if not hashuser:
            hashuser = HashUser(
                id=message.from_user.id,
                friendly_name=self.make_friendly_name(message.from_user),
                username=message.from_user.username,
            )
        hashmessage.user = hashuser

        # A tag was found in the message? So add it and return.
        if tag:
            self.db.add_message(hashmessage, tag)
            return True
        # Otherwise, the message may be a reply to a previous tagged message.
        else:
            tag_obj = self.db.get_tag(hashmessage.reply_to)
            if tag_obj:
                self.db.add_message(hashmessage, tag_obj)
                return True
        return False

    def digest(self, chat_id: int) -> Iterator[HashTag]:
        """The digest

        Returns:
            A generator over the digest giving ``HashTag`` objects``
        """
        yield from self.db.get_chat_tags(chat_id)

    @staticmethod
    def make_friendly_name(user):
        if user.last_name:
            return '%s %s' % (user.first_name, user.last_name)
        return user.first_name
