import time
from board import SCL, SDA
import busio
import adafruit_ads1x15.ads1015 as ADC
import adafruit_ads1x15.ads1115 as ADC_1115
from adafruit_ads1x15.analog_in import AnalogIn

class ADC_Reader(object):
    """
    The ADC Reader class allows for the user to easily set up a connection to
    the ADS1015

    The default address for the ADS1015 is 0x48, but you can change which ADS
    you are connected to by specifying address in __init__

    Example: adc = ADC_Reader(address=0x49)
         voltage = adc.read_voltage()

    read_voltage returns the voltage formatted as a floating integer
    read_raw returns the raw data value the ADS reads

    sample assumes you have the positive side of the shunt resistor plugged into
    A0 and the negative side in A1, and the open circuit voltage plugged into
    A2
    It will return the voltage from the open circuit and the current going over
    the shunt resistor, as well as the average voltage and current specified
    from the number of samples
    """

    def __init__(self, address=0x48, continuous=False, rate=3300, ads1115=False):
        self.address = address
        self.i2c_bus = busio.I2C(SCL, SDA, frequency=400000) #Up to 400kHz, look at https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/
        self.continuous = continuous
        self.rate = rate
        self._avg_voltage_old = 0
        self._avg_current_old = 0
        self._voltage_old = 0
        self._current_old = 0
        if continuous:
            if ads1115:
                self.adc = ADC_1115.ADS1115(i2c=self.i2c_bus, gain=2/3, address=self.address, data_rate=min(self.rate, 860), mode=ADC_1115.Mode.CONTINUOUS)
            else:
                self.adc = ADC.ADS1015(i2c=self.i2c_bus, gain=2/3, address=self.address, data_rate=self.rate, mode=ADC.Mode.CONTINUOUS)
        else:
            if ads1115:
                self.adc = ADC_1115.ADS1115(i2c=self.i2c_bus, gain=2/3, address=self.address, data_rate=min(self.rate, 860), mode=ADC_1115.Mode.SINGLE)
            else:
                self.adc = ADC.ADS1015(i2c=self.i2c_bus, gain=2/3, address=self.address, mode=ADC.Mode.SINGLE)
        self.channels = [AnalogIn(self.adc, ADC.P0), AnalogIn(self.adc, ADC.P1),
                        AnalogIn(self.adc, ADC.P2), AnalogIn(self.adc, ADC.P3)]
        self.differentials = [AnalogIn(self.adc, ADC.P0, ADC.P1), AnalogIn(self.adc, ADC.P2, ADC.P3)]

    def read_voltage(self, chan, _gain=2/3):
        self.adc.gain = _gain
        return self.channels[chan].voltage

    def read_raw(self, chan, _gain=2/3):
        self.adc.gain = _gain
        return self.channels[chan].value

    def read_differential(self, pair, _gain=2/3):
        self.adc.gain = _gain
        return self.differentials[pair].voltage

    def sample(self, frequency=3300, number_of_samples=20):
        resistance = 0.01
        #Single shot sampling
        if not self.continuous:
            sleep_time = 1.0/frequency
            avg_voltage = 0
            avg_current = 0
            for i in range(number_of_samples):
                try:
                    avg_voltage = (avg_voltage*i + self.channels[2].voltage)/(i+1)
                    self.adc.gain = 8 #The shunt resistor probably won't go over 100mV so this works for +/- 1024mV
                    #avg_current = (avg_current*i + self.differentials[0].voltage/resistance)/(i+1)
                    avg_current = (avg_current*i + (self.read_raw(0)/1024.0-self.read_raw(1)/1024.0)/resistance)/(i+1)
                    self.adc.gain = 2/3
                except IOError:
                    print("Error sampling from the ADC 0x%.2X" % (self.address))
                    time.sleep(sleep_time)
                    self.adc.gain = 1
            self._avg_voltage_old = avg_voltage
            self._avg_current_old = avg_current
            return (avg_voltage*11, avg_current)
        #Continuous sampling
        try:
            voltage = (self.adc.read(2)/4096)*6.144
            current = (self.adc.read(0, is_differential=True)/4096)*6.144/resistance
            self.adc.stop_adc()
            self._voltage_old = voltage
            self._current_old = current
            return (voltage*11, current)
        except IOError:
            return (self._voltage_old*11, self._current_old)


if __name__ == "__main__":
    _address = 0x48
    adcs = []
    for i in range(3):
        try:
            adc = ADC_Reader(address=_address+i)
            print("Found ADC at 0x%.2X" % (_address+i))
        except Exception:
            try:
                adc = ADC_Reader(address=_address+i, ads1115=True)
            except Exception:
                continue
        adcs.append(adc)
    print("\t\tVoltage\t\tCurrent")
    while True:
        for i in range(len(adcs)):
            try:
                print("ADC 0x%.2X" % (adcs[i].address))
                print("Sample:\t\t{0[0]:.5f}\t\t{0[1]:.5f}".format(adcs[i].sample()))
                #time.sleep(0.15)
                print("Channel 0:\t{0:.5f}".format(adcs[i].channels[0].voltage))
                #time.sleep(0.15)
                print("Channel 1:\t{0:.5f}".format(adcs[i].channels[1].voltage))
                #time.sleep(0.15)
                print("Channel 2:\t{0:.5f}".format(adcs[i].channels[2].voltage))
                #time.sleep(0.15)
                #adcs[i].adc.gain = 8
                #time.sleep(0.15)
                print("Differential 0:\t{0:.5f}".format(adcs[i].differentials[0].voltage))
                #time.sleep(0.15)
                #adcs[i].adc.gain = 2/3
            except IOError:
                print("0x%.2X crapped out" % (adcs[i].address))
            print("")
        print("\n---------------------------------------\n")
        time.sleep(1)
