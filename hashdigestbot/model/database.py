from functools import partial
from typing import Iterable, Sequence

from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from .customtypes import ShallowSet

# Interesting aliases
PrimaryKey = partial(Column, primary_key=True)
Required = partial(Column, nullable=False)
Optional = Column

# ORM base class
Base = declarative_base()


tags2messages = \
    Table('tags_messages', Base.metadata,
          Column('tag_id', ForeignKey('tags.id'), primary_key=True),
          Column('message_id', ForeignKey('messages.id'), primary_key=True))


class HashTag(Base):
    __tablename__ = 'tags'

    id = PrimaryKey(String)
    forms = Required(ShallowSet)

    messages = relationship("HashMessage", secondary=tags2messages,
                            back_populates="tags")

    def __repr__(self):
        return "HashTag(%s)" % self.id


class HashMessage(Base):
    __tablename__ = 'messages'

    def __init__(self, id: int, text: str, chat_id: int, reply_to: int = None):
        self.id = id
        self.text = text
        self.chat_id = chat_id
        self.reply_to = reply_to

    id = PrimaryKey(Integer)
    text = Required(String)
    chat_id = Required(Integer)
    reply_to = Optional(Integer)

    tags = relationship("HashTag", secondary=tags2messages,
                        back_populates="messages")

    def __repr__(self):
        return "HashMessage(%d)" % self.id


class Database:
    def __init__(self):
        self.session = None

    def bind(self, engine):
        if self.session:
            raise RuntimeError("Database already connected")
        self.session = sessionmaker(bind=engine)(autocommit=True)

    def is_connected(self):
        return bool(self.session)

    def add_message(self, message: HashMessage, tag_names: Iterable[str], is_variations=True):
        session = self.session
        with session.begin():
            # Associate all the tags to the new message
            session.add(message)
            for name in tag_names:
                # Add a tag entry if necessary
                tag_id = self.generate_tag_id(name)
                q = session.query(HashTag).filter_by(id=tag_id)
                if not self._exists(q):
                    tag = HashTag(id=tag_id, forms=set(tag_names))
                else:
                    tag = q.one()

                # The tags passed may not be the ones extracted, but got from get_tags() method.
                # In that case the tags could not be a real variation...
                if is_variations:
                    tag.forms = tag.forms.union(tag_names)

                # Associate the message to this tag
                message.tags.append(tag)

    def get_tags(self, message_id: int = None) -> Sequence[str]:
        """Sequence of tags related to a message"""
        message = self.session.query(HashMessage).filter_by(id=message_id).one()
        return tuple(t.id for t in message.tags)

    def get_messages(self, tag_id: str) -> Sequence[HashMessage]:
        """Sequence of messages related to a tag"""
        tag = self.session.query(HashTag).filter_by(id=tag_id).one()
        return tuple(tag.messages)

    def get_chat_tags(self, chat_id):
        return self.session.query(HashTag).\
            filter(HashTag.messages.any(HashMessage.chat_id == chat_id))

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