from functools import partial

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .customtypes import ShallowSet

# Interesting aliases
PrimaryKey = partial(Column, primary_key=True)
Required = partial(Column, nullable=False)
Optional = Column

# ORM base class
Base = declarative_base()


class HashTag(Base):
    __tablename__ = 'tags'

    id = PrimaryKey(String)
    shapes = Required(ShallowSet)

    messages = relationship("HashMessage", back_populates="tag")

    def __repr__(self):
        return "HashTag(%s)" % self.id


class HashUser(Base):
    __tablename__ = 'users'

    def __init__(self, id, friendly_name, username):
        self.id = id
        self.friendly_name = friendly_name
        self.username = username

    id = PrimaryKey(Integer)
    friendly_name = Required(String)
    username = Required(String)

    def __repr__(self):
        return "HashUser(%s)" % self.friendly_name


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

    # foreign keys
    tag_id = Required(ForeignKey(HashTag.id))
    user_id = Required(ForeignKey(HashUser.id))
    # relationships
    tag = relationship(HashTag, back_populates="messages")
    user = relationship(HashUser)

    def __repr__(self):
        return "HashMessage(%d)" % self.id
