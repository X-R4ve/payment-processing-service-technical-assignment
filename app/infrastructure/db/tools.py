from enum import Enum


def get_enum_values_string(enum: type[Enum]) -> str:
    return ','.join(repr(e.value) for e in enum)
