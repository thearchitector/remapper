import inspect
from functools import lru_cache
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, Set, Type, TypeVar

    T = TypeVar("T", bound=object)
    N = TypeVar("N", bound=object)


_UNSET: object = object()


def _get_available_attributes(source: object) -> Mapping[str, "Any"]:
    """
    Returns all the available attributes of the given source, excluding those that are
    private or dunders.
    """
    return {
        attr: value
        for attr in dir(source)
        if attr[0] != "_"
        and (value := getattr(source, attr, _UNSET)) is not _UNSET
        and not inspect.ismethod(value)
    }


@lru_cache(maxsize=None)
def _get_specifiable_attributes(cls: "Type[T]") -> "Dict[str, bool]":
    """
    Returns all the specifiable attributes (passable through `__init__`) of the given
    class. Each attribute is mapped to a boolean indicating if it is optional;
    Optionality means the attribute has a default value.
    """
    init = cls.__init__
    init_signature = inspect.signature(init)
    parameters = init_signature.parameters.values()
    return {
        param.name: param.default is not param.empty
        for param in parameters
        if param.name != "self"
    }


def remap(
    source: "Any",
    dest_type: "Type[T]",
    nested_types: "Dict[str, Type[N]]" = {},  # noqa: B006
    overrides: Mapping[str, "Any"] = {},  # noqa: B006
) -> "T":
    """
    Instantiates the destination type, providing all the arguments available to it from
    the attributes of the source. The attributes required by the destination type MUST
    be a subset of those accessible on the source; attributes on the destination that
    have default values are thus not required to exist on the source.

    If provided, the overrides can be used to remap source attributes into attributes
    expected by the destination, or supply missing values altogether.

    If nested types are provided, attributes on the source matching those types are recursively remapped to the provided destinations.
    """
    readable_attrs: Mapping[str, "Any"] = {
        **(
            source if isinstance(source, Mapping) else _get_available_attributes(source)
        ),
        **overrides,
    }
    writable_attrs: "Dict[str, bool]" = _get_specifiable_attributes(dest_type)  # type: ignore[arg-type]

    # all the attributes required by the destination that don't have default values
    # and are not available on the source
    unsupplied_required_attrs: "Set[str]" = {
        wa for wa, optional in writable_attrs.items() if not optional
    } - readable_attrs.keys()
    if unsupplied_required_attrs:
        raise TypeError(
            f"The source {source.__class__.__name__} cannot provide values for the"
            f" required arguments {unsupplied_required_attrs} of destination type"
            f" {dest_type.__name__}!"
        )

    return dest_type(
        **{
            attr: (
                remap(readable_attrs[attr], nested_type)
                if (nested_type := nested_types.get(attr, None))
                else readable_attrs[attr]
            )
            for attr in writable_attrs
            # since we've already checked for unsupplied required attributes, we know
            # at this stage any absent readables in the set of writeables are optional.
            if attr in readable_attrs
        }
    )
