from typing import Iterable
import itertools
import sys

import pyparsing as pp

from .interpret import eval
from .parser import TOP_LEVEL
from ._debug import debug_enabled, debug_print


# Debugging for PyParsing
def show_parse_location(instring, start, end=None):
    print("    " + instring)
    if end is not None and end != start:
        print("   " + (" " * start) + "^" + ("-" * (end - start)) + "^")
    else:
        print("   " + (" " * start) + "^")


def on_start_parse(instring, loc, expr):
    print("! Search:", expr)
    show_parse_location(instring, loc + 1)


def on_find_parse(instring, startloc, endloc, expr, toks):
    from .parser import unparse
    print("! +Found:", expr, " -> ", repr(unparse(toks[0])))
    show_parse_location(instring, startloc, endloc)


def on_fail_parse(instring, loc, expr, exc: pp.ParseBaseException):
    print("! Reject:", expr, '(', exc, ')')
    show_parse_location(instring, exc.column)


def set_parser_debug(on_success=False):
    """Activate PyParsing debugging for most expressions"""
    from .parser import PRIMITIVES, NESTED, binary_operator

    for expression in (PRIMITIVES, NESTED, binary_operator):
        expression.setDebugActions(
            on_start_parse if on_success else lambda *args: True,
            on_find_parse if on_success else lambda *args: True,
            on_fail_parse,
        )


def parse_source(source: Iterable[str]):
    for line in source:
        try:
            instruction = TOP_LEVEL.parseString(line, parseAll=True)[0]
        except pp.ParseBaseException as exc:
            on_fail_parse(line, None, None, exc)
            sys.exit(1)
        else:
            yield instruction


def run(source: Iterable[str]):
    debug_print('frontend', "I heard you like to eval")
    debug_print('frontend', "so we put an eval in your eval")
    debug_print('frontend', "so you can eval while you eval")
    for result in eval(parse_source(source)):
        print(result)


if __name__ == "__main__":
    if debug_enabled('frontend'):
        set_parser_debug(on_success=True)
    executable, *code = sys.argv
    run(itertools.chain.from_iterable(block.splitlines() for block in code))
