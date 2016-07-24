from typing import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .entities import Base, HashTag, HashMessage, HashUser


class Database:
    def __init__(self):
        self.session = None

    def connect(self, engine):
        if self.session:
            raise RuntimeError("Database already connected")
        self.session = sessionmaker(bind=engine)(autocommit=True)

    def is_connected(self):
        return bool(self.session)

    def get_message_tag(self, message_id: int) -> HashTag:
        """Tag related to a message"""
        tag = self.session.query(HashTag).\
            join(HashMessage).\
            filter_by(id=message_id).one()
        return tag

    def get_messages_by_tag(self, tag_id: str) -> Iterable[HashMessage]:
        """Sequence of messages related to a tag"""
        messages = self.session.query(HashMessage).\
            filter_by(tag_id=tag_id)
        return messages

    def get_tags_by_chat(self, chat_id) -> Iterable[HashTag]:
        tags = self.session.query(HashTag).\
            join(HashMessage).\
            filter_by(chat_id=chat_id)
        return tags

    def insert(self, instance):
        self.session.add(instance)

    def get(self, entity, **kwargs):
        q = self.session.query(entity).filter_by(**kwargs)
        return q.scalar()

    def exists(self, entity, **kwargs):
        q = self.session.query(entity).filter_by(**kwargs)
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
        db.connect(engine)
    return db
