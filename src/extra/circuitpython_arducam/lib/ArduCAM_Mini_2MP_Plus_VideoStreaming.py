import time as utime

import usb_cdc
from Arducam import *
from board import *

once_number = 128
mode = 0
start_capture = 0
stop_flag = 0
data_in = 0
value_command = 0
flag_command = 0
buffer = bytearray(once_number)

mycam = ArducamClass(OV2640)
mycam.Camera_Detection()
mycam.Spi_Test()
mycam.Camera_Init()
utime.sleep(1)
mycam.clear_fifo_flag()


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
            mycam.OV2640_set_JPEG_size(OV2640_160x120)
        elif value == 1:
            mycam.OV2640_set_JPEG_size(OV2640_176x144)
        elif value == 2:
            mycam.OV2640_set_JPEG_size(OV2640_320x240)
        elif value == 3:
            mycam.OV2640_set_JPEG_size(OV2640_352x288)
        elif value == 4:
            mycam.OV2640_set_JPEG_size(OV2640_640x480)
        elif value == 5:
            mycam.OV2640_set_JPEG_size(OV2640_800x600)
        elif value == 6:
            mycam.OV2640_set_JPEG_size(OV2640_1024x768)
        elif value == 7:
            mycam.OV2640_set_JPEG_size(OV2640_1280x1024)
        elif value == 8:
            mycam.OV2640_set_JPEG_size(OV2640_1600x1200)
        elif value == 0x10:
            mode = 1
            start_capture = 1
        elif value == 0x11:
            mycam.set_format(JPEG)
            mycam.Camera_Init()
            mycam.set_bit(ARDUCHIP_TIM, VSYNC_LEVEL_MASK)
        elif value == 0x20:
            mode = 2
            start_capture = 2
            stop_flag = 0
        elif value == 0x21:
            stop_flag = 1
        elif value == 0x30:
            mode = 3
            start_capture = 3
        elif value == 0x40:
            mycam.OV2640_set_Light_Mode(Auto)
        elif value == 0x41:
            mycam.OV2640_set_Light_Mode(Sunny)
        elif value == 0x42:
            mycam.OV2640_set_Light_Mode(Cloudy)
        elif value == 0x43:
            mycam.OV2640_set_Light_Mode(Office)
        elif value == 0x44:
            mycam.OV2640_set_Light_Mode(Home)
        elif value == 0x50:
            mycam.OV2640_set_Color_Saturation(Saturation2)
        elif value == 0x51:
            mycam.OV2640_set_Color_Saturation(Saturation1)
        elif value == 0x52:
            mycam.OV2640_set_Color_Saturation(Saturation0)
        elif value == 0x53:
            mycam.OV2640_set_Color_Saturation(Saturation_1)
        elif value == 0x54:
            mycam.OV2640_set_Color_Saturation(Saturation_2)
        elif value == 0x60:
            mycam.OV2640_set_Brightness(Brightness2)
        elif value == 0x61:
            mycam.OV2640_set_Brightness(Brightness1)
        elif value == 0x62:
            mycam.OV2640_set_Brightness(Brightness0)
        elif value == 0x63:
            mycam.OV2640_set_Brightness(Brightness_1)
        elif value == 0x64:
            mycam.OV2640_set_Brightness(Brightness_2)
        elif value == 0x70:
            mycam.OV2640_set_Contrast(Contrast2)
        elif value == 0x71:
            mycam.OV2640_set_Contrast(Contrast1)
        elif value == 0x72:
            mycam.OV2640_set_Contrast(Contrast0)
        elif value == 0x73:
            mycam.OV2640_set_Contrast(Contrast_1)
        elif value == 0x74:
            mycam.OV2640_set_Contrast(Contrast_2)
        elif value == 0x80:
            mycam.OV2640_set_Special_effects(Antique)
        elif value == 0x81:
            mycam.OV2640_set_Special_effects(Bluish)
        elif value == 0x82:
            mycam.OV2640_set_Special_effects(Greenish)
        elif value == 0x83:
            mycam.OV2640_set_Special_effects(Reddish)
        elif value == 0x84:
            mycam.OV2640_set_Special_effects(BW)
        elif value == 0x85:
            mycam.OV2640_set_Special_effects(Negative)
        elif value == 0x86:
            mycam.OV2640_set_Special_effects(BWnegative)
        elif value == 0x87:
            mycam.OV2640_set_Special_effects(Normal)

    if mode == 1:
        if start_capture == 1:
            mycam.flush_fifo()
            mycam.clear_fifo_flag()
            mycam.start_capture()
            start_capture = 0
        if mycam.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK) != 0:
            read_fifo_burst()
            mode = 0
    elif mode == 2:
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
