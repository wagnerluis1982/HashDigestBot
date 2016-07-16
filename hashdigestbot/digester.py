import re
from typing import cast, Sequence, Iterable, Tuple, List, Set, FrozenSet, Dict, Iterator

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
        # The following is a dict to store the relation of tag to messages mapped as
        #   tag -> (forms, messages)
        # where
        # - tag: unique form of the tag name
        # - forms: are variations of a tag, e.g. #lovepython and #LovePython
        # - messages: list of HashMessage objects associated to the tag
        self._tag2msgs = cast(Dict[str, Tuple[Set[str], List[HashMessage]]], {})

        # Here we have the back references, i.e message to tags, that is a dict mapped as
        #   msg_id -> [tag, ...]
        # where
        # - msg_id: is the unique id of the message.
        self._msg2tags = cast(Dict[int, Set[str]], {})

    def feed(self, message: HashMessage) -> bool:
        """Give a message to process tags

        The message will be added to the digest if has tags or is a reply to a
        previous message with tags.

        Returns:
            bool: Indicate if the message was added to the digest
        """
        # Extract tags from the message
        tags = hashtags(message.text)
        is_variations = bool(tags)
        # If no tags found, check if message is a reply to a previous tagged message
        if not tags and message.reply_to:
            tags = self.get_tags(message)
        # Verify if I have tags and mark the message
        if tags:
            self._mark(message, tags, is_variations)
            return True
        return False

    def _mark(self, message: HashMessage, tags: Iterable[str], is_variations=True):
        # get the association of this message to tags for later use
        backref = self._msg2tags[message.id] = set()

        for tag in tags:
            key = self.generate_key(tag)
            if key not in self._tag2msgs:
                self._tag2msgs[key] = (set(), list())

            # associate the message to this tag
            forms, messages = self._tag2msgs[key]
            if is_variations:   # The tags passed may not be the ones extracted, but got from get_tags() method.
                forms.add(tag)  # In that case the tags could not be a real variation.
            messages.append(message)

            # associate this tag to the message
            backref.add(key)

    def digest(self) -> Iterator[Tuple[str, Sequence[str], Sequence[HashMessage]]]:
        """The digest

        Returns:
            A generator over the digest giving tuples as ``(tag, forms, messages)``
        """
        for tag, (forms, messages) in self._tag2msgs.items():
            yield tag, tuple(forms), tuple(messages)

    def get_tags(self, message: HashMessage) -> Sequence[str]:
        """Sequence of tags related to a message"""
        if message.reply_to in self._msg2tags:
            return tuple(self._msg2tags[message.reply_to])
        return ()

    def get_messages(self, tag: str) -> Sequence[HashMessage]:
        """Sequence of messages related to a tag"""
        key = self.generate_key(tag)
        taggish = self._tag2msgs.get(key)
        if taggish:
            return tuple(taggish[1])
        return ()

    @staticmethod
    def generate_key(tag: str) -> str:
        """Generate a key for a tag"""
        return tag.lower()
