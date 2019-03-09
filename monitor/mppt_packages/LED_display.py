from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685 as PWM

class LED(object):
    def __init__(self, pwm_address=0x40, pwm_frequency=50000):
        self.address = pwm_address
        self.frequency = pwm_frequency
        self.i2c_bus = busio.I2C(SCL, SDA, frequency=400000)
        self.pwm = PWM(self.i2c_bus, address=pwm_address) #Don't touch reference_clock_speed unless you give the PWM a different clock for some reason
        self.pwm.frequency = pwm_frequency
        for channel in self.pwm.channels:
            channel.duty_cycle = 0x0

    def set_duty_cycle(self, channel, _duty_cycle): #Should _duty_cycle be 0-100 or 0-65535?
        self.pwm.channels[channel].duty_cycle = _duty_cycle
