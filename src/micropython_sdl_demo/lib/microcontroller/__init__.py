# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`microcontroller` - Pin references and cpu functionality
========================================================

* Author(s): Melissa LeBlanc-Williams
"""

import sys
import time

from adafruit_blinka.agnostic import board_id, chip_id
from adafruit_platformdetect.constants import chips as ap_chip
from microcontroller import pin  # pylint: disable=unused-import
from microcontroller.pin import Pin  # pylint: disable=unused-import


def delay_us(delay):
    """Sleep for delay usecs."""
    time.sleep(delay / 1e6)


# We intentionally are patching into this namespace so skip the wildcard check.
# pylint: disable=unused-wildcard-import,wildcard-import,ungrouped-imports

if chip_id == ap_chip.ESP8266:
    pass
elif chip_id == ap_chip.STM32F405:
    pass
elif chip_id == ap_chip.RP2040:
    pass
elif chip_id == ap_chip.BCM2XXX:
    if board_id in [
        "RASPBERRY_PI_4B",
        "RASPBERRY_PI_400",
        "RASPBERRY_PI_CM4",
    ]:
        pass
    else:
        pass
elif chip_id == ap_chip.DRA74X:
    pass
elif chip_id == ap_chip.AM33XX:
    pass
elif chip_id == ap_chip.JH71x0:
    pass
elif chip_id == ap_chip.SUN8I:
    pass
elif chip_id == ap_chip.H5:
    pass
elif chip_id == ap_chip.H6:
    pass
elif chip_id == ap_chip.H616:
    pass
elif chip_id == ap_chip.SAMA5:
    pass
elif chip_id == ap_chip.T210:
    pass
elif chip_id == ap_chip.T186:
    pass
elif chip_id == ap_chip.T194:
    pass
elif chip_id == ap_chip.T234:
    pass
elif chip_id == ap_chip.S905:
    pass
elif chip_id == ap_chip.S905X3:
    pass
elif chip_id == ap_chip.S905Y2:
    pass
elif chip_id == ap_chip.S922X:
    pass
elif chip_id == ap_chip.A311D:
    pass
elif chip_id == ap_chip.EXYNOS5422:
    pass
elif chip_id == ap_chip.APQ8016:
    pass
elif chip_id == ap_chip.A64:
    pass
elif chip_id == ap_chip.A33:
    pass
elif chip_id == ap_chip.RK3308:
    pass
elif chip_id == ap_chip.RK3399:
    pass
elif chip_id == ap_chip.RK3328:
    pass
elif chip_id == ap_chip.H3:
    pass
elif chip_id == ap_chip.H5:
    pass
elif chip_id == ap_chip.IMX8MX:
    pass
elif chip_id == ap_chip.IMX6ULL:
    pass
elif chip_id == ap_chip.HFU540:
    pass
elif chip_id == ap_chip.BINHO:
    pass
elif chip_id == ap_chip.LPC4330:
    pass
elif chip_id == ap_chip.MCP2221:
    pass
elif chip_id == ap_chip.MIPS24KC:
    pass
elif chip_id == ap_chip.MIPS24KEC:
    pass
elif chip_id == ap_chip.FT232H:
    pass
elif chip_id == ap_chip.FT2232H:
    pass
elif chip_id == ap_chip.PENTIUM_N3710:
    pass
elif chip_id == ap_chip.STM32MP157:
    pass
elif chip_id == ap_chip.MT8167:
    pass
elif chip_id == ap_chip.RP2040_U2IF:
    pass
elif chip_id == ap_chip.GENERIC_X86:
    print("WARNING: GENERIC_X86 is not fully supported. Some features may not work.")
elif chip_id is None:
    print(
        "WARNING: chip_id == None is not fully supported. Some features may not work."
    )
elif "sphinx" in sys.modules:
    pass
else:
    raise NotImplementedError("Microcontroller not supported:", chip_id)
