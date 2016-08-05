import re
from datetime import timedelta
from functools import partial

from sqlalchemy import Column, ForeignKey,\
    SmallInteger, Integer, String, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

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

    id = PrimaryKey(Integer)
    friendly_name = Required(String)
    username = Required(String)

    def __repr__(self):
        return "HashUser(%s)" % self.friendly_name


class HashMessage(Base):
    __tablename__ = 'messages'

    id = PrimaryKey(Integer)
    date = Required(DateTime)
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


# Useful regex patterns
RE_EMAIL = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class ConfigChat(Base):
    __tablename__ = 'config_chats'

    chat_id = PrimaryKey(Integer)
    name = Required(String)
    sendto = Required(String)
    interval = Optional(Interval, default=timedelta(days=1))
    messages = Optional(SmallInteger, default=30)

    @validates('sendto')
    def validate_sendto(self, key, address):
        assert RE_EMAIL.match(address)
        return address

    def __repr__(self):
        return "AllowedChat(%d, %s)" % (self.chat_id, self.name)
