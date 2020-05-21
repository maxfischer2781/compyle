#############################################
Toy Language to Python Interpreter/Transpiler
#############################################

This is an example project for implementing a basic interpreter-slash-transpiler
from a simple toy language to Python::

    $ python3 -m compyle 'a := 3
    b := 4 : 12
    >>> (a / b) * 2'
    18

Toy Language
############

The *Toy Language* itself consists of expressions, which are:

* References to names, such as ``foo``,
* Literals of integers, such as ``1337``,
* Literals of fractions, such as ``13 : 37`` fractions or ``13.37`` decimals,
* Binary operators ``+``, ``-``, ``/`` and ``*``, such as ``(foo * 13.37)``.

Parentheses are mandatory around each binary operator expression
but disallowed anywhere else.

The *Toy Language Interpreter* uses statements incorporating
*Toy Language* expressions, which are:

* Assignments to names, such as ``foo := 1337``,
* Evaluations of expressions, such as ``>>> (foo / 20)``.

Statements are line-separated. A *Toy Language Program* is a sequence of statements,
such as::

    foo := 2 : 3
    bar := foo / 3
    >>> bar
    foo := 2
    >>> bar * 2

A trailing ``#`` on a statement indicates comments.
The ``#`` and the rest of the line are ignored.

Quick Tour to Compyling
#######################

The basic functionality of ``compyle`` is based on three Expression actions:

* *Evaluating* means deriving a (Python) value for an expression.
  For example, ``3 : 2`` can be evaluated to ``fractions.Fraction(3, 2)``.
* *Specialising* means updating/simplifying an expression with more information.
  For example, ``(a * 3)`` can be specialised with ``a := 3`` to ``9``.
* *Transpyling* means converting an Expression to Python source code.
  For example, ``(a * 3)`` van be transpylied to ``__namespace__["a"].evaluate() * 3``.

Points of Interest
++++++++++++++++++

The ``compyle`` setup is roughly divided into three sections:

* The abstract expression/statement setup, defining how expressions are handled:

  * `transpyle.py <compyle/transpyle.py>`_ defines expressions, how they are
    specialized, transpyled and evaluated.
  * `interpret.py <compyle/interpret.py>`_ defines statements, how they are
    processed and evaluated.

* The concrete object setup, defining what expressions can express:

  * `variables.py <compyle/variables.py>`_ defines references and how to
    translate (Python) values back to expressions. This allows evaluating
    expressions and references to specialise them.
  * `numbers.py <compyle/numbers.py>`_ defines the expressions for Integers
    and Fractions. There are no floats, as "float literals" are translated
    to Fractions.
  * `operator.py <compyle/operators.py>`_ defines basic arithmetic operators

* The client setup, defining how to write expressions and statements:

  * `parser.py <compyle/parser.py>`_ defines parsing of *Toy Language*
    to expressions and statements.
  * `frontend.py <compyle/frontend.py>`_ defines the command line interface.

Restrictions
############

There are a couple of restrictions from the design of ``compyle``.
These *could* be lifted, but would complicate understanding of the code.

* Expressions represent all levels of AST, values and transpiled code.
* Scoping/Namespaces are not first-class, but tied to Expressions.
* Specialisation is all-or-nothing and eager.
* The transpilation target is plain Python source code.
