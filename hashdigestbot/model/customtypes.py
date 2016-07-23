import json
import typing

from sqlalchemy import TypeDecorator, String
from sqlalchemy.ext.mutable import MutableSet


class ShallowSet(TypeDecorator):
    impl = String

    @property
    def python_type(self):
        return set

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(sorted(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return set(value)


MutableSet.associate_with(ShallowSet)
