from typing import Mapping, Iterable, Union

import attr

from .transpyle import EvaluationError, Expression, Identifier
from ._debug import debug_print, DEBUG_CHANNEL


@attr.s(frozen=True, auto_attribs=True)
class Evaluate:
    expression: Expression


@attr.s(frozen=True, auto_attribs=True)
class Assign:
    name: Identifier
    expression: Expression


def eval(instructions: Iterable[Union[Assign, Evaluate]]):
    """Evaluate a series of instructions"""
    namespace: Mapping[Identifier, Expression] = {}
    for instruction in instructions:
        if type(instruction) is Assign:
            namespace = eval_assign(instruction, namespace)
        elif type(instruction) is Evaluate:
            yield eval_evaluate(instruction, namespace)
        else:
            raise EvaluationError(f"Unknown instruction: {instruction}")


def eval_assign(instruction: Assign, namespace: Mapping[Identifier, Expression]):
    from .parser import unparse
    expression = instruction.expression.specialize({})
    if expression is not instruction.expression:
        new_source = repr(unparse(expression))
        debug_print(DEBUG_CHANNEL.INTERPRET, repr(unparse(instruction)), '=>', new_source)
    else:
        debug_print(DEBUG_CHANNEL.INTERPRET, repr(unparse(instruction)))
    return {**namespace, instruction.name: expression}


def eval_evaluate(instruction: Evaluate, namespace: Mapping[Identifier, Expression]):
    from .parser import unparse
    debug_print(DEBUG_CHANNEL.INTERPRET, repr(unparse(instruction)))
    debug_print(DEBUG_CHANNEL.TRANSPYLE, repr(instruction.expression.transpyle().source))
    try:
        return instruction.expression.evaluate(namespace=namespace)
    except KeyError as e:
        (key,) = e.args
        return f"NameError: name {key!r} is not defined"
