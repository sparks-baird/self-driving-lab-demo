import time as utime

import bitbangio
import board
import busio
import digitalio
from OV2640_reg import *
from OV5642_reg import *

OV2640 = 0
OV5642 = 1

MAX_FIFO_SIZE = 0x7FFFFF
ARDUCHIP_FRAMES = 0x01
ARDUCHIP_TIM = 0x03
VSYNC_LEVEL_MASK = 0x02
ARDUCHIP_TRIG = 0x41
CAP_DONE_MASK = 0x08

OV5642_CHIPID_HIGH = 0x300A
OV5642_CHIPID_LOW = 0x300B

OV2640_160x120 = 0
OV2640_176x144 = 1
OV2640_320x240 = 2
OV2640_352x288 = 3
OV2640_640x480 = 4
OV2640_800x600 = 5
OV2640_1024x768 = 6
OV2640_1280x1024 = 7
OV2640_1600x1200 = 8

OV5642_320x240 = 0
OV5642_640x480 = 1
OV5642_1024x768 = 2
OV5642_1280x960 = 3
OV5642_1600x1200 = 4
OV5642_2048x1536 = 5
OV5642_2592x1944 = 6
OV5642_1920x1080 = 7

Advanced_AWB = 0
Simple_AWB = 1
Manual_day = 2
Manual_A = 3
Manual_cwf = 4
Manual_cloudy = 5


degree_180 = 0
degree_150 = 1
degree_120 = 2
degree_90 = 3
degree_60 = 4
degree_30 = 5
degree_0 = 6
degree30 = 7
degree60 = 8
degree90 = 9
degree120 = 10
degree150 = 11

Auto = 0
Sunny = 1
Cloudy = 2
Office = 3
Home = 4

Antique = 0
Bluish = 1
Greenish = 2
Reddish = 3
BW = 4
Negative = 5
BWnegative = 6
Normal = 7
Sepia = 8
Overexposure = 9
Solarize = 10
Blueish = 11
Yellowish = 12

Exposure_17_EV = 0
Exposure_13_EV = 1
Exposure_10_EV = 2
Exposure_07_EV = 3
Exposure_03_EV = 4
Exposure_default = 5
Exposure03_EV = 6
Exposure07_EV = 7
Exposure10_EV = 8
Exposure13_EV = 9
Exposure17_EV = 10

Auto_Sharpness_default = 0
Auto_Sharpness1 = 1
Auto_Sharpness2 = 2
Manual_Sharpnessoff = 3
Manual_Sharpness1 = 4
Manual_Sharpness2 = 5
Manual_Sharpness3 = 6
Manual_Sharpness4 = 7
Manual_Sharpness5 = 8

MIRROR = 0
FLIP = 1
MIRROR_FLIP = 2

Saturation4 = 0
Saturation3 = 1
Saturation2 = 2
Saturation1 = 3
Saturation0 = 4
Saturation_1 = 5
Saturation_2 = 6
Saturation_3 = 7
Saturation_4 = 8

Brightness4 = 0
Brightness3 = 1
Brightness2 = 2
Brightness1 = 3
Brightness0 = 4
Brightness_1 = 5
Brightness_2 = 6
Brightness_3 = 7
Brightness_4 = 8

Contrast4 = 0
Contrast3 = 1
Contrast2 = 2
Contrast1 = 3
Contrast0 = 4
Contrast_1 = 5
Contrast_2 = 6
Contrast_3 = 7
Contrast_4 = 8

Antique = 0
Bluish = 1
Greenish = 2
Reddish = 3
BW = 4
Negative = 5
BWnegative = 6
Normal = 7
Sepia = 8
Overexposure = 9
Solarize = 10
Blueish = 11
Yellowish = 12

high_quality = 0
default_quality = 1
low_quality = 2

Color_bar = 0
Color_square = 1
BW_square = 2
DLI = 3

BMP = 0
JPEG = 1
RAW = 2


class ArducamClass(object):
    def __init__(self, Type):
        self.CameraMode = JPEG
        self.CameraType = Type
        self.SPI_CS = digitalio.DigitalInOut(board.GP5)
        self.SPI_CS.direction = digitalio.Direction.OUTPUT
        self.I2cAddress = 0x30
        self.spi = busio.SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)
        while not self.spi.try_lock():
            pass
        self.spi.configure(baudrate=4000000, polarity=0, phase=0, bits=8)
        self.i2c = bitbangio.I2C(scl=board.GP9, sda=board.GP8, frequency=1000000)
        while not self.i2c.try_lock():
            pass
        print(self.i2c.scan())
        self.Spi_write(0x07, 0x80)
        utime.sleep(0.1)
        self.Spi_write(0x07, 0x00)
        utime.sleep(0.1)

    def Camera_Detection(self):
        while True:
            if self.CameraType == OV2640:
                self.I2cAddress = 0x30
                self.wrSensorReg8_8(0xFF, 0x01)
                id_h = self.rdSensorReg8_8(0x0A)
                id_l = self.rdSensorReg8_8(0x0B)
                if (id_h == 0x26) and ((id_l == 0x40) or (id_l == 0x42)):
                    print("CameraType is OV2640")
                    break
                else:
                    print("Can't find OV2640 module")
            elif self.CameraType == OV5642:
                self.I2cAddress = 0x3C
                self.wrSensorReg16_8(0xFF, 0x01)
                id_h = self.rdSensorReg16_8(OV5642_CHIPID_HIGH)
                id_l = self.rdSensorReg16_8(OV5642_CHIPID_LOW)
                if (id_h == 0x56) and (id_l == 0x42):
                    print("CameraType is OV5642")
                    break
                else:
                    print("Can't find OV5642 module")
            utime.sleep(1)

    def Set_Camera_mode(self, mode):
        self.CameraMode = mode

    def wrSensorReg16_8(self, addr, val):
        buffer = bytearray(3)
        buffer[0] = (addr >> 8) & 0xFF
        buffer[1] = addr & 0xFF
        buffer[2] = val
        self.iic_write(buffer)

    def rdSensorReg16_8(self, addr):
        buffer = bytearray(2)
        rt = bytearray(1)
        buffer[0] = (addr >> 8) & 0xFF
        buffer[1] = addr & 0xFF
        self.iic_write(buffer)
        self.iic_readinto(rt)
        return rt[0]

    def wrSensorReg8_8(self, addr, val):
        buffer = bytearray(2)
        buffer[0] = addr
        buffer[1] = val
        self.iic_write(buffer)

    def iic_write(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.i2c.writeto(self.I2cAddress, buf, start=start, end=end)

    def iic_readinto(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.i2c.readfrom_into(self.I2cAddress, buf, start=start, end=end)

    def rdSensorReg8_8(self, addr):
        buffer = bytearray(1)
        buffer[0] = addr
        self.iic_write(buffer)
        self.iic_readinto(buffer)
        return buffer[0]

    def Spi_Test(self):
        while True:
            self.Spi_write(0x00, 0x56)
            value = self.Spi_read(0x00)
            if value[0] == 0x56:
                print("SPI interface OK")
                break
            else:
                print("SPI interface Error")
            utime.sleep(1)

    def Camera_Init(self):
        if self.CameraType == OV2640:
            self.wrSensorReg8_8(0xFF, 0x01)
            self.wrSensorReg8_8(0x12, 0x80)
            utime.sleep(0.1)
            self.wrSensorRegs8_8(OV2640_JPEG_INIT)
            self.wrSensorRegs8_8(OV2640_YUV422)
            self.wrSensorRegs8_8(OV2640_JPEG)
            self.wrSensorReg8_8(0xFF, 0x01)
            self.wrSensorReg8_8(0x15, 0x00)
            self.wrSensorRegs8_8(OV2640_320x240_JPEG)
        elif self.CameraType == OV5642:
            self.wrSensorReg16_8(0x3008, 0x80)
            if self.CameraMode == RAW:
                self.wrSensorRegs16_8(OV5642_1280x960_RAW)
                self.wrSensorRegs16_8(OV5642_640x480_RAW)
            else:
                self.wrSensorRegs16_8(OV5642_QVGA_Preview1)
                self.wrSensorRegs16_8(OV5642_QVGA_Preview2)
                utime.sleep(0.1)
                if self.CameraMode == JPEG:
                    utime.sleep(0.1)
                    self.wrSensorRegs16_8(OV5642_JPEG_Capture_QSXGA)
                    self.wrSensorRegs16_8(ov5642_320x240)
                    utime.sleep(0.1)
                    self.wrSensorReg16_8(0x3818, 0xA8)
                    self.wrSensorReg16_8(0x3621, 0x10)
                    self.wrSensorReg16_8(0x3801, 0xB0)
                    self.wrSensorReg16_8(0x4407, 0x04)
                else:
                    reg_val
                    self.wrSensorReg16_8(0x4740, 0x21)
                    self.wrSensorReg16_8(0x501E, 0x2A)
                    self.wrSensorReg16_8(0x5002, 0xF8)
                    self.wrSensorReg16_8(0x501F, 0x01)
                    self.wrSensorReg16_8(0x4300, 0x61)
                    reg_val = self.rdSensorReg16_8(0x3818)
                    self.wrSensorReg16_8(0x3818, (reg_val | 0x60) & 0xFF)
                    reg_val = self.rdSensorReg16_8(0x3621)
                    self.wrSensorReg16_8(0x3621, reg_val & 0xDF)
        else:
            pass

    def Spi_write(self, address, value):
        maskbits = 0x80
        buffer = bytearray(2)
        buffer[0] = address | maskbits
        buffer[1] = value
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.SPI_CS_HIGH()

    def Spi_read(self, address):
        maskbits = 0x7F
        buffer = bytearray(1)
        buffer[0] = address & maskbits
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.spi_readinto(buffer)
        self.SPI_CS_HIGH()
        return buffer

    def spi_write(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.write(buf, start=start, end=end)

    def spi_readinto(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.readinto(buf, start=start, end=end)

    def get_bit(self, addr, bit):
        value = self.Spi_read(addr)[0]
        return value & bit

    def SPI_CS_LOW(self):
        self.SPI_CS.value = False

    def SPI_CS_HIGH(self):
        self.SPI_CS.value = True

    def set_fifo_burst(self):
        buffer = bytearray(1)
        buffer[0] = 0x3C
        self.spi.write(buffer, start=0, end=1)

    def clear_fifo_flag(self):
        self.Spi_write(0x04, 0x01)

    def flush_fifo(self):
        self.Spi_write(0x04, 0x01)

    def start_capture(self):
        self.Spi_write(0x04, 0x02)

    def read_fifo_length(self):
        len1 = self.Spi_read(0x42)[0]
        len2 = self.Spi_read(0x43)[0]
        len3 = self.Spi_read(0x44)[0]
        len3 = len3 & 0x7F
        lenght = ((len3 << 16) | (len2 << 8) | (len1)) & 0x07FFFFF
        return lenght

    def wrSensorRegs8_8(self, reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if addr == 0xFF and val == 0xFF:
                return
            self.wrSensorReg8_8(addr, val)
            utime.sleep(0.001)

    def wrSensorRegs16_8(self, reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if addr == 0xFFFF and val == 0xFF:
                return
            self.wrSensorReg16_8(addr, val)
            utime.sleep(0.003)

    def set_format(self, mode):
        if mode == BMP or mode == JPEG or mode == RAW:
            self.CameraMode = mode

    def set_bit(self, addr, bit):
        temp = self.Spi_read(addr)[0]
        self.Spi_write(addr, temp & (~bit))

    def OV2640_set_JPEG_size(self, size):
        if size == OV2640_160x120:
            self.wrSensorRegs8_8(OV2640_160x120_JPEG)
        elif size == OV2640_176x144:
            self.wrSensorRegs8_8(OV2640_176x144_JPEG)
        elif size == OV2640_320x240:
            self.wrSensorRegs8_8(OV2640_320x240_JPEG)
        elif size == OV2640_352x288:
            self.wrSensorRegs8_8(OV2640_352x288_JPEG)
        elif size == OV2640_640x480:
            self.wrSensorRegs8_8(OV2640_640x480_JPEG)
        elif size == OV2640_800x600:
            self.wrSensorRegs8_8(OV2640_800x600_JPEG)
        elif size == OV2640_1024x768:
            self.wrSensorRegs8_8(OV2640_1024x768_JPEG)
        elif size == OV2640_1280x1024:
            self.wrSensorRegs8_8(OV2640_1280x1024_JPEG)
        elif size == OV2640_1600x1200:
            self.wrSensorRegs8_8(OV2640_1600x1200_JPEG)
        else:
            self.wrSensorRegs8_8(OV2640_320x240_JPEG)

    def OV2640_set_Light_Mode(self, result):
        if result == Auto:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x00)
        elif result == Sunny:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x5E)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x54)
        elif result == Cloudy:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x65)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x4F)
        elif result == Office:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x52)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x66)
        elif result == Home:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x42)
            self.wrSensorReg8_8(0xCD, 0x3F)
            self.wrSensorReg8_8(0xCE, 0x71)
        else:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x00)

    def OV2640_set_Color_Saturation(self, Saturation):
        if Saturation == Saturation2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x68)
            self.wrSensorReg8_8(0x7D, 0x68)
        elif Saturation == Saturation1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x58)
            self.wrSensorReg8_8(0x7D, 0x58)
        elif Saturation == Saturation0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x48)
            self.wrSensorReg8_8(0x7D, 0x48)
        elif Saturation == Saturation_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x38)
            self.wrSensorReg8_8(0x7D, 0x38)
        elif Saturation == Saturation_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x28)
            self.wrSensorReg8_8(0x7D, 0x28)

    def OV2640_set_Brightness(self, Brightness):
        if Brightness == Brightness2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x30)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x10)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x00)
            self.wrSensorReg8_8(0x7D, 0x00)

    def OV2640_set_Contrast(self, Contrast):
        if Contrast == Contrast2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x28)
            self.wrSensorReg8_8(0x7D, 0x0C)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x24)
            self.wrSensorReg8_8(0x7D, 0x16)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x2A)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7D, 0x34)
            self.wrSensorReg8_8(0x7D, 0x06)

    def OV2640_set_Special_effects(self, Special_effect):
        if Special_effect == Antique:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0xA6)
        elif Special_effect == Bluish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0xA0)
            self.wrSensorReg8_8(0x7D, 0x40)
        elif Special_effect == Greenish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0x40)
        elif Special_effect == Reddish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0xC0)
        elif Special_effect == BW:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == Negative:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == BWnegative:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x58)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == Normal:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x00)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)

    def OV5642_set_JPEG_size(self, size):
        if size == OV5642_320x240:
            self.wrSensorRegs16_8(ov5642_320x240)
        elif size == OV5642_640x480:
            self.wrSensorRegs16_8(ov5642_640x480)
        elif size == OV5642_1024x768:
            self.wrSensorRegs16_8(ov5642_1024x768)
        elif size == OV5642_1280x960:
            self.wrSensorRegs16_8(ov5642_1280x960)
        elif size == OV5642_1600x1200:
            self.wrSensorRegs16_8(ov5642_1600x1200)
        elif size == OV5642_2048x1536:
            self.wrSensorRegs16_8(ov5642_2048x1536)
        elif size == OV5642_2592x1944:
            self.wrSensorRegs16_8(ov5642_2592x1944)
        else:
            self.wrSensorRegs16_8(ov5642_320x240)

    def OV5642_set_Light_Mode(self, Light_Mode):
        if Light_Mode == Advanced_AWB:
            self.wrSensorReg16_8(0x3406, 0x0)
            self.wrSensorReg16_8(0x5192, 0x04)
            self.wrSensorReg16_8(0x5191, 0xF8)
            self.wrSensorReg16_8(0x518D, 0x26)
            self.wrSensorReg16_8(0x518F, 0x42)
            self.wrSensorReg16_8(0x518E, 0x2B)
            self.wrSensorReg16_8(0x5190, 0x42)
            self.wrSensorReg16_8(0x518B, 0xD0)
            self.wrSensorReg16_8(0x518C, 0xBD)
            self.wrSensorReg16_8(0x5187, 0x18)
            self.wrSensorReg16_8(0x5188, 0x18)
            self.wrSensorReg16_8(0x5189, 0x56)
            self.wrSensorReg16_8(0x518A, 0x5C)
            self.wrSensorReg16_8(0x5186, 0x1C)
            self.wrSensorReg16_8(0x5181, 0x50)
            self.wrSensorReg16_8(0x5184, 0x20)
            self.wrSensorReg16_8(0x5182, 0x11)
            self.wrSensorReg16_8(0x5183, 0x0)
        elif Light_Mode == Simple_AWB:
            self.wrSensorReg16_8(0x3406, 0x00)
            self.wrSensorReg16_8(0x5183, 0x80)
            self.wrSensorReg16_8(0x5191, 0xFF)
            self.wrSensorReg16_8(0x5192, 0x00)
        elif Light_Mode == Manual_day:
            self.wrSensorReg16_8(0x3406, 0x1)
            self.wrSensorReg16_8(0x3400, 0x7)
            self.wrSensorReg16_8(0x3401, 0x32)
            self.wrSensorReg16_8(0x3402, 0x4)
            self.wrSensorReg16_8(0x3403, 0x0)
            self.wrSensorReg16_8(0x3404, 0x5)
            self.wrSensorReg16_8(0x3405, 0x36)
        elif Light_Mode == Manual_A:
            self.wrSensorReg16_8(0x3406, 0x1)
            self.wrSensorReg16_8(0x3400, 0x4)
            self.wrSensorReg16_8(0x3401, 0x88)
            self.wrSensorReg16_8(0x3402, 0x4)
            self.wrSensorReg16_8(0x3403, 0x0)
            self.wrSensorReg16_8(0x3404, 0x8)
            self.wrSensorReg16_8(0x3405, 0xB6)
        elif Light_Mode == Manual_cwf:
            self.wrSensorReg16_8(0x3406, 0x1)
            self.wrSensorReg16_8(0x3400, 0x6)
            self.wrSensorReg16_8(0x3401, 0x13)
            self.wrSensorReg16_8(0x3402, 0x4)
            self.wrSensorReg16_8(0x3403, 0x0)
            self.wrSensorReg16_8(0x3404, 0x7)
            self.wrSensorReg16_8(0x3405, 0xE2)
        elif Light_Mode == Manual_cloudy:
            self.wrSensorReg16_8(0x3406, 0x1)
            self.wrSensorReg16_8(0x3400, 0x7)
            self.wrSensorReg16_8(0x3401, 0x88)
            self.wrSensorReg16_8(0x3402, 0x4)
            self.wrSensorReg16_8(0x3403, 0x0)
            self.wrSensorReg16_8(0x3404, 0x5)
            self.wrSensorReg16_8(0x3405, 0x0)

    def OV5642_set_Color_Saturation(self, Color_Saturation):
        if Color_Saturation == Saturation4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x80)
            self.wrSensorReg16_8(0x5584, 0x80)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x70)
            self.wrSensorReg16_8(0x5584, 0x70)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x60)
            self.wrSensorReg16_8(0x5584, 0x60)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x50)
            self.wrSensorReg16_8(0x5584, 0x50)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation0:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x40)
            self.wrSensorReg16_8(0x5584, 0x40)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation_1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x30)
            self.wrSensorReg16_8(0x5584, 0x30)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation_2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x20)
            self.wrSensorReg16_8(0x5584, 0x20)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation_3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x10)
            self.wrSensorReg16_8(0x5584, 0x10)
            self.wrSensorReg16_8(0x5580, 0x02)
        elif Color_Saturation == Saturation_4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5583, 0x00)
            self.wrSensorReg16_8(0x5584, 0x00)
            self.wrSensorReg16_8(0x5580, 0x02)

    def OV5642_set_Brightness(self, Brightness):
        if Brightness == Brightness4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x40)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Brightness == Brightness3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x30)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Brightness == Brightness2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x20)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Brightness == Brightness1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x10)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Brightness == Brightness0:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x00)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Brightness == Brightness_1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x10)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x08)
        elif Brightness == Brightness_2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x20)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x08)
        elif Brightness == Brightness_3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x30)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x08)
        elif Brightness == Brightness_4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5589, 0x40)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x558A, 0x08)

    def OV5642_set_Contrast(self, Contrast):
        if Contrast == Contrast4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x30)
            self.wrSensorReg16_8(0x5588, 0x30)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x2C)
            self.wrSensorReg16_8(0x5588, 0x2C)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x28)
            self.wrSensorReg16_8(0x5588, 0x28)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x24)
            self.wrSensorReg16_8(0x5588, 0x24)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast0:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x20)
            self.wrSensorReg16_8(0x5588, 0x20)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast_1:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x1C)
            self.wrSensorReg16_8(0x5588, 0x1C)
            self.wrSensorReg16_8(0x558A, 0x1C)
        elif Contrast == Contrast_2:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x18)
            self.wrSensorReg16_8(0x5588, 0x18)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast_3:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x14)
            self.wrSensorReg16_8(0x5588, 0x14)
            self.wrSensorReg16_8(0x558A, 0x00)
        elif Contrast == Contrast_4:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x04)
            self.wrSensorReg16_8(0x5587, 0x10)
            self.wrSensorReg16_8(0x5588, 0x10)
            self.wrSensorReg16_8(0x558A, 0x00)

    def OV5642_set_hue(self, degree):
        if degree == degree_180:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x80)
            self.wrSensorReg16_8(0x5582, 0x00)
            self.wrSensorReg16_8(0x558A, 0x32)
        elif degree == degree_150:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x6F)
            self.wrSensorReg16_8(0x5582, 0x40)
            self.wrSensorReg16_8(0x558A, 0x32)
        elif degree == degree_120:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x40)
            self.wrSensorReg16_8(0x5582, 0x6F)
            self.wrSensorReg16_8(0x558A, 0x32)
        elif degree == degree_90:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x00)
            self.wrSensorReg16_8(0x5582, 0x80)
            self.wrSensorReg16_8(0x558A, 0x02)
        elif degree == degree_60:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x40)
            self.wrSensorReg16_8(0x5582, 0x6F)
            self.wrSensorReg16_8(0x558A, 0x02)
        elif degree == degree_30:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x6F)
            self.wrSensorReg16_8(0x5582, 0x40)
            self.wrSensorReg16_8(0x558A, 0x02)
        elif degree == degree_0:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x80)
            self.wrSensorReg16_8(0x5582, 0x00)
            self.wrSensorReg16_8(0x558A, 0x01)
        elif degree == degree30:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x6F)
            self.wrSensorReg16_8(0x5582, 0x40)
            self.wrSensorReg16_8(0x558A, 0x01)
        elif degree == degree60:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x40)
            self.wrSensorReg16_8(0x5582, 0x6F)
            self.wrSensorReg16_8(0x558A, 0x01)
        elif degree == degree90:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x00)
            self.wrSensorReg16_8(0x5582, 0x80)
            self.wrSensorReg16_8(0x558A, 0x31)
        elif degree == degree120:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x40)
            self.wrSensorReg16_8(0x5582, 0x6F)
            self.wrSensorReg16_8(0x558A, 0x31)
        elif degree == degree150:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x01)
            self.wrSensorReg16_8(0x5581, 0x6F)
            self.wrSensorReg16_8(0x5582, 0x40)
            self.wrSensorReg16_8(0x558A, 0x31)

    def OV5642_set_Special_effects(self, Special_effect):
        if Special_effect == Bluish:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x18)
            self.wrSensorReg16_8(0x5585, 0xA0)
            self.wrSensorReg16_8(0x5586, 0x40)
        elif Special_effect == Greenish:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x18)
            self.wrSensorReg16_8(0x5585, 0x60)
            self.wrSensorReg16_8(0x5586, 0x60)
        elif Special_effect == Reddish:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x18)
            self.wrSensorReg16_8(0x5585, 0x80)
            self.wrSensorReg16_8(0x5586, 0xC0)
        elif Special_effect == BW:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x18)
            self.wrSensorReg16_8(0x5585, 0x80)
            self.wrSensorReg16_8(0x5586, 0x80)
        elif Special_effect == Negative:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x40)
        elif Special_effect == Sepia:
            self.wrSensorReg16_8(0x5001, 0xFF)
            self.wrSensorReg16_8(0x5580, 0x18)
            self.wrSensorReg16_8(0x5585, 0x40)
            self.wrSensorReg16_8(0x5586, 0xA0)
        elif Special_effect == Normal:
            self.wrSensorReg16_8(0x5001, 0x7F)
            self.wrSensorReg16_8(0x5580, 0x00)

    def OV5642_set_Exposure_level(self, level):
        if level == Exposure_17_EV:
            self.wrSensorReg16_8(0x3A0F, 0x10)
            self.wrSensorReg16_8(0x3A10, 0x08)
            self.wrSensorReg16_8(0x3A1B, 0x10)
            self.wrSensorReg16_8(0x3A1E, 0x08)
            self.wrSensorReg16_8(0x3A11, 0x20)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure_13_EV:
            self.wrSensorReg16_8(0x3A0F, 0x18)
            self.wrSensorReg16_8(0x3A10, 0x10)
            self.wrSensorReg16_8(0x3A1B, 0x18)
            self.wrSensorReg16_8(0x3A1E, 0x10)
            self.wrSensorReg16_8(0x3A11, 0x30)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure_10_EV:
            self.wrSensorReg16_8(0x3A0F, 0x20)
            self.wrSensorReg16_8(0x3A10, 0x18)
            self.wrSensorReg16_8(0x3A11, 0x41)
            self.wrSensorReg16_8(0x3A1B, 0x20)
            self.wrSensorReg16_8(0x3A1E, 0x18)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure_07_EV:
            self.wrSensorReg16_8(0x3A0F, 0x28)
            self.wrSensorReg16_8(0x3A10, 0x20)
            self.wrSensorReg16_8(0x3A11, 0x51)
            self.wrSensorReg16_8(0x3A1B, 0x28)
            self.wrSensorReg16_8(0x3A1E, 0x20)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure_03_EV:
            self.wrSensorReg16_8(0x3A0F, 0x30)
            self.wrSensorReg16_8(0x3A10, 0x28)
            self.wrSensorReg16_8(0x3A11, 0x61)
            self.wrSensorReg16_8(0x3A1B, 0x30)
            self.wrSensorReg16_8(0x3A1E, 0x28)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure_default:
            self.wrSensorReg16_8(0x3A0F, 0x38)
            self.wrSensorReg16_8(0x3A10, 0x30)
            self.wrSensorReg16_8(0x3A11, 0x61)
            self.wrSensorReg16_8(0x3A1B, 0x38)
            self.wrSensorReg16_8(0x3A1E, 0x30)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure03_EV:
            self.wrSensorReg16_8(0x3A0F, 0x40)
            self.wrSensorReg16_8(0x3A10, 0x38)
            self.wrSensorReg16_8(0x3A11, 0x71)
            self.wrSensorReg16_8(0x3A1B, 0x40)
            self.wrSensorReg16_8(0x3A1E, 0x38)
            self.wrSensorReg16_8(0x3A1F, 0x10)
        elif level == Exposure07_EV:
            self.wrSensorReg16_8(0x3A0F, 0x48)
            self.wrSensorReg16_8(0x3A10, 0x40)
            self.wrSensorReg16_8(0x3A11, 0x80)
            self.wrSensorReg16_8(0x3A1B, 0x48)
            self.wrSensorReg16_8(0x3A1E, 0x40)
            self.wrSensorReg16_8(0x3A1F, 0x20)
        elif level == Exposure10_EV:
            self.wrSensorReg16_8(0x3A0F, 0x50)
            self.wrSensorReg16_8(0x3A10, 0x48)
            self.wrSensorReg16_8(0x3A11, 0x90)
            self.wrSensorReg16_8(0x3A1B, 0x50)
            self.wrSensorReg16_8(0x3A1E, 0x48)
            self.wrSensorReg16_8(0x3A1F, 0x20)
        elif level == Exposure13_EV:
            self.wrSensorReg16_8(0x3A0F, 0x58)
            self.wrSensorReg16_8(0x3A10, 0x50)
            self.wrSensorReg16_8(0x3A11, 0x91)
            self.wrSensorReg16_8(0x3A1B, 0x58)
            self.wrSensorReg16_8(0x3A1E, 0x50)
            self.wrSensorReg16_8(0x3A1F, 0x20)
        elif level == Exposure17_EV:
            self.wrSensorReg16_8(0x3A0F, 0x60)
            self.wrSensorReg16_8(0x3A10, 0x58)
            self.wrSensorReg16_8(0x3A11, 0xA0)
            self.wrSensorReg16_8(0x3A1B, 0x60)
            self.wrSensorReg16_8(0x3A1E, 0x58)
            self.wrSensorReg16_8(0x3A1F, 0x20)

    def OV5642_set_Sharpness(self, Sharpness):
        if Sharpness == Auto_Sharpness_default:
            self.wrSensorReg16_8(0x530A, 0x00)
            self.wrSensorReg16_8(0x530C, 0x0)
            self.wrSensorReg16_8(0x530D, 0xC)
            self.wrSensorReg16_8(0x5312, 0x40)
        elif Sharpness == Auto_Sharpness1:
            self.wrSensorReg16_8(0x530A, 0x00)
            self.wrSensorReg16_8(0x530C, 0x4)
            self.wrSensorReg16_8(0x530D, 0x18)
            self.wrSensorReg16_8(0x5312, 0x20)
        elif Sharpness == Auto_Sharpness2:
            self.wrSensorReg16_8(0x530A, 0x00)
            self.wrSensorReg16_8(0x530C, 0x8)
            self.wrSensorReg16_8(0x530D, 0x30)
            self.wrSensorReg16_8(0x5312, 0x10)
        elif Sharpness == Manual_Sharpnessoff:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x00)
            self.wrSensorReg16_8(0x531F, 0x00)
        elif Sharpness == Manual_Sharpness1:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x04)
            self.wrSensorReg16_8(0x531F, 0x04)
        elif Sharpness == Manual_Sharpness2:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x08)
            self.wrSensorReg16_8(0x531F, 0x08)
        elif Sharpness == Manual_Sharpness3:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x0C)
            self.wrSensorReg16_8(0x531F, 0x0C)
        elif Sharpness == Manual_Sharpness4:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x0F)
            self.wrSensorReg16_8(0x531F, 0x0F)
        elif Sharpness == Manual_Sharpness5:
            self.wrSensorReg16_8(0x530A, 0x08)
            self.wrSensorReg16_8(0x531E, 0x1F)
            self.wrSensorReg16_8(0x531F, 0x1F)

    def OV5642_set_Mirror_Flip(self, Mirror_Flip):
        if Mirror_Flip == MIRROR:
            reg_val = self.rdSensorReg16_8(0x3818)
            reg_val = reg_val | 0x00
            reg_val = reg_val & 0x9F
            self.wrSensorReg16_8(0x3818, reg_val)
            reg_val = self.rdSensorReg16_8(0x3621)
            reg_val = reg_val | 0x20
            self.wrSensorReg16_8(0x3621, reg_val)
        elif Mirror_Flip == FLIP:
            reg_val = self.rdSensorReg16_8(0x3818)
            reg_val = reg_val | 0x20
            reg_val = reg_val & 0xBF
            self.wrSensorReg16_8(0x3818, reg_val)
            reg_val = self.rdSensorReg16_8(0x3621)
            reg_val = reg_val | 0x20
            self.wrSensorReg16_8(0x3621, reg_val)
        elif Mirror_Flip == MIRROR_FLIP:
            reg_val = self.rdSensorReg16_8(0x3818)
            reg_val = reg_val | 0x60
            reg_val = reg_val & 0xFF
            self.wrSensorReg16_8(0x3818, reg_val)
            reg_val = self.rdSensorReg16_8(0x3621)
            reg_val = reg_val & 0xDF
            self.wrSensorReg16_8(0x3621, reg_val)
        elif Mirror_Flip == Normal:
            reg_val = self.rdSensorReg16_8(0x3818)
            reg_val = reg_val | 0x40
            reg_val = reg_val & 0xDF
            self.wrSensorReg16_8(0x3818, reg_val)
            reg_val = self.rdSensorReg16_8(0x3621)
            reg_val = reg_val & 0xDF
            self.wrSensorReg16_8(0x3621, reg_val)

    def OV5642_set_Compress_quality(self, quality):
        if quality == high_quality:
            self.wrSensorReg16_8(0x4407, 0x02)
        elif quality == default_quality:
            self.wrSensorReg16_8(0x4407, 0x04)
        elif quality == low_quality:
            self.wrSensorReg16_8(0x4407, 0x08)

    def OV5642_Test_Pattern(self, Pattern):
        if Pattern == Color_bar:
            self.wrSensorReg16_8(0x503D, 0x80)
            self.wrSensorReg16_8(0x503E, 0x00)
        elif Pattern == Color_square:
            self.wrSensorReg16_8(0x503D, 0x85)
            self.wrSensorReg16_8(0x503E, 0x12)
        elif Pattern == BW_square:
            self.wrSensorReg16_8(0x503D, 0x85)
            self.wrSensorReg16_8(0x503E, 0x1A)
        elif Pattern == DLI:
            self.wrSensorReg16_8(0x4741, 0x4)
