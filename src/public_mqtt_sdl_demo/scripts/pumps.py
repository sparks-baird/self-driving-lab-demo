from time import sleep

from machine import PWM, Pin

pumps = [PWM(Pin(i)) for i in range(4)]


def run(pump, power):
    assert 0 <= power <= 1, "power must be between 0 and 1"
    pump.freq(20000)
    pump.duty_u16(round(65535 * power))


for pump in pumps:
    run(pump, 0.5)
    sleep(1.0)
    run(pump, 0.0)
    sleep(1.0)

for power in [0, 0.25, 0.5, 0.75, 1]:
    for pump in pumps:
        print(power)
        run(pump, power)
        sleep(0.25)

[run(pump, 0.0) for pump in pumps]
