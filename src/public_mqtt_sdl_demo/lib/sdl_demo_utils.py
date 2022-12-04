import sys
from time import sleep

from uio import StringIO


def beep(buzzer, power=0.005):
    buzzer.freq(300)
    buzzer.duty_u16(round(65535 * power))
    sleep(0.15)
    buzzer.duty_u16(0)


def get_traceback(err):
    try:
        with StringIO() as f:  # type: ignore
            sys.print_exception(err, f)
            return f.getvalue()
    except Exception as err2:
        print(err2)
        return f"Failed to extract file and line number due to {err2}.\nOriginal error: {err}"  # noqa: E501


def merge_two_dicts(x, y):
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z
