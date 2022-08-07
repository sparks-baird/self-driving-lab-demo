"""https://learn.pimoroni.com/article/getting-started-with-blinkt"""
import time
from blinkt import set_pixel, set_brightness, show, clear

set_brightness(0.05)

clear()
set_pixel(0, 255, 255, 255)
show()

time.sleep(5)

clear()
show()

1 + 1
