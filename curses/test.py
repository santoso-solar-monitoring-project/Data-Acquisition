import curses
from curses import wrapper
import time


def format_output(input_string, error_strings, data_strings):
	output = ">" + input_string + "\n"
	
	output += "\n"
	for line in error_strings:
		output += (line + "\n")
	output += "\n"
	for line in data_strings:
		output += (line + "\n")
	return output
		
KEY_BACKSPACE = 263
KEY_ENTER = 10

def main(stdscr):
	stdscr.clear()
	stdscr.nodelay(True)
	output = ""
	input_string = ""
	error_strings = []
	data_strings = []
	while True:
		c = stdscr.getch()
		stdscr.clear()
		data_strings = []
		if c == ord('q'):
			break
		elif c == KEY_BACKSPACE:
			input_string = input_string[:-1]
		elif c == KEY_ENTER:
			command = input_string
			if command != "set":
				error_strings = ["Not valid command. Press ? for a list of valid commands"]
			else:
				error_strings = []
			input_string = ""
		elif 0 <= c <= 255:
			input_string += chr(c)
		else:
			#stdscr.addstr(str(c))
			pass	
		data_strings.append(str(time.time() % 10))
		output = format_output(input_string, error_strings, data_strings)
		stdscr.addstr(output)
	
wrapper(main)
