import time
import board
import busio
import adafruit_bme680

i2c = busio.I2C(scl=board.GP17, sda=board.GP16)
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

sensor.sea_level_pressure = 1013.25

while True:
    print(f"temp: {sensor.temperature:.2f} C")
    print(f"humidity: {sensor.humidity:.2f} %")
    print(f"pressure: {sensor.pressure:.2f} ")
    
    time.sleep(2)
