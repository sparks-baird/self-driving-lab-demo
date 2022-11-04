from typing import Any

class CancelledError(BaseException):
    pass

class TimeoutError(Exception):
    pass

class SingletonGenerator:
    def __init__(self) -> None:
        pass
    def __iter__(self) -> Any:
        pass
    #   0: return self
    # ? 0: return self
    def __next__(self) -> None:
        pass

def sleep_ms(t: Any, sgen: Any = SingletonGenerator()) -> Any:
    pass

#   0: return sgen
# ? 0: return sgen
def sleep(t: Any) -> Any:
    pass

#   0: return sleep_ms(int(t*))
# ? 0: return sleep_ms(int(t*))
class IOQueue:
    def __init__(self) -> None:
        pass
    def _enqueue(self, s: Any, idx: Any) -> None:
        pass
    def _dequeue(self, s: Any) -> None:
        pass
    def queue_read(self, s: Any) -> None:
        pass
    def queue_write(self, s: Any) -> None:
        pass
    def remove(self, task: Any) -> None:
        pass
    def wait_io_event(self, dt: Any) -> None:
        pass

def _promote_to_task(aw: Any) -> Any:
    pass

def create_task(coro: Any) -> Any:
    pass

#   0: return t
# ? 0: return t
def run_until_complete(main_task: Any) -> Any:
    pass

#   0: return
#   0: return
#   1: return er.value
# ? 1: return er.value
def run(coro: Any) -> Any:
    #   0: return run_until_complete(create_task(coro))
    # ? 0: return run_until_complete(create_task(coro))
    pass

class Loop:
    def create_task(self, coro: Any) -> Any:
        #   0: return create_task(coro)
        # ? 0: return create_task(coro)
        pass
    def run_forever(self) -> None:
        pass
    def run_until_complete(self, aw: Any) -> Any:
        #   0: return run_until_complete(_promote_to_task(aw))
        # ? 0: return run_until_complete(_promote_to_task(aw))
        pass
    def stop(self) -> None:
        pass
    def close(self) -> None:
        pass
    def set_exception_handler(self, handler: Any) -> None:
        pass
    def get_exception_handler(self) -> Any:
        #   0: return Loop._exc_handler
        # ? 0: return Loop._exc_handler
        pass
    def default_exception_handler(self, loop: Any, context: Any) -> None:
        pass
    def call_exception_handler(self, context: Any) -> None:
        pass

def get_event_loop(runq_len: Any, waitq_len: Any) -> Any:
    pass

#   0: return Loop
# ? 0: return Loop
def new_event_loop() -> Any:
    pass

#   0: return Loop
# ? 0: return Loop

class TaskQueue:
    """"""

    def __init__(self):
        pass
    def peek(self) -> Any:
        pass
    def push_sorted(self, v, key):
        pass
    def push_head(self, v):
        pass
    def pop_head(self) -> Any:
        pass
    def remove(self, v):
        pass

def ticks() -> int:
    """
    Returns the uptime of the module in milliseconds.

    :return: The uptime of the module in milliseconds.
    """
    pass

def ticks_add(ticks: int, delta: int) -> int:
    """
    Offsets ticks value by a given number, which can be either positive or
    negative. Given a ticks value, this function allows to calculate ticks
    value delta ticks before or after it, following modular-arithmetic
    definition of tick values (see ``ticks_ms()``).

    This method is useful for calculating deadlines for events/tasks.

    **Note**: You must use ``ticks_diff()`` function to work with deadlines.

    :param ticks: Number obtained from a direct result of call to
        ``ticks_ms()``, ``ticks_us()``, or ``ticks_cpu()`` functions (or from
        previous call to ``ticks_add()``)
    :param delta: Arbitrary integer number or numeric expression.

    :return: Returns the result of the add operation.
    """
    pass

def ticks_diff(ticks1: int, ticks2: int) -> int:
    """
    Measures the period (ticks) difference between values returned from
    ``ticks_ms()``, ``ticks_us()``, or ``ticks_cpu()`` functions, as a signed
    value which may wrap around, so directly subtracting them is not supported.

    The argument order is the same as for subtraction operator,
    ``ticks_diff(ticks1, ticks2)`` has the same meaning as ``ticks1 - ticks2``.

    :param ticks1: Ticks that precede in time the value of ``ticks2``.
    :param ticks2: Second (newer) ticks value.

    :return: The difference between the given ticks values.
    """
    pass
