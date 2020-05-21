from typing import Iterable
import sys

import pyparsing as pp

from .interpret import eval
from .parser import TOP_LEVEL
from ._debug import debug_enabled, DEBUG_CHANNEL


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
    print("! Reject:", expr, "(", exc, ")")
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
    for line in map(str.strip, source):
        if not line:
            continue
        try:
            instruction = TOP_LEVEL.parseString(line, parseAll=True)[0]
        except pp.ParseBaseException as exc:
            on_fail_parse(line, None, None, exc)
            sys.exit(1)
        else:
            yield instruction


def run(source: Iterable[str]):
    if debug_enabled(DEBUG_CHANNEL.PARSING):
        set_parser_debug(on_success=True)
    for result in eval(parse_source(source)):
        print(result)
