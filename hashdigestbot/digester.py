import re
from typing import Sequence, FrozenSet

HASHTAG_RE = re.compile(
    r"(?:^|\W+)"    # Ignore begin or non-words before '#'.
    r"#+(\w+"       # Match the hashtag,
    r"(?!#+.*))\b"  # but don't match if we have #two#tags
)


def hashtags(text: str) -> FrozenSet[str]:
    return frozenset(HASHTAG_RE.findall(text))


class HashMessage:
    def __init__(self, id: int, text: str, reply_to: int = None):
        self.id = id
        self.text = text
        self.reply_to = reply_to


class Digester:
    def __init__(self):
        # Dict[str, Tuple[Set[str], List[HashMessage]]]
        self._subjects = {}

    def feed(self, message: HashMessage) -> bool:
        """Give a message to process tags

        The message will be added to the digest if has tags or is a reply to a
        previous message with tags.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        tags = hashtags(message.text)
        for tag in tags:
            key = tag.lower()
            if key not in self._subjects:
                self._subjects[key] = ({tag}, [message])
            else:
                subject = self._subjects[key]
                subject[0].add(tag)
                subject[1].append(message)

        return bool(tags)

    def get_messages(self, tag: str) -> Sequence[HashMessage]:
        """Sequence of messages related to this tag"""
        key = tag.lower()
        subject = self._subjects.get(key)
        if subject:
            return tuple(subject[1])

        return ()
