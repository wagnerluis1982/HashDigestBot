import json
import typing

from sqlalchemy import TypeDecorator, String


class SetType(TypeDecorator):
    impl = String

    @property
    def python_type(self):
        return frozenset

    def process_bind_param(self, value, dialect):
        assert isinstance(value, typing.AbstractSet)
        if value is not None:
            value = json.dumps(sorted(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return frozenset(value)
