from dataclasses import dataclass
from inspect import signature
from unittest.mock import MagicMock

import pytest

from remapper import remap
from remapper.remap import _get_specifiable_attributes


@dataclass
class Source:
    a: int
    b: int
    c: int


@dataclass
class Destination:
    a: int
    b: int


@dataclass
class UnderdefinedDestination:
    a: int
    d: int  # not on the source


@dataclass
class OptionalDestination:
    a: int
    d: int = 2


@dataclass
class ComplexSource:
    obj: Source


@dataclass
class ComplexDestination:
    obj: Destination


def test_get_attributes(monkeypatch):
    """
    Check that the expected attributes for a given class are properly extracted, and
    that the signature inspection is cached.
    """
    mock: MagicMock = MagicMock(side_effect=signature)
    monkeypatch.setattr("inspect.signature", mock)
    assert _get_specifiable_attributes(OptionalDestination) == {"a": False, "d": True}
    assert _get_specifiable_attributes(OptionalDestination) == {"a": False, "d": True}
    mock.assert_called_once_with(OptionalDestination.__init__)


def test_remap():
    """
    Check that the source type can be converted into the destination type.
    """
    source: Source = Source(a=0, b=1, c=2)
    destination: Destination = remap(source, Destination)
    assert isinstance(destination, Destination)
    assert destination.a == 0
    assert destination.b == 1


def test_remap_impossible():
    """
    Check that if the source type cannot provide an attribute the destination requires,
    an error is raised.
    """
    source: Source = Source(a=0, b=1, c=2)

    with pytest.raises(
        TypeError, match=r".*cannot provide values for the required arguments {'d'}.*"
    ):
        remap(source, UnderdefinedDestination)


def test_remap_override():
    """
    Check that the source type can be converted into a mismatching destination type
    through a supplied override.
    """
    source: Source = Source(a=0, b=1, c=2)

    # its not possible
    with pytest.raises(
        TypeError, match=r".*cannot provide values for the required arguments {'d'}.*"
    ):
        remap(source, UnderdefinedDestination)

    # but now it is
    destination: UnderdefinedDestination = remap(
        source, UnderdefinedDestination, overrides={"d": source.c}
    )
    assert isinstance(destination, UnderdefinedDestination)
    assert destination.a == 0
    assert destination.d == 2


def test_remap_optional():
    """
    Check that a source can be converted to a destination to which it cannot provide all
    arguments if the missing arguments have defaults on the destination.
    """
    source: Source = Source(a=0, b=1, c=2)

    # arguments missing on the source can be supplied by their default on the dest
    destination: OptionalDestination = remap(source, OptionalDestination)
    assert isinstance(destination, OptionalDestination)
    assert destination.a == 0
    assert destination.d == 2


def test_remap_nested():
    """
    Check that a source with a certain attribute can be converted to a destination with
    with a similar attribute of a different type.
    """
    source: ComplexSource = ComplexSource(obj=Source(a=0, b=1, c=2))

    # arguments missing on the source can be supplied by their default on the dest
    destination: ComplexDestination = remap(
        source, ComplexDestination, nested_types={"obj": Destination}
    )
    assert isinstance(destination, ComplexDestination)
    assert destination.obj == Destination(a=0, b=1)
