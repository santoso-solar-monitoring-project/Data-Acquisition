import curses
from curses import wrapper
import time
import multiprocessing



class CursesClient(object):

	def __init__(self):
		self.KEY_BACKSPACE = 263
		self.KEY_ENTER = 10

		self.ACCEPTABLE_COMMANDS = ["observe",
					"conductance",
					"debug"]

		self._command_string = None
		self._data_strings = None
		self._curses_lock = None
		self._error_strings = None

	def run(self, command_string, data_strings, curses_lock):
		self._command_string = command_string
		self._data_strings = data_strings
		self._curses_lock = curses_lock

		wrapper(self.main)

	def format_output(self, input_string):
		output = ">" + input_string + "\n"

		output += "\n"
		for line in self._error_strings:
			output += (line + "\n")
		output += "\n"
		with self._curses_lock:
			for line in self._data_strings:
				output += (line + "\n")
		return output

	def update_command(self, command):
		self._error_strings = [""]
		with self._curses_lock:
			while len(self._command_string) > 0:
				del self.command_string[0]
			self._command_string.append(command)

	def main(self, stdscr):
		stdscr.clear()
		stdscr.nodelay(True)
		output = ""
		input_string = ""
		self._error_strings = [""]
		while True:
			c = stdscr.getch()
			stdscr.erase()

			if c == self.KEY_BACKSPACE:
				input_string = input_string[:-1]
			elif c == self.KEY_ENTER:
				command = input_string.lower()
				if command == "q":
					break
				elif command == "?":
					self._error_strings = ["Here are a list of valid commands..."]
					for line in self.ACCEPTABLE_COMMANDS:
						self._error_strings.append("\t"+line)
				elif command in self.ACCEPTABLE_COMMANDS:
					self.update_command(command)
				else:
					self._error_strings = ["Not a valid command. Press ? for a list of valid commands"]
				input_string = ""
			elif 0 <= c <= 255:
				input_string += chr(c)
			output = self.format_output(input_string)
			stdscr.addstr(output)
