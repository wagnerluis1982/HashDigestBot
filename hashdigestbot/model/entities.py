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

    id = PrimaryKey(Integer)
    friendly_name = Required(String)
    username = Required(String)

    def __repr__(self):
        return "HashUser(%s)" % self.friendly_name


class HashMessage(Base):
    __tablename__ = 'messages'

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
