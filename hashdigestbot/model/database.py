from typing import Sequence, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .entities import Base, HashTag, HashMessage


class Database:
    def __init__(self):
        self.session = None

    def bind(self, engine):
        if self.session:
            raise RuntimeError("Database already connected")
        self.session = sessionmaker(bind=engine)(autocommit=True)

    def is_connected(self):
        return bool(self.session)

    def add_message(self, message: HashMessage, tag_or_name: Union[str, HashTag]):
        session = self.session
        with session.begin():
            if isinstance(tag_or_name, str):
                # Add a tag entry if necessary
                tag_id = self.generate_tag_id(tag_or_name)
                q = session.query(HashTag).filter_by(id=tag_id)
                if not self._exists(q):
                    tag = HashTag(id=tag_id, shapes={tag_or_name})
                # Or fetch tag and add a possible new shape
                else:
                    tag = q.one()
                    tag.shapes.add(tag_or_name)

            # When we have a HashTag instance, means it came from database.
            # Only alias is made. No tag shapes is added here.
            else:
                tag = tag_or_name

            # Add the message associated to the tag
            message.tag = tag
            session.add(message)

    def get_tag(self, message_id: int) -> HashTag:
        """Tag related to a message"""
        tag = self.session.query(HashTag).\
            join(HashMessage).\
            filter_by(id=message_id).one()
        return tag

    def get_messages(self, tag_id: str) -> Sequence[HashMessage]:
        """Sequence of messages related to a tag"""
        messages = self.session.query(HashMessage).\
            filter_by(tag_id=tag_id)
        return tuple(messages)

    def get_chat_tags(self, chat_id):
        tags = self.session.query(HashTag).\
            join(HashMessage).\
            filter_by(chat_id=chat_id)
        return tags

    def _exists(self, q):
        return self.session.query(q.exists()).scalar()

    @staticmethod
    def generate_tag_id(tag: str) -> str:
        """Generate a key for a tag"""
        return tag.lower()

    def __del__(self):
        self.session.close()


db = Database()


def connect(url: str, debug: bool = False) -> Database:
    if not db.is_connected():
        engine = create_engine(url, echo=debug)
        Base.metadata.bind = engine
        Base.metadata.create_all()
        db.bind(engine)
    return db
