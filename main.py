from monitor.i2c import I2C
from monitor.mppt import MPPT
I2C = I2C()
MPPT = MPPT()
switch = 0

while True:
    usr_input = input("Input Command:")
    while True:
        # S for switch
        if usr_input == 's':
            print('..switching modes..')
            switch += 1
            switch %= 3
            MPPT.switch(switch-1)
        # M for measure
        elif usr_input == 'm':
            print('.. measuring panel..')
            led, pwm = MPPT.track()
            I2C.send_data(led,pwm)
        # L for log
        elif usr_input == 'l':
            print('.. printing log..')
        else:
            print("Invalid input. Try again.")
        usr_input = input("Input Command:")



