pynary
===

An experimental library for serializing and deserializing binary
structures expressed in the style of dataclasses, that is, using type
annotations.

This is essentially a frontend over
[Construct](https://construct.readthedocs.io/en/latest/intro.html) for
the actual parsing and serialization; types can be any Construct type.

See the test case for an example.

Running tests
---

`uv run python -m unittest discover -s tests`
