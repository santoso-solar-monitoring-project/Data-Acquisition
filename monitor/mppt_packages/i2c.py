import smbus2


class I2C:

    def __init__(self, address=0x04):
        # for RPI version 1, use “bus = smbus.SMBus(0)”
        self._bus = smbus2.SMBus(bus=1)

        # This is the address we setup in the Arduino Program
        self._address = address

    def send_data(self, led, pwm):
        led = max(min(led, 15), 0)
        pwm = max(min(pwm, 1), -1)
        value = (pwm + 1) * 16 + led
        uno_error = 0
        try:
            self._bus.write_byte(self._address, int(value))
        except OSError:
            print("...Wasnt able to reach Arduino...")
            uno_error = 1
        # bus.write_byte_data(address, 0, value)
        return uno_error

    def set_pwm(self, pwm):
        pwm = max(min(pwm, 255), 0)
        try:
            self._bus.write_byte(self._address, int(255))
            self._bus.write_byte(self._address, int(pwm))
        except:
            print("...pwm set failed...")

    def read_data(self):
        number = self._bus.read_byte(self._address)
        # number = bus.read_byte_data(address, 1)
        return number
