from typing import Iterable
import argparse

from .frontend import run
from ._debug import DEBUG_CHANNEL, ENABLED_CHANNELS


def interactive():
    print("I heard you like to eval")
    print("so we put an eval in your eval")
    print("so you can eval while you eval")
    print("                 - AD, 2020 AD")
    run(iter(input, ""))


def noninteractive(inputs: Iterable[str]):
    run(iter_inputs(inputs))


def iter_inputs(inputs: Iterable[str]):
    for raw_input in inputs:
        try:
            with open(raw_input) as in_stream:
                yield from in_stream
        except FileNotFoundError:
            yield from raw_input.splitlines()


CLI = argparse.ArgumentParser(
    description="The Toy Language Interpreter/Transpyler", prog="compyle",
)
CLI.add_argument(
    "INPUT",
    nargs="*",
    help="Individual statements or paths to files of statements for non-interactive use",
)
CLI_DEBUG = CLI.add_argument_group("debug controls")
CLI_DEBUG.add_argument(
    "--show-parsing", help="Show parsing details", action="store_true",
)
CLI_DEBUG.add_argument(
    "--show-interpret",
    help="Show statement interpretation details",
    action="store_true",
)
CLI_DEBUG.add_argument(
    "--show-transpyle", help="Show transpyled source code", action="store_true",
)

options = CLI.parse_args()
for requested, channel in (
    (options.show_parsing, DEBUG_CHANNEL.PARSING),
    (options.show_interpret, DEBUG_CHANNEL.INTERPRET),
    (options.show_transpyle, DEBUG_CHANNEL.TRANSPYLE),
):
    if requested:
        ENABLED_CHANNELS.add(channel)

if options.INPUT:
    noninteractive(options.INPUT)
else:
    interactive()
