"""CircuitPython Essentials NeoPixel example

This example code uses: Maker Pi Pico ;; Reference: www.cytron.io/p-maker-pi-pico

www.cytron.io/p-maker-pi-pico
https://docs.circuitpython.org/projects/neopixel/en/latest/api.html

https://stackoverflow.com/questions/67363258/configure-mypy-in-vscode-to-enforce-type-hinting,
to deal with OOM
"""
import time

import board
import neopixel

pixel_pin = board.GP28
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.35, auto_write=False)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (50, 50, 50)


for _ in range(1):
    pixels.fill(RED)
    pixels.show()
    time.sleep(1)  # Increase or decrease to change the speed of the solid color change.
    pixels.fill(GREEN)
    pixels.show()
    time.sleep(1)
    pixels.fill(BLUE)
    pixels.show()
    time.sleep(1)

    color_chase(RED, 0.2)  # Increase the number to slow down the color chase
    color_chase(YELLOW, 0.2)
    color_chase(GREEN, 0.2)
    color_chase(CYAN, 0.2)
    color_chase(BLUE, 0.2)
    color_chase(PURPLE, 0.2)

    rainbow_cycle(0.01)  # Increase the number to slow down the rainbow
    time.sleep(1)


pixels.deinit()
