import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADC
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
	the shunt resistor
	"""

	def __init__(self, address=0x48):
		self.address = address
		self.i2c_bus = busio.I2C(board.SCL, board.SDA)
		self.adc = ADC.ADS1015(i2c=self.i2c_bus, address=self.address)
		self.channels = [AnalogIn(self.adc, ADC.P0), AnalogIn(self.adc, ADC.P1),
		 				AnalogIn(self.adc, ADC.P2), AnalogIn(self.adc, ADC.P3)]
		self.differentials = [AnalogIn(self.adc, ADC.P0, ADC.P1), AnalogIn(self.adc, ADC.P2, ADC.P3)]

	def read_voltage(self, chan):
		return self.channels[chan].voltage

	def read_raw(self, chan):
		return self.channels[chan].value

	def sample(self):
		resistance = 0.01
		voltage = self.channels[2].voltage
		current = self.differentials[0]/resistance
		return (voltage, current)


if __name__ == "__main__":
	adc = ADC_Reader()
	print("\t\tVoltage\t\tRaw Value")
	while True:
		for i in range(4):
			print("Channel {}:\t{:.5f}\t\t{}".format(i, adc.read_voltage(i), adc.read_raw(i)))
		#print(adc.sample())
		print("")
		time.sleep(1)
