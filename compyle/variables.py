from typing import Mapping, Set, Type
from functools import singledispatch

import attr

from .transpyle import Expression, Identifier, Names, T, Transpylation, CompylationError


#: set of all Expression types that are primitive values
VALUE_TYPES: Set[Type[Expression]] = set()


@singledispatch
def value_expression(value: T) -> Expression[T]:
    """Given some value, convert it back to an expression producing this value"""
    raise CompylationError(f"no expression conversion for {value_expression!r}")


@attr.s(frozen=True, auto_attribs=True)
class Reference(Expression[T]):
    """A reference to some variable"""

    identifier: Identifier

    @property
    def names(self) -> Names:
        return Names(free={self.identifier})

    def specialize(self, namespace: Mapping[Identifier, Expression]):
        try:
            replacement = namespace[self.identifier]
        except KeyError:
            return self
        return replacement.specialize(namespace)

    def transpyle(self):
        return Transpylation(
            self, f"__namespace__[{self.identifier!r}].evaluate(__namespace__)"
        )
