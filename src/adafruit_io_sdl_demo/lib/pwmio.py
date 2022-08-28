# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`pwmio` - Support for PWM based protocols
===========================================================
See `CircuitPython:pwmio` in CircuitPython for more details.
Not supported by all boards.

* Author(s): Melissa LeBlanc-Williams
"""

import sys

from adafruit_blinka.agnostic import detector

# pylint: disable=unused-import

if detector.board.any_raspberry_pi:
    pass
elif detector.board.any_coral_board:
    pass
elif detector.board.any_giant_board:
    pass
elif detector.board.any_beaglebone:
    pass
elif detector.board.any_rock_pi_board:
    pass
elif detector.board.binho_nova:
    pass
elif detector.board.greatfet_one:
    pass
elif detector.board.any_lubancat:
    pass
elif detector.board.pico_u2if:
    pass
elif (
    detector.board.feather_u2if
    or detector.board.qtpy_u2if
    or detector.board.itsybitsy_u2if
    or detector.board.macropad_u2if
    or detector.board.qt2040_trinkey_u2if
):
    pass
elif "sphinx" in sys.modules:
    pass
else:
    raise NotImplementedError("pwmio not supported for this board.")
