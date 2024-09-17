from dataclasses import dataclass, asdict
from typing import Self

import construct


class _Annotations(dict):
    """A mapping that is __annotations__ in the body of a Pynary class."""

    def __init__(self, body: "_Body"):
        super().__init__()
        self.__body = body

    def __setitem__(self, key, value):
        super().__setitem__(key, value)


class _Body(dict):
    """A mapping in which the body of a Pynary class is evaluted."""

    def __init__(self):
        super().__init__()
        self["__annotations__"] = _Annotations(self)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            if key in self["__annotations__"]:
                return construct.this[key]
            raise


class Meta(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return _Body()

    def __new__(cls, name, bases, namespace, **kwds):
        c = super().__new__(cls, name, bases, namespace, **kwds)
        c._struct = construct.Struct(
            *(name / ty for name, ty in c.__annotations__.items())
        )
        return dataclass(c, kw_only=True)


class Base(metaclass=Meta):
    @classmethod
    def parse(cls, stream) -> Self:
        parsed = cls._struct.parse_stream(stream)
        return cls(**{k: v for k, v in parsed.items() if not k[0] == "_"})

    def __buffer__(self, flags: int) -> memoryview:
        return memoryview(self._struct.build(asdict(self)))


u32 = construct.Int32ul
u64 = construct.Int64ul


def nbytes(length):
    return construct.PaddedString(length, "utf8")
