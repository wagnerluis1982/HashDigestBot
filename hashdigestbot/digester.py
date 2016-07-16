import re
from typing import cast, Sequence, Tuple, List, Set, FrozenSet, Dict

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


class TagMarker:
    def __init__(self):
        # The following is a dict mapped as
        #   tag -> (forms, messages)
        # where
        # - tag: unique form of the tag name
        # - forms: are variations of a tag, e.g. #lovepython and #LovePython
        # - messages: list of HashMessage objects associated to the tag
        self._tag2msgs = cast(Dict[str, Tuple[Set[str], List[HashMessage]]], {})

        # Here we have the back references, that is a dict mapped as
        #   msg_id -> [tag, ...]
        # where
        # - msg_id: is the unique id of the message.
        self._msg2tags = cast(Dict[int, Set[str]], {})

    def mark(self, message, tags):
        # get the association of this message to tags for later use
        backref = self._msg2tags[message.id] = set()

        for tag in tags:
            # generate a key for this tag
            key = tag.lower()
            # associate the message to this tag
            if key not in self._tag2msgs:
                self._tag2msgs[key] = ({tag}, [message])
            else:
                forms, messages = self._tag2msgs[key]
                forms.add(tag)
                messages.append(message)
            # associate this tag to the message
            backref.add(key)

    def get_messages(self, tag):
        key = tag.lower()
        subject = self._tag2msgs.get(key)
        if subject:
            return tuple(subject[1])
        return ()


class Digester:
    def __init__(self):
        self._marker = TagMarker()

    def feed(self, message: HashMessage) -> bool:
        """Give a message to process tags

        The message will be added to the digest if has tags or is a reply to a
        previous message with tags.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        tags = hashtags(message.text)
        self._marker.mark(message, tags)
        return bool(tags)

    def get_messages(self, tag: str) -> Sequence[HashMessage]:
        """Sequence of messages related to this tag"""
        return self._marker.get_messages(tag)
