import io
import unittest

from pynary import *


class MyStructure(Base):
    magic: u32 = 0x11223344
    version: u32
    name: nbytes(32)
    length: u32
    items: nbytes(length)


class PynaryTests(unittest.TestCase):
    def test_basic(self):
        buf = io.BytesIO()
        oldstruct = MyStructure(version=1, name="hello", length=3, items="xyz")
        buf.write(oldstruct)
        buf.seek(0)
        newstruct = MyStructure.parse(buf)
        self.assertEqual(oldstruct, newstruct)
        self.assertEqual(buf.read(), b"")
