# remapper

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/thearchitector/remapper/test.yaml?label=tests&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/remapper?style=flat-square)
![GitHub](https://img.shields.io/github/license/thearchitector/remapper?style=flat-square)

Transform objects to and from similar structural mappings. Useful for translating between sources of truth and presentational models of data.

Supports Python 3.8+. No dependencies.

## Installation

```sh
$ pdm add remapper
# or
$ python -m pip install --user remapper
```

## Usage

> The examples below use dataclasses because they're easy, but `remap` works with any destination type that exposes attributes via its `__init__`.

A trivial example for `remap` is converting one dataclass into another without having to manually pass attributes:

```python
from dataclasses import dataclass

from remapper import remap


@dataclass
class Source:
    a: int
    b: int
    c: int


@dataclass
class Destination:
    a: int
    b: int
    c: int


dest = remap(Source(a=1, b=2, c=3), Destination)
# >> Destination(a=1, b=2, c=3)
```

A more useful example would be in mapping an internal database model to an externally-facing dataclass:

```python
from dataclasses import dataclass

from remapper import remap
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class Source(Base):
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    a: Mapped[int]
    b: Mapped[int]
    c: Mapped[int]


@dataclass
class Destination:
    a: int
    b: int
    c: int

    @property
    def d(self) -> int:
        return self.a + self.b + self.c


source = Source(a=1, b=2, c=3)
await session.commit(source)

dest = remap(source, Destination)
dest.d
# >> 6
```

### Overrides

There's a non-zero chance that a destination may require more data than available on a source. In those cases, you can manually provide values via the `overrides` keyword argument. Values in `overrides` will take precedence over values on the source:

```python
from dataclasses import dataclass

from remapper import remap


@dataclass
class Source:
    a: int
    b: int


@dataclass
class Destination:
    a: int
    b: int
    c: int


dest = remap(Source(a=1, b=2), Destination, overrides={"b": 0, "c": 3})
# >> Destination(a=1, b=0, c=3)
```

### Defaults

If a destination defines more attributes than available on a source, but the destination has default values for those additional attributes, you don't need to supply overrides:

```python
from dataclasses import dataclass

from remapper import remap


@dataclass
class Source:
    a: int
    b: int


@dataclass
class Destination:
    a: int
    b: int
    c: int = 3


dest = remap(Source(a=1, b=2), Destination)
# >> Destination(a=1, b=2, c=3)
```

### Nested Types

Some complex sources may have attributes that themselves need to be converted. Rather than remapping in several steps, you can use the `nested_types` keyword argument to specify inner types of the destination attributes:

```python
from dataclasses import dataclass

from remapper import remap


@dataclass
class Source:
    b: int


@dataclass
class Destination:
    b: int


@dataclass
class ParentSource:
    a: int
    child: Source


@dataclass
class ParentDestination:
    a: int
    child: Destination


## this works but is kind of clunky
source = ParentSource(a=1, child=Source(b=1))
dest_child = remap(source.child, Destination)
dest = remap(source, ParentDestination, overrides={"child": dest_child})
# >> ParentDestination(a=1,child=Destination(b=1))

## so use this instead
dest = remap(
    ParentSource(a=1, child=Source(b=1)),
    ParentDestination,
    nested_types={"child": Destination},
)
# >> ParentDestination(a=1,child=Destination(b=1))
```

## License

This software is licensed under the [BSD 3-Clause Clear License](LICENSE).
