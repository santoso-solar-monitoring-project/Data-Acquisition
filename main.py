import time
from monitor.mppt_packages.i2c import I2C
from monitor.mppt_packages.mppt import MPPT, Modes
from monitor.mppt_packages.adc import ADC_Reader as ADC
I2C = I2C()
adc = ADC()
MPPT = MPPT(adc, mode=Modes.DEBUG)
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
        elif usr_input == 'loop':
            count = 0
            while(count < 100):
                print('..measuring panel..')
                led, pwm = MPPT.track()
                I2C.send_data(led,pwm)
                time.sleep(0.5)
                count += 1
        else:
            print("Invalid input. Try again.")
        usr_input = input("Input Command:")



