"""
b := a + 2
a := 30 + 10

>> b + a
"""
from typing import Callable, Optional
from functools import singledispatch

import pyparsing as pp

from .variables import Reference
from .transpyle import Expression
from .numbers import Integer, Fraction
from .operators import OperatorBinary
from .interpret import Evaluate, Assign


@singledispatch
def unparse(what):
    return repr(what)


def rule(syntax: pp.ParserElement, name: Optional[str] = None):
    def bind_rule(
        transformation: Callable[[pp.ParseResults], Expression]
    ) -> pp.ParserElement:
        """Bind a ``transformation`` to the ``syntax`` rule"""
        syntax.setName(name if name is not None else transformation.__name__.upper())
        syntax.setParseAction(transformation)
        return syntax

    return bind_rule


IDENTIFIER = pp.Word(pp.alphas, pp.alphas + "_")


@rule(IDENTIFIER.copy())
def reference(result: pp.ParseResults):
    """A named reference, such as ``Kevin``"""
    return Reference(result[0])


@unparse.register
def unparse_reference(what: Reference):
    return what.identifier


@rule(pp.Word(pp.nums) + pp.Suppress(":") - pp.Word(pp.nums).setName('integer'))
def fraction(result: pp.ParseResults):
    """A Fraction literal, such as ``37 : 13``"""
    numerator, denominator = map(int, result)
    return Fraction(numerator=numerator, denominator=denominator)


@rule(pp.Combine(pp.Word(pp.nums) + "." - pp.Word(pp.nums).setName('integer')))
def decimal(result: pp.ParseResults):
    """A Fraction as decimal literal, such as ``13.37``"""
    numerator = int(result[0].replace(".", ""))
    denominator = 10 ** (len(result[0]) - result[0].index(".") - 1)
    return Fraction(numerator=numerator, denominator=denominator)


@unparse.register
def unparse_fraction(what: Fraction):
    return f"{what.numerator} : {what.denominator}"


@rule(pp.Word(pp.nums))
def integer(result: pp.ParseResults):
    """An integer literal, such as ``1337``"""
    return Integer(value=int(result[0]))


@unparse.register
def unparse_integer(what: Integer):
    return f"{what.value}"


PRIMITIVES = pp.MatchFirst((reference, fraction, decimal, integer))
NESTED = pp.Forward()


@rule(NESTED + pp.MatchFirst(list("+-*/")) - NESTED, name="LHS [+-*/] RHS")
def binary_operator(result: pp.ParseResults):
    """Binary operator of nested expressions, such as ``(13 + 37) * 13.12"""
    lhs, symbol, rhs = result
    return OperatorBinary(symbol=symbol, children=(lhs, rhs))


@unparse.register
def unparse_binary_operator(what: OperatorBinary):
    lhs, rhs = map(unparse, what.children)
    return f"({lhs} {what.symbol} {rhs})"


NESTED << pp.MatchFirst(
    (
        (pp.Suppress("(") + binary_operator + pp.Suppress(")")).setName(
            f"'(' {binary_operator.name} ')'"
        ),
        PRIMITIVES,
    )
)

LINE_COMMENT = pp.Optional(pp.Literal("#") + pp.SkipTo(pp.StringEnd()))


@rule(IDENTIFIER.copy() - pp.Suppress(":=") - (binary_operator | NESTED) + LINE_COMMENT)
def assignment(result: pp.ParseResults):
    """Assignment to a name, such as ``foo := 12 + bar"""
    name, expression = result
    return Assign(name=name, expression=expression)


@unparse.register
def unparse_assignment(what: Assign):
    return f"{what.name} := {unparse(what.expression)}"


@rule(pp.Suppress(">>>") - (binary_operator | NESTED) + LINE_COMMENT)
def evaluation(result: pp.ParseResults):
    """Evaluation of an expression, such as ``>>> a + b``"""
    expression = result[0]
    return Evaluate(expression=expression)


@unparse.register
def unparse_evaluation(what: Evaluate):
    return f">>> {unparse(what.expression)}"


TOP_LEVEL: pp.ParseExpression = (evaluation | assignment)
