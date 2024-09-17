from dataclasses import dataclass, asdict
from typing import Self

import construct


class _Body(dict):
    """
    A mapping in which the body of a Pynary class is evaluated.

    Compared to a normal class being evaluated with locals() set to a
    normal dict, fields that received a type annotation but no actual
    assignment can be referenced, and they're passed to construct's
    "this" feature. Consider the example in Construct's docs:

        from construct import Struct, Int8ub, Array, this

        image = Struct(
            "width" / Int8ub,
            "height" / Int8ub,
            "pixels" / Array(this.width * this.height, Byte),
        )

    We would like to write it as:

        class Image(Base):
            width: Int8ub
            height: Int8ub
            pixels: Array(width * height, Byte)

    but we need "width" and "height" to be usable in the annotation.
    """

    def __init__(self):
        super().__init__()
        self["__annotations__"] = {}

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            if key in self["__annotations__"]:
                return construct.this[key]
            raise


class Meta(type):
    """
    The metaclass of Pynary classes.

    You probably want to use Base instead of using this directly.
    """

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
    """
    The base class of Pynary classes.

    This implicitly makes the class a dataclass.
    """

    @classmethod
    def parse(cls, stream: io.RawIOBase | io.BufferedIOBase) -> Self:
        """Construct a new object by reading from a stream."""
        parsed = cls._struct.parse_stream(stream)
        return cls(**{k: v for k, v in parsed.items() if not k[0] == "_"})

    def __buffer__(self, flags: int) -> memoryview:
        """
        Serialize the object as a read-only memoryview.

        This method implements the buffer protocol, allowing writing to
        a stream with by calling the .write() method on an object
        directly.
        """
        return memoryview(self._struct.build(asdict(self)))


u32 = construct.Int32ul
u64 = construct.Int64ul


def nbytes(length):
    return construct.PaddedString(length, "utf8")
