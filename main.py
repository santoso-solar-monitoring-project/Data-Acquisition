import time
import csv
from monitor.mppt_packages.i2c import I2C
from monitor.mppt_packages.mppt import MPPT, Modes
from monitor.mppt_packages.adc import ADC_Reader as ADC
I2C = I2C()
adc = ADC(address=0x48, continuous=False)
MPPT = MPPT(adc, mode=Modes.DEBUG)
switch = 0

CSV_FILE = open('log.csv', 'w', newline='')
CSV_WRITER = csv.writer(CSV_FILE)
CSV_WRITER.writerow(['Voltage', 'Current', 'PWM', 'LED'])

while True:
    usr_input = input("Input Command:")
    while True:
        # S for switch
        if usr_input == 's':
            print('..switching modes..')
            switch = (switch+1)%3
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
            while count < 100:
                print('..measuring panel..')
                led, pwm = MPPT.track()
                I2C.send_data(led,pwm)
                voltage, current = adc.sample()
                CSV_WRITER.writerow([voltage, current, pwm, led])
                time.sleep(0.5)
                count += 1
        elif usr_input == 'test':
            I2C.set_pwm(round(255*0.6))
            count = 0
            adc_fails = 0
            uno_fails = 0
            measurement_fails = 0
            while count < 100:
                led, pwm = MPPT.track(test=True)
                uno_fail = I2C.send_data(led, pwm)
                time.sleep(0.2)

                count += 1
                #adc_fails += adc_fail
                uno_fails += uno_fail
                #measurement_fails += measurement_fail
                print("COUNT: ", count)
            print("\n---- TEST RESULTS ----")
            #print("\tADC FAILURES: ", adc_fails)
            print("\tUNO FAILURES: ", uno_fails)
            #print("\tOUT OF BOUNDS MEASUREMENTS: ", measurement_fails)
        elif usr_input == "set":
            pwm = int(input("Desired PWM: "))
            I2C.set_pwm(pwm)
        else:
            print("Invalid input. Try again.")
        usr_input = input("Input Command:")



