# This file is from https://github.com/python/typeshed as of commit sha b6d28acb2368cdd8c87554e01e22e134061997d6
# Copyright github.com/python/typeshed project contributors

import sys
from typing import Any, ClassVar

from typing_extensions import Literal, TypeAlias

PyCF_ONLY_AST: Literal[1024]
if sys.version_info >= (3, 8):
    PyCF_TYPE_COMMENTS: Literal[4096]
    PyCF_ALLOW_TOP_LEVEL_AWAIT: Literal[8192]

_Identifier: TypeAlias = str

class AST:
    if sys.version_info >= (3, 10):
        __match_args__ = ()
    _attributes: ClassVar[tuple[str, ...]]
    _fields: ClassVar[tuple[str, ...]]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    # TODO: Not all nodes have all of the following attributes
    lineno: int
    col_offset: int
    if sys.version_info >= (3, 8):
        end_lineno: int | None
        end_col_offset: int | None
        type_comment: str | None

class mod(AST): ...

if sys.version_info >= (3, 8):
    class type_ignore(AST): ...

    class TypeIgnore(type_ignore):
        if sys.version_info >= (3, 10):
            __match_args__ = ("lineno", "tag")
        tag: str

    class FunctionType(mod):
        if sys.version_info >= (3, 10):
            __match_args__ = ("argtypes", "returns")
        argtypes: list[expr]
        returns: expr

class Module(mod):
    if sys.version_info >= (3, 10):
        __match_args__ = ("body", "type_ignores")
    body: list[stmt]
    if sys.version_info >= (3, 8):
        type_ignores: list[TypeIgnore]

class Interactive(mod):
    if sys.version_info >= (3, 10):
        __match_args__ = ("body",)
    body: list[stmt]

class Expression(mod):
    if sys.version_info >= (3, 10):
        __match_args__ = ("body",)
    body: expr

class stmt(AST): ...

class FunctionDef(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = (
            "name",
            "args",
            "body",
            "decorator_list",
            "returns",
            "type_comment",
        )
    name: _Identifier
    args: arguments
    body: list[stmt]
    decorator_list: list[expr]
    returns: expr | None

class AsyncFunctionDef(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = (
            "name",
            "args",
            "body",
            "decorator_list",
            "returns",
            "type_comment",
        )
    name: _Identifier
    args: arguments
    body: list[stmt]
    decorator_list: list[expr]
    returns: expr | None

class ClassDef(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("name", "bases", "keywords", "body", "decorator_list")
    name: _Identifier
    bases: list[expr]
    keywords: list[keyword]
    body: list[stmt]
    decorator_list: list[expr]

class Return(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value",)
    value: expr | None

class Delete(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("targets",)
    targets: list[expr]

class Assign(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("targets", "value", "type_comment")
    targets: list[expr]
    value: expr

class AugAssign(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("target", "op", "value")
    target: expr
    op: operator
    value: expr

class AnnAssign(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("target", "annotation", "value", "simple")
    target: expr
    annotation: expr
    value: expr | None
    simple: int

class For(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("target", "iter", "body", "orelse", "type_comment")
    target: expr
    iter: expr
    body: list[stmt]
    orelse: list[stmt]

class AsyncFor(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("target", "iter", "body", "orelse", "type_comment")
    target: expr
    iter: expr
    body: list[stmt]
    orelse: list[stmt]

class While(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("test", "body", "orelse")
    test: expr
    body: list[stmt]
    orelse: list[stmt]

class If(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("test", "body", "orelse")
    test: expr
    body: list[stmt]
    orelse: list[stmt]

class With(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("items", "body", "type_comment")
    items: list[withitem]
    body: list[stmt]

class AsyncWith(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("items", "body", "type_comment")
    items: list[withitem]
    body: list[stmt]

class Raise(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("exc", "cause")
    exc: expr | None
    cause: expr | None

class Try(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("body", "handlers", "orelse", "finalbody")
    body: list[stmt]
    handlers: list[ExceptHandler]
    orelse: list[stmt]
    finalbody: list[stmt]

if sys.version_info >= (3, 11):
    class TryStar(stmt):
        __match_args__ = ("body", "handlers", "orelse", "finalbody")
        body: list[stmt]
        handlers: list[ExceptHandler]
        orelse: list[stmt]
        finalbody: list[stmt]

class Assert(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("test", "msg")
    test: expr
    msg: expr | None

class Import(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("names",)
    names: list[alias]

class ImportFrom(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("module", "names", "level")
    module: str | None
    names: list[alias]
    level: int

class Global(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("names",)
    names: list[_Identifier]

class Nonlocal(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("names",)
    names: list[_Identifier]

class Expr(stmt):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value",)
    value: expr

class Pass(stmt): ...
class Break(stmt): ...
class Continue(stmt): ...
class expr(AST): ...

class BoolOp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("op", "values")
    op: boolop
    values: list[expr]

class BinOp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("left", "op", "right")
    left: expr
    op: operator
    right: expr

class UnaryOp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("op", "operand")
    op: unaryop
    operand: expr

class Lambda(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("args", "body")
    args: arguments
    body: expr

class IfExp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("test", "body", "orelse")
    test: expr
    body: expr
    orelse: expr

class Dict(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("keys", "values")
    keys: list[expr | None]
    values: list[expr]

class Set(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elts",)
    elts: list[expr]

class ListComp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elt", "generators")
    elt: expr
    generators: list[comprehension]

class SetComp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elt", "generators")
    elt: expr
    generators: list[comprehension]

class DictComp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("key", "value", "generators")
    key: expr
    value: expr
    generators: list[comprehension]

class GeneratorExp(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elt", "generators")
    elt: expr
    generators: list[comprehension]

class Await(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value",)
    value: expr

class Yield(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value",)
    value: expr | None

class YieldFrom(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value",)
    value: expr

class Compare(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("left", "ops", "comparators")
    left: expr
    ops: list[cmpop]
    comparators: list[expr]

class Call(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("func", "args", "keywords")
    func: expr
    args: list[expr]
    keywords: list[keyword]

class FormattedValue(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value", "conversion", "format_spec")
    value: expr
    conversion: int
    format_spec: expr | None

class JoinedStr(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("values",)
    values: list[expr]

if sys.version_info < (3, 8):
    class Num(expr):  # Deprecated in 3.8; use Constant
        n: complex

    class Str(expr):  # Deprecated in 3.8; use Constant
        s: str

    class Bytes(expr):  # Deprecated in 3.8; use Constant
        s: bytes

    class NameConstant(expr):  # Deprecated in 3.8; use Constant
        value: Any

    class Ellipsis(expr): ...  # Deprecated in 3.8; use Constant

class Constant(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value", "kind")
    value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
    kind: str | None
    # Aliases for value, for backwards compatibility
    s: Any
    n: complex

if sys.version_info >= (3, 8):
    class NamedExpr(expr):
        if sys.version_info >= (3, 10):
            __match_args__ = ("target", "value")
        target: expr
        value: expr

class Attribute(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value", "attr", "ctx")
    value: expr
    attr: _Identifier
    ctx: expr_context

if sys.version_info >= (3, 9):
    _Slice: TypeAlias = expr
else:
    class slice(AST): ...
    _Slice: TypeAlias = slice

class Slice(_Slice):
    if sys.version_info >= (3, 10):
        __match_args__ = ("lower", "upper", "step")
    lower: expr | None
    upper: expr | None
    step: expr | None

if sys.version_info < (3, 9):
    class ExtSlice(slice):
        dims: list[slice]

    class Index(slice):
        value: expr

class Subscript(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value", "slice", "ctx")
    value: expr
    slice: _Slice
    ctx: expr_context

class Starred(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("value", "ctx")
    value: expr
    ctx: expr_context

class Name(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("id", "ctx")
    id: _Identifier
    ctx: expr_context

class List(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elts", "ctx")
    elts: list[expr]
    ctx: expr_context

class Tuple(expr):
    if sys.version_info >= (3, 10):
        __match_args__ = ("elts", "ctx")
    elts: list[expr]
    ctx: expr_context
    if sys.version_info >= (3, 9):
        dims: list[expr]

class expr_context(AST): ...

if sys.version_info < (3, 9):
    class AugLoad(expr_context): ...
    class AugStore(expr_context): ...
    class Param(expr_context): ...

    class Suite(mod):
        body: list[stmt]

class Del(expr_context): ...
class Load(expr_context): ...
class Store(expr_context): ...
class boolop(AST): ...
class And(boolop): ...
class Or(boolop): ...
class operator(AST): ...
class Add(operator): ...
class BitAnd(operator): ...
class BitOr(operator): ...
class BitXor(operator): ...
class Div(operator): ...
class FloorDiv(operator): ...
class LShift(operator): ...
class Mod(operator): ...
class Mult(operator): ...
class MatMult(operator): ...
class Pow(operator): ...
class RShift(operator): ...
class Sub(operator): ...
class unaryop(AST): ...
class Invert(unaryop): ...
class Not(unaryop): ...
class UAdd(unaryop): ...
class USub(unaryop): ...
class cmpop(AST): ...
class Eq(cmpop): ...
class Gt(cmpop): ...
class GtE(cmpop): ...
class In(cmpop): ...
class Is(cmpop): ...
class IsNot(cmpop): ...
class Lt(cmpop): ...
class LtE(cmpop): ...
class NotEq(cmpop): ...
class NotIn(cmpop): ...

class comprehension(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = ("target", "iter", "ifs", "is_async")
    target: expr
    iter: expr
    ifs: list[expr]
    is_async: int

class excepthandler(AST): ...

class ExceptHandler(excepthandler):
    if sys.version_info >= (3, 10):
        __match_args__ = ("type", "name", "body")
    type: expr | None
    name: _Identifier | None
    body: list[stmt]

class arguments(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = (
            "posonlyargs",
            "args",
            "vararg",
            "kwonlyargs",
            "kw_defaults",
            "kwarg",
            "defaults",
        )
    if sys.version_info >= (3, 8):
        posonlyargs: list[arg]
    args: list[arg]
    vararg: arg | None
    kwonlyargs: list[arg]
    kw_defaults: list[expr | None]
    kwarg: arg | None
    defaults: list[expr]

class arg(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = ("arg", "annotation", "type_comment")
    arg: _Identifier
    annotation: expr | None

class keyword(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = ("arg", "value")
    arg: _Identifier | None
    value: expr

class alias(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = ("name", "asname")
    name: _Identifier
    asname: _Identifier | None

class withitem(AST):
    if sys.version_info >= (3, 10):
        __match_args__ = ("context_expr", "optional_vars")
    context_expr: expr
    optional_vars: expr | None

if sys.version_info >= (3, 10):
    class Match(stmt):
        __match_args__ = ("subject", "cases")
        subject: expr
        cases: list[match_case]

    class pattern(AST): ...
    # Without the alias, Pyright complains variables named pattern are recursively defined
    _Pattern: TypeAlias = pattern

    class match_case(AST):
        __match_args__ = ("pattern", "guard", "body")
        pattern: _Pattern
        guard: expr | None
        body: list[stmt]

    class MatchValue(pattern):
        __match_args__ = ("value",)
        value: expr

    class MatchSingleton(pattern):
        __match_args__ = ("value",)
        value: Literal[True, False, None]

    class MatchSequence(pattern):
        __match_args__ = ("patterns",)
        patterns: list[pattern]

    class MatchStar(pattern):
        __match_args__ = ("name",)
        name: _Identifier | None

    class MatchMapping(pattern):
        __match_args__ = ("keys", "patterns", "rest")
        keys: list[expr]
        patterns: list[pattern]
        rest: _Identifier | None

    class MatchClass(pattern):
        __match_args__ = ("cls", "patterns", "kwd_attrs", "kwd_patterns")
        cls: expr
        patterns: list[pattern]
        kwd_attrs: list[_Identifier]
        kwd_patterns: list[pattern]

    class MatchAs(pattern):
        __match_args__ = ("pattern", "name")
        pattern: _Pattern | None
        name: _Identifier | None

    class MatchOr(pattern):
        __match_args__ = ("patterns",)
        patterns: list[pattern]
