from time import sleep

from machine import Pin

white_led = Pin(9, mode=Pin.OUT)
# white_led2 = Pin(8, mode=Pin.OUT)

white_led.on()
# white_led2.on()
sleep(2.0)
white_led.off()
# white_led2.off()
