"""Sterling Baird: wrapper class for AS7341 sensor."""

from as7341 import AS7341, AS7341_MODE_SPM
from machine import I2C, Pin


class ExternalDeviceNotFound(OSError):
    pass


class Sensor:
    def __init__(
        self, atime=100, astep=999, gain=128, i2c=I2C(1, scl=Pin(27), sda=Pin(26))
    ):
        """Wrapper for Rob Hamerling's AS7341 implementation.

        Mimics the original CircuitPython class a bit more, specific to the needs of
        SDL-Demo.

        Rob Hamerling's implementation:
        - https://gitlab.com/robhamerling/micropython-as7341

        Original Circuit Python repo:
        - https://github.com/adafruit/Adafruit_CircuitPython_AS7341

        Parameters
        ----------
        atime : int, optional
            The integration time step size in 2.78 microsecond increments, by default 100
        astep : int, optional
            The integration time step count. Total integration time will be (ATIME + 1)
            * (ASTEP + 1) * 2.78µS, by default 999, meaning 281 ms assuming atime=100
        again : int, optional
            The ADC gain multiplier. factor 8 (with pretty much light), by default 128
        i2c : I2C, optional
            The I2C bus, by default machine.I2C(1, scl=machine.Pin(27),
            sda=machine.Pin(26))

        Raises
        ------
        ExternalDeviceNotFound
            Couldn't connect to AS7341.

        Examples
        --------
        >>> sensor = Sensor(atime=29, astep=599, again=4)
        >>> channel_data = sensor.all_channels
        """

        # i2c = machine.SoftI2C(scl=Pin(27), sda=Pin(26))
        self.i2c = i2c
        addrlist = " ".join(["0x{:02X}".format(x) for x in i2c.scan()])  # type: ignore
        print("Detected devices at I2C-addresses:", addrlist)

        sensor = AS7341(i2c)

        if not sensor.isconnected():
            raise ExternalDeviceNotFound("Failed to contact AS7341, terminating")

        sensor.set_measure_mode(AS7341_MODE_SPM)

        sensor.set_atime(atime)
        sensor.set_astep(astep)
        sensor.set_again(gain)

        self.sensor = sensor

        self.__atime = atime
        self.__astep = astep
        self.__gain = gain

    @property
    def _atime(self):
        return self.__atime

    @_atime.setter
    def _atime(self, value):
        self.__atime = value
        self.sensor.set_atime(value)

    @property
    def _astep(self):
        return self.__astep

    @_astep.setter
    def _astep(self, value):
        self.__atime = value
        self.sensor.set_astep(value)

    @property
    def _gain(self):
        return self.__gain

    @_gain.setter
    def _gain(self, value):
        self.__gain = value
        self.sensor.set_again(value)

    @property
    def all_channels(self):
        self.sensor.start_measure("F1F4CN")
        f1, f2, f3, f4, clr, nir = self.sensor.get_spectral_data()

        self.sensor.start_measure("F5F8CN")
        f5, f6, f7, f8, clr, nir = self.sensor.get_spectral_data()

        clr, nir  # to ignore "unused" linting warnings

        return [f1, f2, f3, f4, f5, f6, f7, f8]

    def disable(self):
        self.sensor.disable()
