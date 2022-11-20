import machine
import uos
from sdcard import sdcard

cs = machine.Pin(15, machine.Pin.OUT)


spi = machine.SPI(
    1,
    baudrate=1000000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=machine.SPI.MSB,
    sck=machine.Pin(10),
    mosi=machine.Pin(11),
    miso=machine.Pin(12),
)

# Initialize SD card
sd = sdcard.SDCard(spi, cs)


vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

with open("/sd/test01.txt", "w") as file:
    file.write("Hello, SD World!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)
