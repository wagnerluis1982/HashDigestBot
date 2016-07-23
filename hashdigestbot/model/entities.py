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
    forms = Required(ShallowSet)

    messages = relationship("HashMessage", back_populates="tag")

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

    tag_id = Required(ForeignKey(HashTag.id))
    tag = relationship(HashTag, back_populates="messages")

    def __repr__(self):
        return "HashMessage(%d)" % self.id
