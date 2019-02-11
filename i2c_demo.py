import smbus2
import time
# for RPI version 1, use “bus = smbus.SMBus(0)”
bus = smbus2.SMBus(bus=1)

# This is the address we setup in the Arduino Program
address = 0x04


def write_number(value):
    bus.write_byte(address, int(value))
    # bus.write_byte_data(address, 0, value)
    return -1


def read_number():
    number = bus.read_byte(address)
    # number = bus.read_byte_data(address, 1)
    return number

while True:
    var = input("Enter 1 – 9: ")
    if not var:
        continue

    write_number(var)
    print("RPI: Hi Arduino, I sent you {}".format(var))
    # sleep one second
    time.sleep(1)

    number = read_number()
    print("Arduino: Hey RPI, I received a digit {}".format(number))
