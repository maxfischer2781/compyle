"""
Language parser/unparser definition

This module works bidirectional:
It can go from source code to expressions/statements and back again.

The parser serves to translate human-readable source-code into executable objects:
from *Toy Language* strings to ``transpyle`` expressions and ``interpret`` statements.
The parser is defined as a series of ``rule`` definitions, some of which are nested.

The unparser serves to provide a canonical source-code from executable objects:
from ``transpyle`` expressions and ``interpret`` statements to *Toy Language* strings.
The unparser is defined as separate ``unparse`` definitions, which resolve recursively.

Notably, unparser -> parser is exact whereas parser -> unparser may lose some details.
For example, parsing-unparsing a decimal literal results in a fraction literal
that represents the same value.
"""
from typing import Callable, Optional
from functools import singledispatch

import pyparsing as pp

from .variables import Reference
from .transpyle import Expression
from .numbers import Integer, Fraction
from .operators import OperatorBinary
from .interpret import Evaluate, Assign

# ToyLanguage and transpyle are free of side-effects.
# We can use PyParsing's memoizing to speed up parsing.
pp.ParserElement.enablePackrat()


@singledispatch
def unparse(what):
    """
    Translate an expression/statement to its canonical source code

    This is a ``singledispatch`` function. Use ``unparse.register(Type)`` to
    register an unparsing rule for a given ``Type``.
    """
    return repr(what)


def rule(syntax: pp.ParserElement, name: Optional[str] = None):
    """
    Define a rule to transform a syntax into an object

    This is a two-stage decorator, which takes a ``syntax`` description
    (a ``pyparsing`` parser) and then decorates a function to
    transform the parsing result to an expression.

    If ``name`` is given, it becomes the display name of the parser
    during debugging. Otherwise, the name of the decorated function
    is used in uppercase.
    """

    def bind_rule(
        transformation: Callable[[pp.ParseResults], Expression]
    ) -> pp.ParserElement:
        """Bind a ``transformation`` to the ``syntax`` rule"""
        syntax.setName(name if name is not None else transformation.__name__.upper())
        syntax.setParseAction(transformation)
        return syntax

    return bind_rule


# Note: PyParsing already ships with lots of helpers in `pyparsing.pyparsing_common`.
#       If you are *not* building a demonstrator, use these wherever applicable.
IDENTIFIER = pp.Word(pp.alphas, pp.alphas + "_").setName("IDENTIFIER")
DIGITS = pp.Word(pp.nums).setName("DIGITS")
SIGN = pp.MatchFirst(["-", "+"])


@rule(IDENTIFIER.copy())
def reference(result: pp.ParseResults):
    """A named reference, such as ``Kevin``"""
    return Reference(result[0])


@unparse.register(Reference)
def unparse_reference(what: Reference):
    return what.identifier


@rule(pp.Combine(pp.Optional(SIGN, default="+") + DIGITS))
def integer(result: pp.ParseResults):
    """An integer literal, such as ``1337``"""
    return Integer(value=int(result[0]))


@unparse.register(Integer)
def unparse_integer(what: Integer):
    return f"{what.value}"


@rule(integer + pp.Suppress(":") - integer)
def fraction(result: pp.ParseResults):
    """A Fraction literal, such as ``37 : 13``"""
    numerator, denominator = result
    return Fraction(numerator=numerator.value, denominator=denominator.value)


@rule(pp.Regex(r"-?\d+\.\d+"))
def decimal(result: pp.ParseResults):
    """A Fraction as decimal literal, such as ``13.37``"""
    numerator = int(result[0].replace(".", ""))
    denominator = 10 ** (len(result[0]) - result[0].index(".") - 1)
    return Fraction(numerator=numerator, denominator=denominator)


@unparse.register(Fraction)
def unparse_fraction(what: Fraction):
    return f"{what.numerator} : {what.denominator}"


PRIMITIVES = pp.MatchFirst((reference, fraction, decimal, integer))
NESTED = pp.Forward()


@rule(NESTED + pp.oneOf("+ - * /") - NESTED, name="LHS [+-*/] RHS")
def binary_operator(result: pp.ParseResults):
    """Binary operator of nested expressions, such as ``(13 + 37) * 13.12"""
    lhs, symbol, rhs = result
    return OperatorBinary(symbol=symbol, children=(lhs, rhs))


@unparse.register(OperatorBinary)
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

LINE_COMMENT = pp.Suppress(pp.Optional(pp.Literal("#") + pp.SkipTo(pp.StringEnd())))


@rule(IDENTIFIER - pp.Suppress(":=") - (binary_operator | NESTED) + LINE_COMMENT)
def assignment(result: pp.ParseResults):
    """Assignment to a name, such as ``foo := 12 + bar"""
    name, expression = result
    return Assign(name=name, expression=expression)


@unparse.register(Assign)
def unparse_assignment(what: Assign):
    return f"{what.name} := {unparse(what.expression)}"


@rule(pp.Suppress(">>>") - (binary_operator | NESTED) + LINE_COMMENT)
def evaluation(result: pp.ParseResults):
    """Evaluation of an expression, such as ``>>> a + b``"""
    expression = result[0]
    return Evaluate(expression=expression)


@unparse.register(Evaluate)
def unparse_evaluation(what: Evaluate):
    return f">>> {unparse(what.expression)}"


TOP_LEVEL: pp.ParseExpression = (evaluation | assignment)
