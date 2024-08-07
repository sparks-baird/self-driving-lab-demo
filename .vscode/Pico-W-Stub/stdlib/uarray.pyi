import sys
from collections.abc import Iterable, MutableSequence
from typing import Generic, TypeVar, overload

_IntTypeCode = ["b", "B", "h", "H", "i", "I", "l", "L", "q", "Q"]
_FloatTypeCode = ["f", "d"]
_UnicodeTypeCode = ["u"]
_TypeCode = _IntTypeCode | _FloatTypeCode | _UnicodeTypeCode

_T = TypeVar("_T", int, float, str)

if sys.version_info.major >= 3:
    typecodes: str

class array(MutableSequence[_T], Generic[_T]):
    typecode: _TypeCode
    itemsize: int
    def __init__(
        self: any,
        typecode: str | _IntTypeCode | _FloatTypeCode | _UnicodeTypeCode,
        __initializer: bytes | Iterable[_T] = ...,
    ) -> None: ...
    def append(self, __v: _T) -> None: ...
    def extend(self, __bb: Iterable[_T]) -> None: ...
    def __len__(self) -> int: ...
    @overload
    def __getitem__(self, i: int) -> _T: ...
    @overload
    def __getitem__(self, s: slice) -> array[_T]: ...
    @overload  # type: ignore  # Overrides MutableSequence
    def __setitem__(self, i: int, o: _T) -> None: ...
    @overload
    def __setitem__(self, s: slice, o: array[_T]) -> None: ...
    def __delitem__(self, i: int | slice) -> None: ...
    def __add__(self, x: array[_T]) -> array[_T]: ...
    def __ge__(self, other: array[_T]) -> bool: ...
    def __gt__(self, other: array[_T]) -> bool: ...
    def __iadd__(self, x: array[_T]) -> array[_T]: ...  # type: ignore  # Overrides MutableSequence
    def __imul__(self, n: int) -> array[_T]: ...
    def __le__(self, other: array[_T]) -> bool: ...
    def __lt__(self, other: array[_T]) -> bool: ...
    def __mul__(self, n: int) -> array[_T]: ...
    def __rmul__(self, n: int) -> array[_T]: ...

    if sys.version_info.major < 3:
        def __delslice__(self, i: int, j: int) -> None: ...
        def __getslice__(self, i: int, j: int) -> array[_T]: ...
        def __setslice__(self, i: int, j: int, y: array[_T]) -> None: ...

ArrayType = array
