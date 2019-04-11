import smbus2


class I2C:

    def __init__(self, address=0x04):
        # for RPI version 1, use “bus = smbus.SMBus(0)”
        self._bus = smbus2.SMBus(bus=1)

        # This is the address we setup in the Arduino Program
        self._address = address

    def send_data(self, led, pwm):
        value = (pwm + 1) * 16 + led
        self._bus.write_byte(self._address, int(value))
        # bus.write_byte_data(address, 0, value)
        return -1

    def read_data(self):
        number = self._bus.read_byte(self._address)
        # number = bus.read_byte_data(address, 1)
        return number
