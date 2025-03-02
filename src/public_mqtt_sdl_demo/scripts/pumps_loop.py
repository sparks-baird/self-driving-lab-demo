import random
from time import sleep

from machine import PWM, Pin

pumps = [PWM(Pin(i)) for i in range(4)]


def run(pump, power):
    assert 0 <= power <= 1, "power must be between 0 and 1"
    pump.freq(20000)
    pump.duty_u16(round(65535 * power))


def run_exp():
    for pump in pumps:
        pw = random.random()
        print(pw)
        run(pump, pw)
        sleep(10.25)


run_exp()
[run(pump, 0.0) for pump in pumps]
# while True:
#    run_exp()
##    sleep(50000)

#    [run(pump, 0.0) for pump in pumps]
#    sleep(50000)
