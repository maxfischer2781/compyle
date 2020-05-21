from typing import Mapping, Any

import attr

from .transpyle import CompoundExpression, Transpylation, Identifier
from .variables import value_expression, VALUE_TYPES


@attr.s(frozen=True, auto_attribs=True)
class OperatorBinary(CompoundExpression):
    symbol: str

    def specialize(self, namespace: Mapping[Identifier, Any]):
        lhs, rhs = (child.specialize(namespace) for child in self.children)
        specialization = OperatorBinary(children=(lhs, rhs), symbol=self.symbol)
        if type(lhs) in VALUE_TYPES and type(rhs) in VALUE_TYPES:
            return value_expression(specialization.evaluate(namespace))
        return specialization

    def transpyle(self):
        lhs, rhs = self.children
        return Transpylation(
            self, f"{lhs.transpyle().source} {self.symbol} {rhs.transpyle().source}"
        )
