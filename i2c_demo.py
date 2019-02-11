import smbus
import time
# for RPI version 1, use “bus = smbus.SMBus(0)”
bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04


def write_number(value):
    bus.write_byte(address, value)
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
    print("RPI: Hi Arduino, I sent you ", var)
    # sleep one second
    time.sleep(1)

    number = readNumber()
    print("Arduino: Hey RPI, I received a digit ", number)
