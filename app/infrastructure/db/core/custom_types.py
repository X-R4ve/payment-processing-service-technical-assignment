from enum import Enum

from sqlalchemy import TypeDecorator, String


class EnumString(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_cls: type[Enum], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_cls = enum_cls

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enum_cls(value)

    def __repr__(self):
        return f"{type(self).__name__}({self._enum_cls.__name__})"

    def copy(self, *args, **kwargs):
        return type(self)(self._enum_cls, *args, **kwargs)