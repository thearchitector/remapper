# remap

![GitHub Workflow Status](https://raster.shields.io/github/actions/workflow/status/thearchitector/remap/test.yaml?label=tests&style=flat-square)
![PyPI - Downloads](https://raster.shields.io/pypi/dm/remap?style=flat-square)
![GitHub](https://raster.shields.io/github/license/thearchitector/remap?style=flat-square)

Transform objects to and from similar structural mappings. Useful for translating between sources of truth and presentational models of data.

Supports Python 3.8+. No dependencies.

## Installation

```sh
$ pdm add remap
# or
$ python -m pip install --user remap
```

## Usage

A trivial example for `remap` is converting one dataclass into another without having to manually pass attributes:

```python
from dataclasses import dataclass

from remap import remap

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


dest = remap(Source(1, 2, 3), Destination)
>> Destination(1, 2, 3)
```

A more useful example would be a mapping between a database model and a dataclass:

## License

This software is licensed under the [BSD 3-Clause License](LICENSE).
