# remapper

![GitHub Workflow Status](https://raster.shields.io/github/actions/workflow/status/thearchitector/remapper/test.yaml?label=tests&style=flat-square)
![PyPI - Downloads](https://raster.shields.io/pypi/dm/remapper?style=flat-square)
![GitHub](https://raster.shields.io/github/license/thearchitector/remapper?style=flat-square)

Transform objects to and from similar structural mappings. Useful for translating between sources of truth and presentational models of data.

Supports Python 3.8+. No dependencies.

## Installation

```sh
$ pdm add remapper
# or
$ python -m pip install --user remapper
```

## Usage

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

A more useful example would be a mapping an internal database model to an externally-facing dataclass:

```python
from dataclasses import dataclass

from remapper import remap
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass

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

source = Source(a=1, b=2, c=3)
await session.commit(source)

dest = remap(source, Destination)
# >> Destination(a=1, b=2, c=3)
```

## License

This software is licensed under the [BSD 3-Clause Clear License](LICENSE).
