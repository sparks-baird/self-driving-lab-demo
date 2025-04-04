# This file is from https://github.com/python/typeshed as of commit sha b6d28acb2368cdd8c87554e01e22e134061997d6
# Copyright github.com/python/typeshed project contributors

import sys
from collections.abc import Iterable, Iterator, Sized
from typing import NoReturn, overload

from _typeshed import ReadableBuffer, Self

ACCESS_DEFAULT: int
ACCESS_READ: int
ACCESS_WRITE: int
ACCESS_COPY: int

ALLOCATIONGRANULARITY: int

if sys.platform == "linux":
    MAP_DENYWRITE: int
    MAP_EXECUTABLE: int
    if sys.version_info >= (3, 10):
        MAP_POPULATE: int

if sys.platform != "win32":
    MAP_ANON: int
    MAP_ANONYMOUS: int
    MAP_PRIVATE: int
    MAP_SHARED: int
    PROT_EXEC: int
    PROT_READ: int
    PROT_WRITE: int

    PAGESIZE: int

class mmap(Iterable[int], Sized):
    if sys.platform == "win32":
        def __init__(
            self,
            fileno: int,
            length: int,
            tagname: str | None = ...,
            access: int = ...,
            offset: int = ...,
        ) -> None: ...
    else:
        def __init__(
            self,
            fileno: int,
            length: int,
            flags: int = ...,
            prot: int = ...,
            access: int = ...,
            offset: int = ...,
        ) -> None: ...

    def close(self) -> None: ...
    if sys.version_info >= (3, 8):
        def flush(self, offset: int = ..., size: int = ...) -> None: ...
    else:
        def flush(self, offset: int = ..., size: int = ...) -> int: ...

    def move(self, dest: int, src: int, count: int) -> None: ...
    def read_byte(self) -> int: ...
    def readline(self) -> bytes: ...
    def resize(self, newsize: int) -> None: ...
    def seek(self, pos: int, whence: int = ...) -> None: ...
    def size(self) -> int: ...
    def tell(self) -> int: ...
    def write_byte(self, byte: int) -> None: ...
    def __len__(self) -> int: ...
    closed: bool
    if sys.version_info >= (3, 8) and sys.platform != "win32":
        def madvise(self, option: int, start: int = ..., length: int = ...) -> None: ...

    def find(self, sub: ReadableBuffer, start: int = ..., stop: int = ...) -> int: ...
    def rfind(self, sub: ReadableBuffer, start: int = ..., stop: int = ...) -> int: ...
    def read(self, n: int | None = ...) -> bytes: ...
    def write(self, bytes: ReadableBuffer) -> int: ...
    @overload
    def __getitem__(self, __index: int) -> int: ...
    @overload
    def __getitem__(self, __index: slice) -> bytes: ...
    def __delitem__(self, __index: int | slice) -> NoReturn: ...
    @overload
    def __setitem__(self, __index: int, __object: int) -> None: ...
    @overload
    def __setitem__(self, __index: slice, __object: ReadableBuffer) -> None: ...
    # Doesn't actually exist, but the object is actually iterable because it has __getitem__ and
    # __len__, so we claim that there is also an __iter__ to help type checkers.
    def __iter__(self) -> Iterator[int]: ...
    def __enter__(self: Self) -> Self: ...
    def __exit__(self, *args: object) -> None: ...

if sys.version_info >= (3, 8) and sys.platform != "win32":
    MADV_NORMAL: int
    MADV_RANDOM: int
    MADV_SEQUENTIAL: int
    MADV_WILLNEED: int
    MADV_DONTNEED: int
    MADV_FREE: int

    if sys.platform == "linux":
        MADV_REMOVE: int
        MADV_DONTFORK: int
        MADV_DOFORK: int
        MADV_HWPOISON: int
        MADV_MERGEABLE: int
        MADV_UNMERGEABLE: int
        # Seems like this constant is not defined in glibc.
        # See https://github.com/python/typeshed/pull/5360 for details
        # MADV_SOFT_OFFLINE: int
        MADV_HUGEPAGE: int
        MADV_NOHUGEPAGE: int
        MADV_DONTDUMP: int
        MADV_DODUMP: int

    # This Values are defined for FreeBSD but type checkers do not support conditions for these
    if sys.platform != "linux" and sys.platform != "darwin":
        MADV_NOSYNC: int
        MADV_AUTOSYNC: int
        MADV_NOCORE: int
        MADV_CORE: int
        MADV_PROTECT: int

if sys.version_info >= (3, 10) and sys.platform == "darwin":
    MADV_FREE_REUSABLE: int
    MADV_FREE_REUSE: int
