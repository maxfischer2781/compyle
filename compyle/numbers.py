from typing import Mapping, Any
from fractions import Fraction as PyFraction

import attr

from .transpyle import Expression, Names, Transpylation, E, T, Identifier
from .variables import value_expression, VALUE_TYPES


class PyInteger(int):
    def __truediv__(self, other):
        if isinstance(other, PyInteger):
            return PyFraction(int(self), int(other))
        return NotImplemented


@attr.s(frozen=True, auto_attribs=True)
class Integer(Expression[PyInteger]):
    value: int
    names = Names(bound={"__PyInteger__": PyInteger})

    def specialize(self, namespace: Mapping[Identifier, Any]):
        return self

    def transpyle(self):
        return Transpylation(self, f"__PyInteger__({self.value})")

    def evaluate(self, namespace: Mapping[Identifier, Any]) -> int:
        return PyInteger(self.value)


VALUE_TYPES.add(Integer)


@value_expression.register(int)
def int_expression(value: int):
    return Integer(value)


@attr.s(frozen=True, auto_attribs=True)
class Fraction(Expression[PyFraction]):
    numerator: int
    denominator: int
    names = Names(bound={"__PyFraction__": PyFraction})

    def specialize(self, namespace: Mapping[Identifier, Any]):
        return self

    def transpyle(self):
        return Transpylation(
            self, f"__PyFraction__({self.numerator}, {self.denominator})"
        )

    def evaluate(self, namespace: Mapping[Identifier, Any]):
        return PyFraction(self.numerator, self.denominator)


VALUE_TYPES.add(Fraction)


@value_expression.register(PyFraction)
def fraction_expression(value: PyFraction):
    return Fraction(numerator=value.numerator, denominator=value.denominator)
