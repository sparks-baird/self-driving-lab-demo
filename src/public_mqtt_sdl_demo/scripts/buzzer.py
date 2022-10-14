from time import sleep

from machine import PWM, Pin

buzzer = PWM(Pin(18))


def chime_on(power=0.02):
    for i in [100, 500, 900]:
        buzzer.freq(i)
        buzzer.duty_u16(round(65535 * power))
        sleep(0.15)
    buzzer.duty_u16(0)


def chime_off(power=0.02):
    for i in [900, 500, 100]:
        buzzer.freq(i)
        buzzer.duty_u16(round(65535 * power))  # 30% of 65535
        sleep(0.15)
    buzzer.duty_u16(0)


chime_on()

sleep(1.0)

chime_off()
