# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`analogio` - Analog input and output control
============================================
See `CircuitPython:analogio` in CircuitPython for more details.
Not supported by all boards.

* Author(s): Carter Nelson, Melissa LeBlanc-Williams
"""

import sys

from adafruit_blinka.agnostic import detector

# pylint: disable=ungrouped-imports,wrong-import-position,unused-import

if detector.board.microchip_mcp2221:
    pass
elif detector.board.greatfet_one:
    pass
elif detector.chip.RK3308:
    pass
elif detector.chip.RK3399:
    pass
elif detector.chip.IMX6ULL:
    pass
elif detector.chip.STM32MP157:
    pass
elif "sphinx" in sys.modules:
    pass
elif detector.board.pico_u2if:
    pass
elif detector.board.feather_u2if:
    pass
elif detector.board.qtpy_u2if:
    pass
elif detector.board.itsybitsy_u2if:
    pass
else:
    raise NotImplementedError("analogio not supported for this board.")
