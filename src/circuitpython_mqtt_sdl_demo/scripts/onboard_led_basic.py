from time import sleep

import board
import digitalio

onboard_led = digitalio.DigitalInOut(board.LED)  # only works for Pico W
onboard_led.direction = digitalio.Direction.OUTPUT

onboard_led.value = True
sleep(1)
onboard_led.value = False
