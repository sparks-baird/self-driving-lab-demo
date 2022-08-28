# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_as7341`
================================================================================

CircuitPython library for use with the Adafruit AS7341 breakout


* Author(s): Bryan Siepert

Implementation Notes
--------------------

**Hardware:**

* `Adafruit AS7341 Breakout
  <https://www.adafruit.com/product/4698>`_ (Product ID: 4698)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

* Adafruit's Register library:
  https://github.com/adafruit/Adafruit_CircuitPython_Register

"""

__version__ = "1.2.11"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_AS7341.git"

from time import monotonic, sleep

from adafruit_bus_device import i2c_device
from adafruit_register.i2c_bit import RWBit
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_struct import Struct, UnaryStruct  # , ROUnaryStruct
from micropython import const

try:
    from typing import Any, Callable, Optional, Tuple, TypeVar

    # Only needed for typing
    import busio  # pylint: disable=unused-import

    TCallable = TypeVar("TCallable", bound=Callable[..., Any])

except ImportError:
    pass

# Correct content of WHO_AM_I register
_AS7341_DEVICE_ID: int = const(0b001001)
_AS7341_I2CADDR_DEFAULT: int = const(0x39)  # AS7341 default i2c address
_AS7341_CHIP_ID: int = const(0x09)  # AS7341 default device id from WHOAMI
_AS7341_WHOAMI: int = const(0x92)  # Chip ID register
# Enables LED control and sets light sensing mode
_AS7341_CONFIG: int = const(0x70)
_AS7341_GPIO: int = const(0x73)  # Connects photo diode to GPIO or INT pins
_AS7341_LED: int = const(0x74)  # LED Register; Enables and sets current limit
_AS7341_ENABLE: int = const(
    0x80
)  # Main enable register. Controls SMUX, Flicker Detection,Spectral and
# Power
_AS7341_ATIME: int = const(0x81)  # Sets ADC integration step count
# Spectral measurement Low Threshold low byte
_AS7341_SP_LOW_TH_L: int = const(0x84)
# 0 Spectral measurement Low Threshold high byte
_AS7341_SP_LOW_TH_H: int = const(0x85)
# Spectral measurement High Threshold low byte
_AS7341_SP_HIGH_TH_L: int = const(0x86)
# Spectral measurement High Threshold low byte
_AS7341_SP_HIGH_TH_H: int = const(0x87)
_AS7341_STATUS: int = const(
    0x93
)  # Interrupt status registers. Indicates the occourance of an interrupt
_AS7341_ASTATUS: int = const(
    0x94
)  # Spectral Saturation and Gain status. Reading from here latches the data
_AS7341_CH0_DATA_L: int = const(0x95)  # ADC Channel 0 Data
_AS7341_CH0_DATA_H: int = const(0x96)  # ADC Channel 0 Data
_AS7341_CH1_DATA_L: int = const(0x97)  # ADC Channel 1 Data
_AS7341_CH1_DATA_H: int = const(0x98)  # ADC Channel 1 Data
_AS7341_CH2_DATA_L: int = const(0x99)  # ADC Channel 2 Data
_AS7341_CH2_DATA_H: int = const(0x9A)  # ADC Channel 2 Data
_AS7341_CH3_DATA_L: int = const(0x9B)  # ADC Channel 3 Data
_AS7341_CH3_DATA_H: int = const(0x9C)  # ADC Channel 3 Data
_AS7341_CH4_DATA_L: int = const(0x9D)  # ADC Channel 4 Data
_AS7341_CH4_DATA_H: int = const(0x9E)  # ADC Channel 4 Data
_AS7341_CH5_DATA_L: int = const(0x9F)  # ADC Channel 5 Data
_AS7341_CH5_DATA_H: int = const(0xA0)  # ADC Channel 5 Data
_AS7341_STATUS2: int = const(0xA3)  # Measurement status flags; saturation, validity
_AS7341_STATUS3: int = const(0xA4)  # Spectral interrupt source, high or low threshold
_AS7341_CFG0: int = const(
    0xA9
)  # Sets Low power mode, Register bank, and Trigger lengthening
_AS7341_CFG1: int = const(0xAA)  # Controls ADC Gain
_AS7341_CFG6: int = const(0xAF)  # Used to configure Smux
_AS7341_CFG9: int = const(0xB2)  # flicker detect and SMUX command system ints
_AS7341_CFG12: int = const(
    0xB5
)  # ADC channel for interrupts, persistence and auto-gain
_AS7341_PERS = const(
    0xBD
)  # number of measurements outside thresholds to trigger an interrupt
_AS7341_GPIO2 = const(
    0xBE
)  # GPIO Settings and status: polarity, direction, sets output, reads
_AS7341_ASTEP_L: int = const(0xCA)  # Integration step size ow byte
_AS7341_ASTEP_H: int = const(0xCB)  # Integration step size high byte
_AS7341_FD_TIME1: int = const(0xD8)  # Flicker detection integration time low byte
_AS7341_FD_TIME2: int = const(0xDA)  # Flicker detection gain and high nibble
_AS7341_FD_STATUS: int = const(
    0xDB
)  # Flicker detection status; measurement valid, saturation, flicker
_AS7341_INTENAB: int = const(0xF9)  # Enables individual interrupt types
_AS7341_CONTROL: int = const(0xFA)  # Auto-zero, fifo clear, clear SAI active
_AS7341_FD_CFG0: int = const(0xD7)  # Enables FIFO for flicker detection


def _low_bank(func: Any) -> Any:
    # pylint:disable=protected-access
    def _decorator(self, *args, **kwargs) -> Any:
        self._low_bank_active = True
        retval = func(self, *args, **kwargs)
        self._low_bank_active = False
        return retval

    return _decorator


class CV:
    """struct helper"""

    @classmethod
    def add_values(
        cls,
        value_tuples: Tuple[str, int, int, Optional[float]],
    ) -> None:
        """Add CV values to the class"""
        cls.string = {}
        cls.lsb = {}

        for value_tuple in value_tuples:
            name, value, string, lsb = value_tuple
            setattr(cls, name, value)
            cls.string[value] = string
            cls.lsb[value] = lsb

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validate that a given value is a member"""
        return value in cls.string


# class Flicker(CV):
#     """Options for ``flicker_detection_type``"""

#     pass  # pylint: disable=unnecessary-pass


# Flicker.add_values((("FLICKER_100HZ", 0, 100, None), ("FLICKER_1000HZ", 1, 1000, None)))


class Gain(CV):
    """Options for ``accelerometer_range``

    +-------------------------------+-------------------------+
    | Setting                       | Gain Value              |
    +===============================+=========================+
    | :py:const:`Gain.GAIN_0_5X`    | 0.5                     |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_1X`      | 1                       |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_2X`      | 2                       |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_4X`      | 4                       |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_8X`      | 8                       |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_16X`     | 16                      |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_32X`     | 32                      |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_64X`     | 64                      |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_128X`    | 128                     |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_256X`    | 256                     |
    +-------------------------------+-------------------------+
    | :py:const:`Gain.GAIN_512X`    | 512                     |
    +-------------------------------+-------------------------+

    """


Gain.add_values(
    (
        ("GAIN_0_5X", 0, 0.5, None),
        ("GAIN_1X", 1, 1, None),
        ("GAIN_2X", 2, 2, None),
        ("GAIN_4X", 3, 4, None),
        ("GAIN_8X", 4, 8, None),
        ("GAIN_16X", 5, 16, None),
        ("GAIN_32X", 6, 32, None),
        ("GAIN_64X", 7, 64, None),
        ("GAIN_128X", 8, 128, None),
        ("GAIN_256X", 9, 256, None),
        ("GAIN_512X", 10, 512, None),
    )
)


class SMUX_OUT(CV):
    """Options for ``smux_out``"""


SMUX_OUT.add_values(
    (
        ("DISABLED", 0, 0, None),
        ("ADC0", 1, 1, None),
        ("ADC1", 2, 2, None),
        ("ADC2", 3, 3, None),
        ("ADC3", 4, 4, None),
        ("ADC4", 5, 5, None),
        ("ADC5", 6, 6, None),
    )
)


class SMUX_IN(CV):
    """Options for ``smux_in``"""


SMUX_IN.add_values(
    (
        ("NC_F3L", 0, 0, None),
        ("F1L_NC", 1, 1, None),
        ("NC_NC0", 2, 2, None),
        ("NC_F8L", 3, 3, None),
        ("F6L_NC", 4, 4, None),
        ("F2L_F4L", 5, 5, None),
        ("NC_F5L", 6, 6, None),
        ("F7L_NC", 7, 7, None),
        ("NC_CL", 8, 8, None),
        ("NC_F5R", 9, 9, None),
        ("F7R_NC", 10, 10, None),
        ("NC_NC1", 11, 11, None),
        ("NC_F2R", 12, 12, None),
        ("F4R_NC", 13, 13, None),
        ("F8R_F6R", 14, 14, None),
        ("NC_F3R", 15, 15, None),
        ("F1R_EXT_GPIO", 16, 16, None),
        ("EXT_INT_CR", 17, 17, None),
        ("NC_DARK", 18, 18, None),
        ("NIR_F", 19, 19, None),
    )
)


class AS7341:  # pylint:disable=too-many-instance-attributes, no-member
    """Library for the AS7341 Sensor

    :param ~busio.I2C i2c_bus: The I2C bus the device is connected to
    :param int address: The I2C device address. Defaults to :const:`0x39`


    **Quickstart: Importing and using the device**

        Here is an example of using the :class:`AS7341`.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            from adafruit_as7341 import AS7341

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            sensor = AS7341(i2c)

        Now you have access to the different channels

        .. code-block:: python

            channel_415nm = sensor.channel_415nm
            channel_445nm = sensor.channel_445nm
            channel_480nm = sensor.channel_480nm
            channel_515nm = sensor.channel_515nm
            channel_555nm = sensor.channel_555nm
            channel_590nm = sensor.channel_590nm
            channel_630nm = sensor.channel_630nm
            channel_680nm = sensor.channel_680nm

    """

    _device_id: ROBits = ROBits(6, _AS7341_WHOAMI, 2)

    _smux_enable_bit: RWBit = RWBit(_AS7341_ENABLE, 4)
    _led_control_enable_bit: RWBit = RWBit(_AS7341_CONFIG, 3)
    _color_meas_enabled: RWBit = RWBit(_AS7341_ENABLE, 1)
    _power_enabled: RWBit = RWBit(_AS7341_ENABLE, 0)

    _low_bank_active: RWBit = RWBit(_AS7341_CFG0, 4)
    _smux_command: RWBits = RWBits(2, _AS7341_CFG6, 3)
    _fd_status: UnaryStruct = UnaryStruct(_AS7341_FD_STATUS, "<B")

    _channel_0_data: UnaryStruct = UnaryStruct(_AS7341_CH0_DATA_L, "<H")
    _channel_1_data: UnaryStruct = UnaryStruct(_AS7341_CH1_DATA_L, "<H")
    _channel_2_data: UnaryStruct = UnaryStruct(_AS7341_CH2_DATA_L, "<H")
    _channel_3_data: UnaryStruct = UnaryStruct(_AS7341_CH3_DATA_L, "<H")
    _channel_4_data: UnaryStruct = UnaryStruct(_AS7341_CH4_DATA_L, "<H")
    _channel_5_data: UnaryStruct = UnaryStruct(_AS7341_CH5_DATA_L, "<H")

    # "Reading the ASTATUS register (0x60 or 0x94) latches
    # all 12 spectral data bytes to that status read." Datasheet Sec. 10.2.7
    _all_channels: Struct = Struct(_AS7341_ASTATUS, "<BHHHHHH")
    _led_current_bits: RWBits = RWBits(7, _AS7341_LED, 0)
    _led_enabled = RWBit(_AS7341_LED, 7)

    atime: UnaryStruct = UnaryStruct(_AS7341_ATIME, "<B")
    """The integration time step count.
    Total integration time will be ``(ATIME + 1) * (ASTEP + 1) * 2.78µS``

    :rtype: int
    """

    astep: UnaryStruct = UnaryStruct(_AS7341_ASTEP_L, "<H")
    """The integration time step size in 2.78 microsecond increments

    :rtype: int
    """

    _gain: UnaryStruct = UnaryStruct(_AS7341_CFG1, "<B")
    _data_ready_bit: RWBit = RWBit(_AS7341_STATUS2, 6)
    """
 * @brief
 *
 * @return true: success false: failure
    """

    def __init__(
        self, i2c_bus: busio.I2C, address: int = _AS7341_I2CADDR_DEFAULT
    ) -> None:

        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)
        if not self._device_id in [_AS7341_DEVICE_ID]:
            raise RuntimeError("Failed to find an AS7341 sensor - check your wiring!")
        self.initialize()
        self._buffer = bytearray(2)
        self._low_channels_configured = False
        self._high_channels_configured = False
        self._flicker_detection_1k_configured = False

    def initialize(self) -> None:
        """Configure the sensors with the default settings"""

        self._power_enabled = True
        self._led_control_enabled = True
        self.atime = 100
        self.astep = 999
        self.gain = Gain.GAIN_128X  # pylint:disable=no-member

    @property
    def all_channels(self) -> Tuple[int, ...]:
        """The current readings for all six ADC channels"""

        self._configure_f1_f4()
        adc_reads_f1_f4 = self._all_channels
        reads = adc_reads_f1_f4[1:-2]

        self._configure_f5_f8()
        adc_reads_f5_f8 = self._all_channels
        reads += adc_reads_f5_f8[1:-2]

        return reads

    @property
    def channel_415nm(self) -> int:
        """The current reading for the 415nm band"""
        self._configure_f1_f4()
        return self._channel_0_data

    @property
    def channel_445nm(self) -> int:
        """The current reading for the 445nm band"""
        self._configure_f1_f4()
        return self._channel_1_data

    @property
    def channel_480nm(self) -> int:
        """The current reading for the 480nm band"""
        self._configure_f1_f4()
        return self._channel_2_data

    @property
    def channel_515nm(self) -> int:
        """The current reading for the 515nm band"""
        self._configure_f1_f4()
        return self._channel_3_data

    @property
    def channel_555nm(self) -> int:
        """The current reading for the 555nm band"""
        self._configure_f5_f8()
        return self._channel_0_data

    @property
    def channel_590nm(self) -> int:
        """The current reading for the 590nm band"""
        self._configure_f5_f8()
        return self._channel_1_data

    @property
    def channel_630nm(self) -> int:
        """The current reading for the 630nm band"""
        self._configure_f5_f8()
        return self._channel_2_data

    @property
    def channel_680nm(self) -> int:
        """The current reading for the 680nm band"""
        self._configure_f5_f8()
        return self._channel_3_data

    @property
    def channel_clear(self) -> int:
        """The current reading for the clear sensor"""
        self._configure_f5_f8()
        return self._channel_4_data

    @property
    def channel_nir(self) -> int:
        """The current reading for the NIR (near-IR) sensor"""
        self._configure_f5_f8()
        return self._channel_5_data

    def _wait_for_data(self, timeout: float = 1.0) -> None:
        """Wait for sensor data to be ready"""
        start = monotonic()
        while not self._data_ready_bit:
            if monotonic() - start > timeout:
                raise RuntimeError("Timeout occurred waiting for sensor data")
            sleep(0.001)

    def _write_register(self, addr: int, data: int) -> None:

        self._buffer[0] = addr
        self._buffer[1] = data

        with self.i2c_device as i2c:
            i2c.write(self._buffer)

    def _configure_f1_f4(self) -> None:
        """Configure the sensor to read from elements F1-F4, Clear, and NIR"""
        # disable SP_EN bit while  making config changes
        if self._low_channels_configured:
            return
        self._high_channels_configured = False
        self._flicker_detection_1k_configured = False

        self._color_meas_enabled = False

        # ENUM-ify
        self._smux_command = 2
        # Write new configuration to all the 20 registers

        self._f1f4_clear_nir()
        # Start SMUX command
        self._smux_enabled = True

        # Enable SP_EN bit
        self._color_meas_enabled = True
        self._low_channels_configured = True
        self._wait_for_data()

    def _configure_f5_f8(self) -> None:
        """Configure the sensor to read from elements F5-F8, Clear, and NIR"""
        # disable SP_EN bit while  making config changes
        if self._high_channels_configured:
            return

        self._low_channels_configured = False
        self._flicker_detection_1k_configured = False

        self._color_meas_enabled = False

        # ENUM-ify
        self._smux_command = 2
        # Write new configuration to all the 20 registers

        self._f5f8_clear_nir()
        # Start SMUX command
        self._smux_enabled = True

        # Enable SP_EN bit
        self._color_meas_enabled = True
        self._high_channels_configured = True
        self._wait_for_data()

    @property
    def flicker_detected(self) -> Optional[int]:
        """The flicker frequency detected in Hertz"""
        if not self._flicker_detection_1k_configured:
            AttributeError(
                "Flicker detection must be enabled to access `flicker_detected`"
            )
        flicker_status = self._fd_status

        if flicker_status == 45:
            return 1000
        if flicker_status == 46:
            return 1200
        return None
        # if we haven't returned yet either there was an error or an unknown frequency was detected

    @property
    def flicker_detection_enabled(self) -> bool:
        """The flicker detection status of the sensor. True if the sensor is configured\
            to detect flickers. Currently only 1000Hz and 1200Hz flicker detection is supported
        """
        return self._flicker_detection_1k_configured

    @flicker_detection_enabled.setter
    def flicker_detection_enabled(self, flicker_enable: bool) -> None:
        if flicker_enable:
            self._configure_1k_flicker_detection()
        else:
            self._configure_f1_f4()  # sane default

    def _f1f4_clear_nir(self) -> None:
        """Configure SMUX for sensors F1-F4, Clear and NIR"""
        self._set_smux(SMUX_IN.NC_F3L, SMUX_OUT.DISABLED, SMUX_OUT.ADC2)
        self._set_smux(SMUX_IN.F1L_NC, SMUX_OUT.ADC0, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC0, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F8L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F6L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F2L_F4L, SMUX_OUT.ADC1, SMUX_OUT.ADC3)
        self._set_smux(SMUX_IN.NC_F5L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F7L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_CL, SMUX_OUT.DISABLED, SMUX_OUT.ADC4)
        self._set_smux(SMUX_IN.NC_F5R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F7R_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC1, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F2R, SMUX_OUT.DISABLED, SMUX_OUT.ADC1)
        self._set_smux(SMUX_IN.F4R_NC, SMUX_OUT.ADC3, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F8R_F6R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F3R, SMUX_OUT.DISABLED, SMUX_OUT.ADC2)
        self._set_smux(SMUX_IN.F1R_EXT_GPIO, SMUX_OUT.ADC0, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.EXT_INT_CR, SMUX_OUT.DISABLED, SMUX_OUT.ADC4)
        self._set_smux(SMUX_IN.NC_DARK, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NIR_F, SMUX_OUT.ADC5, SMUX_OUT.DISABLED)

    def _f5f8_clear_nir(self) -> None:
        # SMUX Config for F5,F6,F7,F8,NIR,Clear
        self._set_smux(SMUX_IN.NC_F3L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F1L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC0, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F8L, SMUX_OUT.DISABLED, SMUX_OUT.ADC3)
        self._set_smux(SMUX_IN.F6L_NC, SMUX_OUT.ADC1, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F2L_F4L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F5L, SMUX_OUT.DISABLED, SMUX_OUT.ADC0)
        self._set_smux(SMUX_IN.F7L_NC, SMUX_OUT.ADC2, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_CL, SMUX_OUT.DISABLED, SMUX_OUT.ADC4)
        self._set_smux(SMUX_IN.NC_F5R, SMUX_OUT.DISABLED, SMUX_OUT.ADC0)
        self._set_smux(SMUX_IN.F7R_NC, SMUX_OUT.ADC2, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC1, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F2R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F4R_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F8R_F6R, SMUX_OUT.ADC3, SMUX_OUT.ADC1)
        self._set_smux(SMUX_IN.NC_F3R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F1R_EXT_GPIO, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.EXT_INT_CR, SMUX_OUT.DISABLED, SMUX_OUT.ADC4)
        self._set_smux(SMUX_IN.NC_DARK, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NIR_F, SMUX_OUT.ADC5, SMUX_OUT.DISABLED)

    # TODO: Convert as much of this as possible to properties or named attributes
    def _configure_1k_flicker_detection(self) -> None:
        self._low_channels_configured = False
        self._high_channels_configured = False

        # RAM_BANK 0 select which RAM bank to access in register addresses 0x00-0x7f
        self._write_register(_AS7341_CFG0, 0x00)

        # The coefficient calculated are stored into the RAM bank 0 and RAM bank 1,
        # they are used instead of 100Hz and 120Hz coefficients which are the default
        # flicker detection coefficients
        # write new coefficients to detect the 1000Hz and 1200Hz - part 1
        self._write_register(0x04, 0x9E)
        self._write_register(0x05, 0x36)
        self._write_register(0x0E, 0x2E)
        self._write_register(0x0F, 0x1B)
        self._write_register(0x18, 0x7D)
        self._write_register(0x19, 0x36)
        self._write_register(0x22, 0x09)
        self._write_register(0x23, 0x1B)
        self._write_register(0x2C, 0x5B)
        self._write_register(0x2D, 0x36)
        self._write_register(0x36, 0xE5)
        self._write_register(0x37, 0x1A)
        self._write_register(0x40, 0x3A)
        self._write_register(0x41, 0x36)
        self._write_register(0x4A, 0xC1)
        self._write_register(0x4B, 0x1A)
        self._write_register(0x54, 0x18)
        self._write_register(0x55, 0x36)
        self._write_register(0x5E, 0x9C)
        self._write_register(0x5F, 0x1A)
        self._write_register(0x68, 0xF6)
        self._write_register(0x69, 0x35)
        self._write_register(0x72, 0x78)
        self._write_register(0x73, 0x1A)
        self._write_register(0x7C, 0x4D)
        self._write_register(0x7D, 0x35)

        # RAM_BANK 1 select which RAM bank to access in register addresses 0x00-0x7f
        self._write_register(_AS7341_CFG0, 0x01)

        # write new coefficients to detect the 1000Hz and 1200Hz - part 1
        self._write_register(0x06, 0x54)
        self._write_register(0x07, 0x1A)
        self._write_register(0x10, 0xB3)
        self._write_register(0x11, 0x35)
        self._write_register(0x1A, 0x2F)
        self._write_register(0x1B, 0x1A)

        self._write_register(_AS7341_CFG0, 0x01)

        # select RAM coefficients for flicker detection by setting
        # fd_disable_constant_init to „1“ (FD_CFG0 register) in FD_CFG0 register -
        # 0xD7
        # fd_disable_constant_init=1
        # fd_samples=4
        self._write_register(_AS7341_FD_CFG0, 0x60)

        # in FD_CFG1 register - 0xd8 fd_time(7:0) = 0x40
        self._write_register(_AS7341_FD_TIME1, 0x40)

        # in FD_CFG2 register - 0xd9  fd_dcr_filter_size=1 fd_nr_data_sets(2:0)=5
        self._write_register(0xD9, 0x25)

        # in FD_CFG3 register - 0xda fd_gain=9
        self._write_register(_AS7341_FD_TIME2, 0x48)

        # in CFG9 register - 0xb2 sien_fd=1
        self._write_register(_AS7341_CFG9, 0x40)

        # in ENABLE - 0x80  fden=1 and pon=1 are enabled
        self._write_register(_AS7341_ENABLE, 0x41)

        self._flicker_detection_1k_configured = True

    def _smux_template(self) -> None:
        # SMUX_OUT.DISABLED
        # SMUX_OUT.ADC0
        # SMUX_OUT.ADC1
        # SMUX_OUT.ADC2
        # SMUX_OUT.ADC3
        # SMUX_OUT.ADC4
        # SMUX_OUT.ADC5
        self._set_smux(SMUX_IN.NC_F3L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F1L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC0, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F8L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F6L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F2L_F4L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F5L, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F7L_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_CL, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F5R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F7R_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_NC1, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F2R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F4R_NC, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F8R_F6R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_F3R, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.F1R_EXT_GPIO, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.EXT_INT_CR, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NC_DARK, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)
        self._set_smux(SMUX_IN.NIR_F, SMUX_OUT.DISABLED, SMUX_OUT.DISABLED)

    def _set_smux(self, smux_addr: int, smux_out1: int, smux_out2: int) -> None:
        """Connect a pair of sensors to an ADC channel"""
        low_nibble = smux_out1
        high_nibble = smux_out2 << 4
        smux_byte = high_nibble | low_nibble
        self._write_register(smux_addr, smux_byte)

    @property
    def gain(self) -> int:
        """The ADC gain multiplier. Must be a valid :meth:`adafruit_as7341.Gain`"""
        return self._gain

    @gain.setter
    def gain(self, gain_value: str) -> None:
        if not Gain.is_valid(gain_value):
            raise AttributeError("`gain` must be a valid `adafruit_as7341.Gain`")
        self._gain = gain_value

    @property
    def _smux_enabled(self) -> bool:
        return self._smux_enable_bit

    @_smux_enabled.setter
    def _smux_enabled(self, enable_smux: bool):
        self._low_bank_active = False
        self._smux_enable_bit = enable_smux
        while self._smux_enable_bit is True:
            sleep(0.001)

    @property
    @_low_bank
    def led_current(self) -> int:
        """The maximum allowed current through the attached LED in milliamps.
        Odd numbered values will be rounded down to the next lowest even number due
        to the internal configuration restrictions"""
        current_val = self._led_current_bits
        return (current_val * 2) + 4

    @led_current.setter
    @_low_bank
    def led_current(self, led_current: int) -> None:
        new_current = int((min(258, max(4, led_current)) - 4) / 2)
        self._led_current_bits = new_current

    @property
    @_low_bank
    def led(self) -> bool:
        """The  attached LED. Set to True to turn on, False to turn off"""
        return self._led_enabled

    @led.setter
    @_low_bank
    def led(self, led_on: bool) -> None:
        self._led_enabled = led_on

    @property
    @_low_bank
    def _led_control_enabled(self) -> bool:
        return self._led_control_enable_bit

    @_led_control_enabled.setter
    @_low_bank
    def _led_control_enabled(self, enabled: bool) -> None:
        self._led_control_enable_bit = enabled
