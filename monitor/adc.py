import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADC
from adafruit_ads1x15.analog_in import AnalogIn

class ADC_Reader(object):
	"""
	The ADC Reader class allows for the user to easily set up a connection to the ADS1015

	The default address for the ADS1015 is 0x48, but you can change which ADS you are
	connected to by specifying address in __init__

	read_voltage returns the voltage formatted as a floating integer
	read_raw returns the raw data value the ADS reads
	"""

	def __init__(self, address=0x48):
		self.address = address
		self.i2c_bus = busio.I2C(board.SCL, board.SDA)
		self.adc = ADC.ADS1015(i2c=self.i2c_bus, address=self.address)
		self.channel = AnalogIn(self.adc, ADC.P0)

	def read_voltage(self):
		return self.channel.voltage

	def read_raw(self):
		return self.channel.value

if __name__ == "__main__":
	adc = ADC_Reader()
	print("Voltage\t\tRaw Value")
	while True:
		print("{:.5f}\t\t{}".format(adc.read_voltage(), adc.read_raw()))
		time.sleep(1)
