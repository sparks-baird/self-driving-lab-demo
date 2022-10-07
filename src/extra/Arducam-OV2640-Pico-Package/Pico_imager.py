import time as utime

import board
import busio
from Arducam_OV2640 import *
from board import *

"""
0x00-0x08       -       Change resolution if mode is JPEG
0x10            -       Capture Image and send it via Uart

0x11            -       Init Camera with mode YUV
0x12            -       Init Camera with mode JPEG

0x20            -       Start Video Stream (Continuous capture mode)
0x21            -       Stop Video Stream (Continuous capture mode)

0x30            -       ???

0x40-0x44       -       Set Light mode
0x50-0x54       -       Set Color Saturation
0x60-0x64       -       Set Brightness
0x70-0x74       -       Set Contrast
0x80-0x87       -       Set Special Effects
0x90-0x95       -       Set Compression (0 off; 5 full)

0xA0            -       Connection Test
"""

once_number = 1024
mode = 0
start_capture = 0
stop_flag = 0
buffer = bytearray(1024)

uart = busio.UART(
    tx=board.GP0, rx=board.GP1, baudrate=921600, bits=8, parity=None, stop=1, timeout=0
)
mycam = ArducamClass(OV2640)
mycam.Camera_Detection()
mycam.Spi_Test()
# mycam.Camera_Init(JPEG)
mycam.Camera_Init(YUV)
utime.sleep(1)
mycam.clear_fifo_flag()


def read_fifo_burst():
    uart.write(str.encode("START\n"))
    count = 0
    lenght = mycam.read_fifo_length()
    mycam.SPI_CS_LOW()
    mycam.set_fifo_burst()
    while True:
        mycam.spi.readinto(buffer, start=0, end=once_number)
        uart.write(buffer)
        count += once_number
        if count + once_number > lenght:
            count = lenght - count
            mycam.spi.readinto(buffer, start=0, end=count)
            uart.write(buffer)
            mycam.SPI_CS_HIGH()
            mycam.clear_fifo_flag()
            break

    uart.write(str.encode("\n"))
    uart.write(str.encode("STOP\n"))


while True:
    value = uart.read()
    if value != None:
        value = int.from_bytes(value, "big")
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
            mycam.set_format(YUV)
            mycam.Camera_Init()
            mycam.set_bit(ARDUCHIP_TIM, VSYNC_LEVEL_MASK)
        elif value == 0x12:
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

        elif value == 0x90:
            mycam.OV2640_set_JPEG_Compression(Compression_Off)
        elif value == 0x91:
            mycam.OV2640_set_JPEG_Compression(Compression_1)
        elif value == 0x92:
            mycam.OV2640_set_JPEG_Compression(Compression_2)
        elif value == 0x93:
            mycam.OV2640_set_JPEG_Compression(Compression_3)
        elif value == 0x94:
            mycam.OV2640_set_JPEG_Compression(Compression_4)
        elif value == 0x95:
            mycam.OV2640_set_JPEG_Compression(Compression_Full)

        elif value == 0xA0:
            uart.write(b"\x00")

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
