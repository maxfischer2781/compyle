import sys
import itertools

from .frontend import run

executable, *code = sys.argv
run(itertools.chain.from_iterable(block.splitlines() for block in code))
