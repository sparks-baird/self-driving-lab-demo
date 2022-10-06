import time as utime

import usb_cdc
from Arducam import *
from board import *

mode = 0
start_capture = 0
stop_flag = 0
once_number = 128
value_command = 0
flag_command = 0
buffer = bytearray(once_number)

mycam = ArducamClass(OV5642)
mycam.Camera_Detection()
mycam.Spi_Test()
mycam.Camera_Init()
mycam.Spi_write(ARDUCHIP_TIM, VSYNC_LEVEL_MASK)
utime.sleep(1)
mycam.clear_fifo_flag()
mycam.Spi_write(ARDUCHIP_FRAMES, 0x00)


def read_fifo_burst():
    count = 0
    lenght = mycam.read_fifo_length()
    mycam.SPI_CS_LOW()
    mycam.set_fifo_burst()
    while True:
        mycam.spi.readinto(buffer, start=0, end=once_number)
        usb_cdc.data.write(buffer)
        utime.sleep(0.00015)
        count += once_number
        if count + once_number > lenght:
            count = lenght - count
            mycam.spi.readinto(buffer, start=0, end=count)
            usb_cdc.data.write(buffer)
            mycam.SPI_CS_HIGH()
            mycam.clear_fifo_flag()
            break


while True:
    if usb_cdc.data.in_waiting > 0:
        value_command = usb_cdc.data.read()
        flag_command = 1
    if flag_command == 1:
        flag_command = 0
        value = int.from_bytes(value_command, "big")
        if value == 0:
            mycam.OV5642_set_JPEG_size(OV5642_320x240)
        elif value == 1:
            mycam.OV5642_set_JPEG_size(OV5642_640x480)
        elif value == 2:
            mycam.OV5642_set_JPEG_size(OV5642_1024x768)
        elif value == 3:
            mycam.OV5642_set_JPEG_size(OV5642_1280x960)
        elif value == 4:
            mycam.OV5642_set_JPEG_size(OV5642_1600x1200)
        elif value == 5:
            mycam.OV5642_set_JPEG_size(OV5642_2048x1536)
        elif value == 6:
            mycam.OV5642_set_JPEG_size(OV5642_2592x1944)
        elif value == 0x10:
            mode = 1
            start_capture = 1
        elif value == 0x20:
            mode = 2
            start_capture = 2
            stop_flag = 0
        elif value == 0x21:
            stop_flag = 1
        elif value == 0x40:
            mycam.OV5642_set_Light_Mode(Advanced_AWB)
        elif value == 0x41:
            mycam.OV5642_set_Light_Mode(Simple_AWB)
        elif value == 0x42:
            mycam.OV5642_set_Light_Mode(Manual_day)
        elif value == 0x43:
            mycam.OV5642_set_Light_Mode(Manual_A)
        elif value == 0x44:
            mycam.OV5642_set_Light_Mode(Manual_cwf)
        elif value == 0x45:
            mycam.OV5642_set_Light_Mode(Manual_cloudy)
        elif value == 0x50:
            mycam.OV5642_set_Color_Saturation(Saturation4)
        elif value == 0x51:
            mycam.OV5642_set_Color_Saturation(Saturation3)
        elif value == 0x52:
            mycam.OV5642_set_Color_Saturation(Saturation2)
        elif value == 0x53:
            mycam.OV5642_set_Color_Saturation(Saturation1)
        elif value == 0x54:
            mycam.OV5642_set_Color_Saturation(Saturation0)
        elif value == 0x55:
            mycam.OV5642_set_Color_Saturation(Saturation_1)
        elif value == 0x56:
            mycam.OV5642_set_Color_Saturation(Saturation_2)
        elif value == 0x57:
            mycam.OV5642_set_Color_Saturation(Saturation_3)
        elif value == 0x58:
            mycam.OV5642_set_Light_Mode(Saturation_4)
        elif value == 0x60:
            mycam.OV5642_set_Brightness(Brightness4)
        elif value == 0x61:
            mycam.OV5642_set_Brightness(Brightness3)
        elif value == 0x62:
            mycam.OV5642_set_Brightness(Brightness2)
        elif value == 0x63:
            mycam.OV5642_set_Brightness(Brightness1)
        elif value == 0x64:
            mycam.OV5642_set_Brightness(Brightness0)
        elif value == 0x65:
            mycam.OV5642_set_Brightness(Brightness_1)
        elif value == 0x66:
            mycam.OV5642_set_Brightness(Brightness_2)
        elif value == 0x67:
            mycam.OV5642_set_Brightness(Brightness_3)
        elif value == 0x68:
            mycam.OV5642_set_Brightness(Brightness_4)
        elif value == 0x70:
            mycam.OV5642_set_Contrast(Contrast4)
        elif value == 0x71:
            mycam.OV5642_set_Contrast(Contrast3)
        elif value == 0x72:
            mycam.OV5642_set_Contrast(Contrast2)
        elif value == 0x73:
            mycam.OV5642_set_Contrast(Contrast1)
        elif value == 0x74:
            mycam.OV5642_set_Contrast(Contrast0)
        elif value == 0x75:
            mycam.OV5642_set_Contrast(Contrast_1)
        elif value == 0x76:
            mycam.OV5642_set_Contrast(Contrast_2)
        elif value == 0x77:
            mycam.OV5642_set_Contrast(Contrast_3)
        elif value == 0x78:
            mycam.OV5642_set_Contrast(Contrast_4)
        elif value == 0x80:
            mycam.OV5642_set_hue(degree_180)
        elif value == 0x81:
            mycam.OV5642_set_hue(degree_150)
        elif value == 0x82:
            mycam.OV5642_set_hue(degree_120)
        elif value == 0x83:
            mycam.OV5642_set_hue(degree_90)
        elif value == 0x84:
            mycam.OV5642_set_hue(degree_60)
        elif value == 0x85:
            mycam.OV5642_set_hue(degree_30)
        elif value == 0x86:
            mycam.OV5642_set_hue(degree_0)
        elif value == 0x87:
            mycam.OV5642_set_hue(degree30)
        elif value == 0x88:
            mycam.OV5642_set_hue(degree60)
        elif value == 0x89:
            mycam.OV5642_set_hue(degree90)
        elif value == 0x8A:
            mycam.OV5642_set_hue(degree120)
        elif value == 0x8B:
            mycam.OV5642_set_hue(degree150)
        elif value == 0x90:
            mycam.OV5642_set_Special_effects(Normal)
        elif value == 0x91:
            mycam.OV5642_set_Special_effects(BW)
        elif value == 0x92:
            mycam.OV5642_set_Special_effects(Bluish)
        elif value == 0x93:
            mycam.OV5642_set_Special_effects(Sepia)
        elif value == 0x94:
            mycam.OV5642_set_Special_effects(Reddish)
        elif value == 0x95:
            mycam.OV5642_set_Special_effects(Greenish)
        elif value == 0x96:
            mycam.OV5642_set_Special_effects(Negative)
        elif value == 0xA0:
            mycam.OV5642_set_Exposure_level(Exposure_17_EV)
        elif value == 0xA1:
            mycam.OV5642_set_Exposure_level(Exposure_13_EV)
        elif value == 0xA2:
            mycam.OV5642_set_Exposure_level(Exposure_10_EV)
        elif value == 0xA3:
            mycam.OV5642_set_Exposure_level(Exposure_07_EV)
        elif value == 0xA4:
            mycam.OV5642_set_Exposure_level(Exposure_03_EV)
        elif value == 0xA5:
            mycam.OV5642_set_Exposure_level(Exposure_default)
        elif value == 0xA6:
            mycam.OV5642_set_Exposure_level(Exposure07_EV)
        elif value == 0xA7:
            mycam.OV5642_set_Exposure_level(Exposure10_EV)
        elif value == 0xA8:
            mycam.OV5642_set_Exposure_level(Exposure13_EV)
        elif value == 0xA9:
            mycam.OV5642_set_Exposure_level(Exposure17_EV)
        elif value == 0xB0:
            mycam.OV5642_set_Sharpness(Auto_Sharpness_default)
        elif value == 0xB1:
            mycam.OV5642_set_Sharpness(Auto_Sharpness1)
        elif value == 0xB2:
            mycam.OV5642_set_Sharpness(Auto_Sharpness2)
        elif value == 0xB3:
            mycam.OV5642_set_Sharpness(Manual_Sharpnessoff)
        elif value == 0xB4:
            mycam.OV5642_set_Sharpness(Manual_Sharpness1)
        elif value == 0xB5:
            mycam.OV5642_set_Sharpness(Manual_Sharpness2)
        elif value == 0xB6:
            mycam.OV5642_set_Sharpness(Manual_Sharpness3)
        elif value == 0xB7:
            mycam.OV5642_set_Sharpness(Manual_Sharpness4)
        elif value == 0xB8:
            mycam.OV5642_set_Sharpness(Manual_Sharpness5)
        elif value == 0xC0:
            mycam.OV5642_set_Mirror_Flip(MIRROR)
        elif value == 0xC1:
            mycam.OV5642_set_Mirror_Flip(FLIP)
        elif value == 0xC2:
            mycam.OV5642_set_Mirror_Flip(MIRROR_FLIP)
        elif value == 0xC3:
            mycam.OV5642_set_Mirror_Flip(Normal)
        elif value == 0xD0:
            mycam.OV5642_set_Compress_quality(high_quality)
        elif value == 0xD1:
            mycam.OV5642_set_Compress_quality(default_quality)
        elif value == 0xD2:
            mycam.OV5642_set_Compress_quality(low_quality)
        elif value == 0xE0:
            mycam.OV5642_Test_Pattern(Color_bar)
        elif value == 0xE1:
            mycam.OV5642_Test_Pattern(Color_square)
        elif value == 0xE2:
            mycam.OV5642_Test_Pattern(BW_square)
        elif value == 0xE3:
            mycam.OV5642_Test_Pattern(DLI)

    if mode == 1:
        if start_capture == 1:
            mycam.flush_fifo()
            mycam.clear_fifo_flag()
            mycam.start_capture()
            start_capture = 0
        if mycam.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK) != 0:
            read_fifo_burst()
            mode = 0

    if mode == 2:
        if stop_flag == 0:
            if start_capture == 2:
                start_capture = 0
                mycam.flush_fifo()
                mycam.clear_fifo_flag()
                mycam.start_capture()
            if mycam.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK) != 0:
                read_fifo_burst()
                start_capture = 2
        else:
            mode = 0
            start_capture = 0
