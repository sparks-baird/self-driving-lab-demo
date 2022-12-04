from time import sleep

from machine import PWM, Pin

pump = PWM(Pin(0))


def run(pump, power):
    assert 0 <= power <= 1, "power must be between 0 and 1"
    pump.freq(20000)
    pump.duty_u16(round(65535 * power))


for power in [0, 0.25, 0.5, 0.75, 1]:
    print(power)
    run(pump, power)
    sleep(0.5)

run(pump, 0.0)
