# This file is from https://github.com/python/typeshed as of commit sha b6d28acb2368cdd8c87554e01e22e134061997d6
# Copyright github.com/python/typeshed project contributors

import collections  # Needed by aliases like DefaultDict, see mypy issue 2986
import sys
from abc import ABCMeta, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from re import Pattern as Pattern
from re import match as Match
from types import (
    BuiltinFunctionType,
    CodeType,
    FrameType,
    FunctionType,
    MethodDescriptorType,
    MethodType,
    MethodWrapperType,
    ModuleType,
    TracebackType,
    WrapperDescriptorType,
)

import _typeshed
from _collections_abc import dict_items, dict_keys, dict_values
from _typeshed import IdentityFunction, Incomplete, SupportsKeysAndGetItem
from typing_extensions import Never as _Never
from typing_extensions import ParamSpec as _ParamSpec
from typing_extensions import final as _final

__all__ = [
    "AbstractSet",
    "Any",
    "AnyStr",
    "AsyncContextManager",
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "ByteString",
    "Callable",
    "ChainMap",
    "ClassVar",
    "Collection",
    "Container",
    "ContextManager",
    "Coroutine",
    "Counter",
    "DefaultDict",
    "Deque",
    "Dict",
    "FrozenSet",
    "Generator",
    "Generic",
    "Hashable",
    "ItemsView",
    "Iterable",
    "Iterator",
    "KeysView",
    "List",
    "Mapping",
    "MappingView",
    "MutableMapping",
    "MutableSequence",
    "MutableSet",
    "NamedTuple",
    "NewType",
    "Optional",
    "Reversible",
    "Sequence",
    "Set",
    "Sized",
    "SupportsAbs",
    "SupportsBytes",
    "SupportsComplex",
    "SupportsFloat",
    "SupportsInt",
    "SupportsRound",
    "Text",
    "Tuple",
    "Type",
    "TypeVar",
    "Union",
    "ValuesView",
    "TYPE_CHECKING",
    "cast",
    "get_type_hints",
    "no_type_check",
    "no_type_check_decorator",
    "overload",
    "ForwardRef",
    "NoReturn",
    "OrderedDict",
]

if sys.version_info >= (3, 8):
    __all__ += [
        "Final",
        "Literal",
        "Protocol",
        "SupportsIndex",
        "TypedDict",
        "final",
        "get_args",
        "get_origin",
        "runtime_checkable",
    ]

if sys.version_info >= (3, 9):
    __all__ += ["Annotated", "BinaryIO", "IO", "Match", "Pattern", "TextIO"]

if sys.version_info >= (3, 10):
    __all__ += [
        "Concatenate",
        "ParamSpec",
        "ParamSpecArgs",
        "ParamSpecKwargs",
        "TypeAlias",
        "TypeGuard",
        "is_typeddict",
    ]

if sys.version_info >= (3, 11):
    __all__ += [
        "LiteralString",
        "Never",
        "NotRequired",
        "Required",
        "Self",
        "TypeVarTuple",
        "Unpack",
        "assert_never",
        "assert_type",
        "clear_overloads",
        "dataclass_transform",
        "get_overloads",
        "reveal_type",
    ]

ContextManager = AbstractContextManager
AsyncContextManager = AbstractAsyncContextManager

# This itself is only available during type checking
def type_check_only(func_or_cls: _F) -> _F: ...

Any = object()

@_final
class TypeVar:
    __name__: str
    __bound__: Any | None
    __constraints__: tuple[Any, ...]
    __covariant__: bool
    __contravariant__: bool
    def __init__(
        self,
        name: str,
        *constraints: Any,
        bound: Any | None = ...,
        covariant: bool = ...,
        contravariant: bool = ...,
    ) -> None: ...
    if sys.version_info >= (3, 10):
        def __or__(self, right: Any) -> _SpecialForm: ...
        def __ror__(self, left: Any) -> _SpecialForm: ...
    if sys.version_info >= (3, 11):
        def __typing_subst__(self, arg: Incomplete) -> Incomplete: ...

# Used for an undocumented mypy feature. Does not exist at runtime.
_promote = object()

# N.B. Keep this definition in sync with typing_extensions._SpecialForm
@_final
class _SpecialForm:
    def __getitem__(self, parameters: Any) -> object: ...
    if sys.version_info >= (3, 10):
        def __or__(self, other: Any) -> _SpecialForm: ...
        def __ror__(self, other: Any) -> _SpecialForm: ...

_F = TypeVar("_F", bound=Callable[..., Any])
_P = _ParamSpec("_P")
_T = TypeVar("_T")

def overload(func: _F) -> _F: ...

# Unlike the vast majority module-level objects in stub files,
# these `_SpecialForm` objects in typing need the default value `= ...`,
# due to the fact that they are used elswhere in the same file.
# Otherwise, flake8 erroneously flags them as undefined.
# `_SpecialForm` objects in typing.py that are not used elswhere in the same file
# do not need the default value assignment.
Union: _SpecialForm = ...
Generic: _SpecialForm = ...
# Protocol is only present in 3.8 and later, but mypy needs it unconditionally
Protocol: _SpecialForm = ...
Callable: _SpecialForm = ...
Type: _SpecialForm = ...
NoReturn: _SpecialForm = ...
ClassVar: _SpecialForm = ...

Optional: _SpecialForm
Tuple: _SpecialForm
if sys.version_info >= (3, 8):
    Final: _SpecialForm
    def final(f: _T) -> _T: ...
    Literal: _SpecialForm
    # TypedDict is a (non-subscriptable) special form.
    TypedDict: object

if sys.version_info >= (3, 11):
    Self: _SpecialForm
    Never: _SpecialForm = ...
    Unpack: _SpecialForm
    Required: _SpecialForm
    NotRequired: _SpecialForm
    LiteralString: _SpecialForm

    class TypeVarTuple:
        __name__: str
        def __init__(self, name: str) -> None: ...
        def __iter__(self) -> Any: ...
        def __typing_subst__(self, arg: Never) -> Never: ...
        def __typing_prepare_subst__(
            self, alias: Incomplete, args: Incomplete
        ) -> Incomplete: ...

if sys.version_info >= (3, 10):
    class ParamSpecArgs:
        __origin__: ParamSpec
        def __init__(self, origin: ParamSpec) -> None: ...

    class ParamSpecKwargs:
        __origin__: ParamSpec
        def __init__(self, origin: ParamSpec) -> None: ...

    class ParamSpec:
        __name__: str
        __bound__: Any | None
        __covariant__: bool
        __contravariant__: bool
        def __init__(
            self,
            name: str,
            *,
            bound: Any | None = ...,
            contravariant: bool = ...,
            covariant: bool = ...,
        ) -> None: ...
        @property
        def args(self) -> ParamSpecArgs: ...
        @property
        def kwargs(self) -> ParamSpecKwargs: ...
        if sys.version_info >= (3, 11):
            def __typing_subst__(self, arg: Incomplete) -> Incomplete: ...
            def __typing_prepare_subst__(
                self, alias: Incomplete, args: Incomplete
            ) -> Incomplete: ...

        def __or__(self, right: Any) -> _SpecialForm: ...
        def __ror__(self, left: Any) -> _SpecialForm: ...

    Concatenate: _SpecialForm
    TypeAlias: _SpecialForm
    TypeGuard: _SpecialForm

    class NewType:
        def __init__(self, name: str, tp: Any) -> None: ...
        def __call__(self, x: _T) -> _T: ...
        def __or__(self, other: Any) -> _SpecialForm: ...
        def __ror__(self, other: Any) -> _SpecialForm: ...
        __supertype__: type

else:
    def NewType(name: str, tp: Any) -> Any: ...

# These type variables are used by the container types.
_S = TypeVar("_S")
_KT = TypeVar("_KT")  # Key type.
_VT = TypeVar("_VT")  # Value type.
_T_co = TypeVar("_T_co", covariant=True)  # Any type covariant containers.
_V_co = TypeVar("_V_co", covariant=True)  # Any type covariant containers.
_KT_co = TypeVar("_KT_co", covariant=True)  # Key type covariant containers.
_VT_co = TypeVar("_VT_co", covariant=True)  # Value type covariant containers.
_T_contra = TypeVar("_T_contra", contravariant=True)  # Ditto contravariant.
_TC = TypeVar("_TC", bound=Type[object])

def no_type_check(arg: _F) -> _F: ...
def no_type_check_decorator(decorator: Callable[_P, _T]) -> Callable[_P, _T]: ...  # type: ignore[misc]

# Type aliases and type constructors

class _Alias:
    # Class for defining generic aliases for library types.
    def __getitem__(self, typeargs: Any) -> Any: ...

List = _Alias()
Dict = _Alias()
DefaultDict = _Alias()
Set = _Alias()
FrozenSet = _Alias()
Counter = _Alias()
Deque = _Alias()
ChainMap = _Alias()

OrderedDict = _Alias()

if sys.version_info >= (3, 9):
    Annotated: _SpecialForm

# Predefined type variables.
AnyStr = TypeVar("AnyStr", str, bytes)  # noqa: Y001

# Technically in 3.7 this inherited from GenericMeta. But let's not reflect that, since
# type checkers tend to assume that Protocols all have the ABCMeta metaclass.
class _ProtocolMeta(ABCMeta): ...

# Abstract base classes.

def runtime_checkable(cls: _TC) -> _TC: ...
@runtime_checkable
class SupportsInt(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __int__(self) -> int: ...

@runtime_checkable
class SupportsFloat(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __float__(self) -> float: ...

@runtime_checkable
class SupportsComplex(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __complex__(self) -> complex: ...

@runtime_checkable
class SupportsBytes(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __bytes__(self) -> bytes: ...

if sys.version_info >= (3, 8):
    @runtime_checkable
    class SupportsIndex(Protocol, metaclass=ABCMeta):
        @abstractmethod
        def __index__(self) -> int: ...

@runtime_checkable
class SupportsAbs(Protocol[_T_co]):
    @abstractmethod
    def __abs__(self) -> _T_co: ...

@runtime_checkable
class SupportsRound(Protocol[_T_co]):
    @overload
    @abstractmethod
    def __round__(self) -> int: ...
    @overload
    @abstractmethod
    def __round__(self, __ndigits: int) -> _T_co: ...

@runtime_checkable
class Sized(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __len__(self) -> int: ...

@runtime_checkable
class Hashable(Protocol, metaclass=ABCMeta):
    # TODO: This is special, in that a subclass of a hashable class may not be hashable
    #   (for example, list vs. object). It's not obvious how to represent this. This class
    #   is currently mostly useless for static checking.
    @abstractmethod
    def __hash__(self) -> int: ...

@runtime_checkable
class Iterable(Protocol[_T_co]):
    @abstractmethod
    def __iter__(self) -> Iterator[_T_co]: ...

@runtime_checkable
class Iterator(Iterable[_T_co], Protocol[_T_co]):
    @abstractmethod
    def __next__(self) -> _T_co: ...
    def __iter__(self) -> Iterator[_T_co]: ...

@runtime_checkable
class Reversible(Iterable[_T_co], Protocol[_T_co]):
    @abstractmethod
    def __reversed__(self) -> Iterator[_T_co]: ...

class Generator(Iterator[_T_co], Generic[_T_co, _T_contra, _V_co]):
    def __next__(self) -> _T_co: ...
    @abstractmethod
    def send(self, __value: _T_contra) -> _T_co: ...
    @overload
    @abstractmethod
    def throw(
        self,
        __typ: Type[BaseException],
        __val: BaseException | object = ...,
        __tb: TracebackType | None = ...,
    ) -> _T_co: ...
    @overload
    @abstractmethod
    def throw(
        self, __typ: BaseException, __val: None = ..., __tb: TracebackType | None = ...
    ) -> _T_co: ...
    def close(self) -> None: ...
    def __iter__(self) -> Generator[_T_co, _T_contra, _V_co]: ...
    @property
    def gi_code(self) -> CodeType: ...
    @property
    def gi_frame(self) -> FrameType: ...
    @property
    def gi_running(self) -> bool: ...
    @property
    def gi_yieldfrom(self) -> Generator[Any, Any, Any] | None: ...

@runtime_checkable
class Awaitable(Protocol[_T_co]):
    @abstractmethod
    def __await__(self) -> Generator[Any, None, _T_co]: ...

class Coroutine(Awaitable[_V_co], Generic[_T_co, _T_contra, _V_co]):
    __name__: str
    __qualname__: str
    @property
    def cr_await(self) -> Any | None: ...
    @property
    def cr_code(self) -> CodeType: ...
    @property
    def cr_frame(self) -> FrameType: ...
    @property
    def cr_running(self) -> bool: ...
    @abstractmethod
    def send(self, __value: _T_contra) -> _T_co: ...
    @overload
    @abstractmethod
    def throw(
        self,
        __typ: Type[BaseException],
        __val: BaseException | object = ...,
        __tb: TracebackType | None = ...,
    ) -> _T_co: ...
    @overload
    @abstractmethod
    def throw(
        self, __typ: BaseException, __val: None = ..., __tb: TracebackType | None = ...
    ) -> _T_co: ...
    @abstractmethod
    def close(self) -> None: ...

# NOTE: This type does not exist in typing.py or PEP 484 but mypy needs it to exist.
# The parameters correspond to Generator, but the 4th is the original type.
@type_check_only
class AwaitableGenerator(
    Awaitable[_V_co],
    Generator[_T_co, _T_contra, _V_co],
    Generic[_T_co, _T_contra, _V_co, _S],
    metaclass=ABCMeta,
): ...

@runtime_checkable
class AsyncIterable(Protocol[_T_co]):
    @abstractmethod
    def __aiter__(self) -> AsyncIterator[_T_co]: ...

@runtime_checkable
class AsyncIterator(AsyncIterable[_T_co], Protocol[_T_co]):
    @abstractmethod
    def __anext__(self) -> Awaitable[_T_co]: ...
    def __aiter__(self) -> AsyncIterator[_T_co]: ...

class AsyncGenerator(AsyncIterator[_T_co], Generic[_T_co, _T_contra]):
    def __anext__(self) -> Awaitable[_T_co]: ...
    @abstractmethod
    def asend(self, __value: _T_contra) -> Awaitable[_T_co]: ...
    @overload
    @abstractmethod
    def athrow(
        self,
        __typ: Type[BaseException],
        __val: BaseException | object = ...,
        __tb: TracebackType | None = ...,
    ) -> Awaitable[_T_co]: ...
    @overload
    @abstractmethod
    def athrow(
        self, __typ: BaseException, __val: None = ..., __tb: TracebackType | None = ...
    ) -> Awaitable[_T_co]: ...
    def aclose(self) -> Awaitable[None]: ...
    @property
    def ag_await(self) -> Any: ...
    @property
    def ag_code(self) -> CodeType: ...
    @property
    def ag_frame(self) -> FrameType: ...
    @property
    def ag_running(self) -> bool: ...

@runtime_checkable
class Container(Protocol[_T_co]):
    @abstractmethod
    def __contains__(self, __x: object) -> bool: ...

@runtime_checkable
class Collection(Iterable[_T_co], Container[_T_co], Protocol[_T_co]):
    # Implement Sized (but don't have it as a base class).
    @abstractmethod
    def __len__(self) -> int: ...

class Sequence(Collection[_T_co], Reversible[_T_co], Generic[_T_co]):
    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> _T_co: ...
    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> Sequence[_T_co]: ...
    # Mixin methods
    def index(self, value: Any, start: int = ..., stop: int = ...) -> int: ...
    def count(self, value: Any) -> int: ...
    def __contains__(self, value: object) -> bool: ...
    def __iter__(self) -> Iterator[_T_co]: ...
    def __reversed__(self) -> Iterator[_T_co]: ...

class MutableSequence(Sequence[_T], Generic[_T]):
    @abstractmethod
    def insert(self, index: int, value: _T) -> None: ...
    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> _T: ...
    @overload
    @abstractmethod
    def __getitem__(self, index: slice) -> MutableSequence[_T]: ...
    @overload
    @abstractmethod
    def __setitem__(self, index: int, value: _T) -> None: ...
    @overload
    @abstractmethod
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None: ...
    @overload
    @abstractmethod
    def __delitem__(self, index: int) -> None: ...
    @overload
    @abstractmethod
    def __delitem__(self, index: slice) -> None: ...
    # Mixin methods
    def append(self, value: _T) -> None: ...
    def clear(self) -> None: ...
    def extend(self, values: Iterable[_T]) -> None: ...
    def reverse(self) -> None: ...
    def pop(self, index: int = ...) -> _T: ...
    def remove(self, value: _T) -> None: ...
    def __iadd__(self: _typeshed.Self, values: Iterable[_T]) -> _typeshed.Self: ...

class AbstractSet(Collection[_T_co], Generic[_T_co]):
    @abstractmethod
    def __contains__(self, x: object) -> bool: ...
    def _hash(self) -> int: ...
    # Mixin methods
    def __le__(self, other: AbstractSet[Any]) -> bool: ...
    def __lt__(self, other: AbstractSet[Any]) -> bool: ...
    def __gt__(self, other: AbstractSet[Any]) -> bool: ...
    def __ge__(self, other: AbstractSet[Any]) -> bool: ...
    def __and__(self, other: AbstractSet[Any]) -> AbstractSet[_T_co]: ...
    def __or__(self, other: AbstractSet[_T]) -> AbstractSet[_T_co | _T]: ...
    def __sub__(self, other: AbstractSet[Any]) -> AbstractSet[_T_co]: ...
    def __xor__(self, other: AbstractSet[_T]) -> AbstractSet[_T_co | _T]: ...
    def isdisjoint(self, other: Iterable[Any]) -> bool: ...

class MutableSet(AbstractSet[_T], Generic[_T]):
    @abstractmethod
    def add(self, value: _T) -> None: ...
    @abstractmethod
    def discard(self, value: _T) -> None: ...
    # Mixin methods
    def clear(self) -> None: ...
    def pop(self) -> _T: ...
    def remove(self, value: _T) -> None: ...
    def __ior__(self: _typeshed.Self, it: AbstractSet[_T]) -> _typeshed.Self: ...  # type: ignore[override,misc]
    def __iand__(self: _typeshed.Self, it: AbstractSet[Any]) -> _typeshed.Self: ...
    def __ixor__(self: _typeshed.Self, it: AbstractSet[_T]) -> _typeshed.Self: ...  # type: ignore[override,misc]
    def __isub__(self: _typeshed.Self, it: AbstractSet[Any]) -> _typeshed.Self: ...

class MappingView(Sized):
    def __init__(self, mapping: Mapping[Any, Any]) -> None: ...  # undocumented
    def __len__(self) -> int: ...

class ItemsView(
    MappingView, AbstractSet[tuple[_KT_co, _VT_co]], Generic[_KT_co, _VT_co]
):
    def __init__(self, mapping: Mapping[_KT_co, _VT_co]) -> None: ...  # undocumented
    def __and__(self, other: Iterable[Any]) -> set[tuple[_KT_co, _VT_co]]: ...
    def __rand__(self, other: Iterable[_T]) -> set[_T]: ...
    def __contains__(self, item: object) -> bool: ...
    def __iter__(self) -> Iterator[tuple[_KT_co, _VT_co]]: ...
    if sys.version_info >= (3, 8):
        def __reversed__(self) -> Iterator[tuple[_KT_co, _VT_co]]: ...

    def __or__(self, other: Iterable[_T]) -> set[tuple[_KT_co, _VT_co] | _T]: ...
    def __ror__(self, other: Iterable[_T]) -> set[tuple[_KT_co, _VT_co] | _T]: ...
    def __sub__(self, other: Iterable[Any]) -> set[tuple[_KT_co, _VT_co]]: ...
    def __rsub__(self, other: Iterable[_T]) -> set[_T]: ...
    def __xor__(self, other: Iterable[_T]) -> set[tuple[_KT_co, _VT_co] | _T]: ...
    def __rxor__(self, other: Iterable[_T]) -> set[tuple[_KT_co, _VT_co] | _T]: ...

class KeysView(MappingView, AbstractSet[_KT_co], Generic[_KT_co]):
    def __init__(self, mapping: Mapping[_KT_co, Any]) -> None: ...  # undocumented
    def __and__(self, other: Iterable[Any]) -> set[_KT_co]: ...
    def __rand__(self, other: Iterable[_T]) -> set[_T]: ...
    def __contains__(self, key: object) -> bool: ...
    def __iter__(self) -> Iterator[_KT_co]: ...
    if sys.version_info >= (3, 8):
        def __reversed__(self) -> Iterator[_KT_co]: ...

    def __or__(self, other: Iterable[_T]) -> set[_KT_co | _T]: ...
    def __ror__(self, other: Iterable[_T]) -> set[_KT_co | _T]: ...
    def __sub__(self, other: Iterable[Any]) -> set[_KT_co]: ...
    def __rsub__(self, other: Iterable[_T]) -> set[_T]: ...
    def __xor__(self, other: Iterable[_T]) -> set[_KT_co | _T]: ...
    def __rxor__(self, other: Iterable[_T]) -> set[_KT_co | _T]: ...

class ValuesView(MappingView, Iterable[_VT_co], Generic[_VT_co]):
    def __init__(self, mapping: Mapping[Any, _VT_co]) -> None: ...  # undocumented
    def __contains__(self, value: object) -> bool: ...
    def __iter__(self) -> Iterator[_VT_co]: ...
    if sys.version_info >= (3, 8):
        def __reversed__(self) -> Iterator[_VT_co]: ...

class Mapping(Collection[_KT], Generic[_KT, _VT_co]):
    # TODO: We wish the key type could also be covariant, but that doesn't work,
    # see discussion in https://github.com/python/typing/pull/273.
    @abstractmethod
    def __getitem__(self, __key: _KT) -> _VT_co: ...
    # Mixin methods
    @overload
    def get(self, __key: _KT) -> _VT_co | None: ...
    @overload
    def get(self, __key: _KT, default: _VT_co | _T) -> _VT_co | _T: ...
    def items(self) -> ItemsView[_KT, _VT_co]: ...
    def keys(self) -> KeysView[_KT]: ...
    def values(self) -> ValuesView[_VT_co]: ...
    def __contains__(self, __o: object) -> bool: ...

class MutableMapping(Mapping[_KT, _VT], Generic[_KT, _VT]):
    @abstractmethod
    def __setitem__(self, __key: _KT, __value: _VT) -> None: ...
    @abstractmethod
    def __delitem__(self, __key: _KT) -> None: ...
    def clear(self) -> None: ...
    @overload
    def pop(self, __key: _KT) -> _VT: ...
    @overload
    def pop(self, __key: _KT, default: _VT | _T) -> _VT | _T: ...
    def popitem(self) -> tuple[_KT, _VT]: ...
    # This overload should be allowed only if the value type is compatible with None.
    # Keep OrderedDict.setdefault in line with MutableMapping.setdefault, modulo positional-only differences.
    @overload
    def setdefault(self: MutableMapping[_KT, _T | None], __key: _KT) -> _T | None: ...
    @overload
    def setdefault(self, __key: _KT, __default: _VT) -> _VT: ...
    # 'update' used to take a Union, but using overloading is better.
    # The second overloaded type here is a bit too general, because
    # Mapping[tuple[_KT, _VT], W] is a subclass of Iterable[tuple[_KT, _VT]],
    # but will always have the behavior of the first overloaded type
    # at runtime, leading to keys of a mix of types _KT and tuple[_KT, _VT].
    # We don't currently have any way of forcing all Mappings to use
    # the first overload, but by using overloading rather than a Union,
    # mypy will commit to using the first overload when the argument is
    # known to be a Mapping with unknown type parameters, which is closer
    # to the behavior we want. See mypy issue  #1430.
    #
    # Various mapping classes have __ior__ methods that should be kept roughly in line with .update():
    # -- dict.__ior__
    # -- os._Environ.__ior__
    # -- collections.UserDict.__ior__
    # -- collections.ChainMap.__ior__
    # -- weakref.WeakValueDictionary.__ior__
    # -- weakref.WeakKeyDictionary.__ior__
    @overload
    def update(self, __m: SupportsKeysAndGetItem[_KT, _VT], **kwargs: _VT) -> None: ...
    @overload
    def update(self, __m: Iterable[tuple[_KT, _VT]], **kwargs: _VT) -> None: ...
    @overload
    def update(self, **kwargs: _VT) -> None: ...

Text = str

TYPE_CHECKING: bool

# In stubs, the arguments of the IO class are marked as positional-only.
# This differs from runtime, but better reflects the fact that in reality
# classes deriving from IO use different names for the arguments.
class IO(Iterator[AnyStr], Generic[AnyStr]):
    # TODO use abstract properties
    @property
    def mode(self) -> str: ...
    @property
    def name(self) -> str: ...
    @abstractmethod
    def close(self) -> None: ...
    @property
    def closed(self) -> bool: ...
    @abstractmethod
    def fileno(self) -> int: ...
    @abstractmethod
    def flush(self) -> None: ...
    @abstractmethod
    def isatty(self) -> bool: ...
    @abstractmethod
    def read(self, __n: int = ...) -> AnyStr: ...
    @abstractmethod
    def readable(self) -> bool: ...
    @abstractmethod
    def readline(self, __limit: int = ...) -> AnyStr: ...
    @abstractmethod
    def readlines(self, __hint: int = ...) -> list[AnyStr]: ...
    @abstractmethod
    def seek(self, __offset: int, __whence: int = ...) -> int: ...
    @abstractmethod
    def seekable(self) -> bool: ...
    @abstractmethod
    def tell(self) -> int: ...
    @abstractmethod
    def truncate(self, __size: int | None = ...) -> int: ...
    @abstractmethod
    def writable(self) -> bool: ...
    @abstractmethod
    def write(self, __s: AnyStr) -> int: ...
    @abstractmethod
    def writelines(self, __lines: Iterable[AnyStr]) -> None: ...
    @abstractmethod
    def __next__(self) -> AnyStr: ...
    @abstractmethod
    def __iter__(self) -> Iterator[AnyStr]: ...
    @abstractmethod
    def __enter__(self) -> IO[AnyStr]: ...
    @abstractmethod
    def __exit__(
        self,
        __t: Type[BaseException] | None,
        __value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> None: ...

class BinaryIO(IO[bytes]):
    @abstractmethod
    def __enter__(self) -> BinaryIO: ...

class TextIO(IO[str]):
    # TODO use abstractproperty
    @property
    def buffer(self) -> BinaryIO: ...
    @property
    def encoding(self) -> str: ...
    @property
    def errors(self) -> str | None: ...
    @property
    def line_buffering(self) -> int: ...  # int on PyPy, bool on CPython
    @property
    def newlines(self) -> Any: ...  # None, str or tuple
    @abstractmethod
    def __enter__(self) -> TextIO: ...

class ByteString(Sequence[int], metaclass=ABCMeta): ...

# Functions

_get_type_hints_obj_allowed_types = (  # noqa: Y026  # TODO: Use TypeAlias once mypy bugs are fixed
    object
    | Callable[..., Any]
    | FunctionType
    | BuiltinFunctionType
    | MethodType
    | ModuleType
    | WrapperDescriptorType
    | MethodWrapperType
    | MethodDescriptorType
)

if sys.version_info >= (3, 9):
    def get_type_hints(
        obj: _get_type_hints_obj_allowed_types,
        globalns: dict[str, Any] | None = ...,
        localns: dict[str, Any] | None = ...,
        include_extras: bool = ...,
    ) -> dict[str, Any]: ...

else:
    def get_type_hints(
        obj: _get_type_hints_obj_allowed_types,
        globalns: dict[str, Any] | None = ...,
        localns: dict[str, Any] | None = ...,
    ) -> dict[str, Any]: ...

if sys.version_info >= (3, 8):
    def get_origin(tp: Any) -> Any | None: ...
    def get_args(tp: Any) -> tuple[Any, ...]: ...

@overload
def cast(typ: Type[_T], val: Any) -> _T: ...
@overload
def cast(typ: str, val: Any) -> Any: ...
@overload
def cast(typ: object, val: Any) -> Any: ...

if sys.version_info >= (3, 11):
    def reveal_type(__obj: _T) -> _T: ...
    def assert_never(__arg: Never) -> Never: ...
    def assert_type(__val: _T, __typ: Any) -> _T: ...
    def clear_overloads() -> None: ...
    def get_overloads(
        func: Callable[..., object]
    ) -> Sequence[Callable[..., object]]: ...
    def dataclass_transform(
        *,
        eq_default: bool = ...,
        order_default: bool = ...,
        kw_only_default: bool = ...,
        field_specifiers: tuple[type[Any] | Callable[..., Any], ...] = ...,
        **kwargs: Any,
    ) -> IdentityFunction: ...

# Type constructors

class NamedTuple(tuple[Any, ...]):
    if sys.version_info < (3, 8):
        _field_types: collections.OrderedDict[str, type]
    elif sys.version_info < (3, 9):
        _field_types: dict[str, type]
    _field_defaults: dict[str, Any]
    _fields: tuple[str, ...]
    _source: str
    @overload
    def __init__(
        self, typename: str, fields: Iterable[tuple[str, Any]] = ...
    ) -> None: ...
    @overload
    def __init__(self, typename: str, fields: None = ..., **kwargs: Any) -> None: ...
    @classmethod
    def _make(cls: Type[_T], iterable: Iterable[Any]) -> _T: ...
    if sys.version_info >= (3, 8):
        def _asdict(self) -> dict[str, Any]: ...
    else:
        def _asdict(self) -> collections.OrderedDict[str, Any]: ...

    def _replace(self: _typeshed.Self, **kwargs: Any) -> _typeshed.Self: ...

# Internal mypy fallback type for all typed dicts (does not exist at runtime)
# N.B. Keep this mostly in sync with typing_extensions._TypedDict/mypy_extensions._TypedDict
@type_check_only
class _TypedDict(Mapping[str, object], metaclass=ABCMeta):
    __total__: ClassVar[bool]
    if sys.version_info >= (3, 9):
        __required_keys__: ClassVar[frozenset[str]]
        __optional_keys__: ClassVar[frozenset[str]]

    def copy(self: _typeshed.Self) -> _typeshed.Self: ...
    # Using Never so that only calls using mypy plugin hook that specialize the signature
    # can go through.
    def setdefault(self, k: _Never, default: object) -> object: ...
    # Mypy plugin hook for 'pop' expects that 'default' has a type variable type.
    def pop(
        self, k: _Never, default: _T = ...
    ) -> object: ...  # pyright: ignore[reportInvalidTypeVarUse]
    def update(self: _T, __m: _T) -> None: ...
    def __delitem__(self, k: _Never) -> None: ...
    def items(self) -> dict_items[str, object]: ...
    def keys(self) -> dict_keys[str, object]: ...
    def values(self) -> dict_values[str, object]: ...
    if sys.version_info >= (3, 9):
        def __or__(self: _typeshed.Self, __value: _typeshed.Self) -> _typeshed.Self: ...
        def __ior__(
            self: _typeshed.Self, __value: _typeshed.Self
        ) -> _typeshed.Self: ...

@_final
class ForwardRef:
    __forward_arg__: str
    __forward_code__: CodeType
    __forward_evaluated__: bool
    __forward_value__: Any | None
    __forward_is_argument__: bool
    __forward_is_class__: bool
    __forward_module__: Any | None
    if sys.version_info >= (3, 9):
        # The module and is_class arguments were added in later Python 3.9 versions.
        def __init__(
            self,
            arg: str,
            is_argument: bool = ...,
            module: Any | None = ...,
            *,
            is_class: bool = ...,
        ) -> None: ...
    else:
        def __init__(self, arg: str, is_argument: bool = ...) -> None: ...

    if sys.version_info >= (3, 9):
        def _evaluate(
            self,
            globalns: dict[str, Any] | None,
            localns: dict[str, Any] | None,
            recursive_guard: frozenset[str],
        ) -> Any | None: ...
    else:
        def _evaluate(
            self, globalns: dict[str, Any] | None, localns: dict[str, Any] | None
        ) -> Any | None: ...

    def __eq__(self, other: object) -> bool: ...
    if sys.version_info >= (3, 11):
        def __or__(self, other: Any) -> _SpecialForm: ...
        def __ror__(self, other: Any) -> _SpecialForm: ...

if sys.version_info >= (3, 10):
    def is_typeddict(tp: object) -> bool: ...

def _type_repr(obj: object) -> str: ...
