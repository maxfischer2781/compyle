"""
The interpreter/transpiler core definition
"""
from typing import Optional, Mapping, Any, Callable, Set, TypeVar, Generic, Union, Tuple
from typing_extensions import Protocol, runtime_checkable
from collections import ChainMap

import attr


T = TypeVar("T")
E = TypeVar("E", bound="Expression")


class CompylationError(BaseException):
    """An internal error during transpylation/evaluation"""


class EvaluationError(BaseException):
    """An exception when trying to get the value of an expression"""


# === Expression Level Identifiers ===
# These are the placeholders *used internally* for anything our
# language does not understand. They are not the same as variables
# as perceived by programmers.
#
# For example, given the source code ``x + 1337``, any language
# likely makes ``x`` a placeholder. However, if numbers are not
# built into the language then ``1337`` will be a placeholder
# as well; similarly, ``+`` might be a dynamic operation.
Identifier = str


# === Expression Interfaces ===
# The basic layout used to represent, specialize and transpile
# computation/transformation instructions. Expressions represent
# specific instructions, whereas Names are the generic placeholders
# for values to be filled in. To *specialize* an expression means
# filling in some names with values, and *transpyling* it means
# creating executable code.
#
# For example, the Python code ``x + y + z`` would be represented by
# an Expression for ``+`` with free Names ``x``, ``y`` and ``z``. When
# specialising ``y = 3``, it would reduce to ``x + 3 + z`` - another
# ``+`` Expression with free Names ``x``. When transpyling this,
# it would create the Python bytecode for ``sum(x, 3, z)``.


@attr.s(frozen=True, auto_attribs=True)
class Names(Protocol):
    """Names of an expression"""

    #: names which can still be bound to some value
    free: Set[Identifier] = attr.ib(factory=set)
    #: names which represent some value
    bound: Mapping[Identifier, Any] = attr.ib(factory=dict)

    def bind(self, namespace: 'Mapping[Identifier, Expression]') -> 'Names':
        return Names(
            free=self.free - namespace.keys(), bound={**self.bound, **namespace}
        )


@runtime_checkable
class Expression(Protocol[T]):
    """Structure of every Expression"""

    __slots__ = ()

    @property
    def names(self) -> Names:
        raise NotImplementedError

    def specialize(
        self: E, namespace: 'Mapping[Identifier, Expression]'
    ) -> 'Union[E, Expression]':
        """Create a new Expression to which all of ``namespace`` is bound already"""
        raise NotImplementedError

    # === NOTE ===
    # If we wanted to support multiple backends (e.g. Python, C++, ...)
    # these would be single-dispatch methods. This would allow us to define
    # per-language transpilers/evaluators (e.g. python_backend.transpile,
    # cpp_backend.transpile, ...).
    def transpyle(self: E) -> 'Transpylation[E, T]':
        """Create appropriate Python code for this expression"""
        raise NotImplementedError

    def evaluate(self, namespace: 'Mapping[Identifier, Expression]') -> T:
        """Evaluate the expression to its value"""
        return self.transpyle().evaluate(namespace)


@attr.s(frozen=True, auto_attribs=True)
class Transpylation(Generic[E, T]):
    """An expression transpiled to Python code"""

    parent: E
    source: str
    _code: Optional[Any] = attr.ib(init=False, default=None)

    def evaluate(self, namespace: 'Mapping[Identifier, Expression]') -> T:
        assert self.parent.names.bound.keys().isdisjoint(namespace)
        if self._code is None:
            object.__setattr__(self, "_code", self.__compile())
        return eval(
            self._code, {"__namespace__": namespace, **self.parent.names.bound}
        )

    def __compile(self) -> Callable[..., T]:
        return compile(self.source, self.source, "eval", dont_inherit=True)


# === Primitive and Compound Expressions ===
# Primitives are the fundamental kinds of expressions that do not depend
# on others. In contrast, Compounds consist of other expressions.
#
# For example, the Python code ``x + 13`` would be represented by
# a PrimitiveExpression for the reference to ``x`` and the literal ``13``.
# In turn, a CompoundExpression representing ``+`` would contain  the
# two PrimitiveExpressions.
#
# Note that a PrimitiveExpression is not necessarily primitive in the
# target language as well. For example, a language with decimal instead
# of float numbers would represent ``13.12`` as a single PrimitiveExpression,
# but transpile it to ``Fraction(1312, 100)``.


@attr.s(frozen=True, auto_attribs=True)
class CompoundExpression(Expression[T]):
    children: Tuple[Expression, ...]
    _names: Optional[Names] = attr.ib(init=False, default=None)

    @property
    def names(self) -> Names:
        if self._names is None:
            object.__setattr__(
                self,
                "_names",
                Names(
                    free=set.union(*(child.names.free for child in self.children)),
                    bound=ChainMap(*(child.names.bound for child in self.children)),
                ),
            )
        return self._names
