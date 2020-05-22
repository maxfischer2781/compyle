from typing import Iterable
from fractions import Fraction

import pytest

from compyle.interpret import eval
from compyle.frontend import parse_source


def evaluate(source: Iterable[str]):
    return eval(parse_source(source))


EXPRESSIONS = [
    ('3', 3),
    ('-4', -4),
    ('3:4', Fraction(3, 4)),
    ('3 : 4', Fraction(3, 4)),
    ('9:12', Fraction(3, 4)),
    ('-9:12', Fraction(-3, 4)),
    ('9.12', Fraction(912, 100)),
    ('3/4', Fraction(3, 4)),
    ('3*4', 12),
    ('3-4', -1),
]


@pytest.mark.parametrize('expression, result', EXPRESSIONS)
def test_evaluate(expression, result):
    assert next(evaluate([f'>>> {expression}'])) == result
