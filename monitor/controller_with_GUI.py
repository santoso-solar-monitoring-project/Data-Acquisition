from mppt_packages import adc, mppt, pusher, i2c
from multiprocessing import Process, Manager, Lock, freeze_support
import signal, sys, time, os
from pynput.keyboard import Key, Listener

'''
A signal handler for when you press Ctrl+class
Cleans up the processes before exiting
'''
def signal_handler(signum, frame):
    print("\nShutting down processes...")
    panel_process.terminate()
    web_process.terminate()
    control_process.terminate()
    raise KeyboardInterrupt("Killed processes, exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


'''
Locks to make sure the web process doesn't send data that's being changed
'''
voltage_lock = Lock()
current_lock = Lock()


'''
This function will be called as a Process later
Assumes the ADC at 0x48 is connected to the MPPT panel
'''
def run_monitor(voltages, currents, mppt_mode, ready_flag):
    ADC_p1 = adc.ADC_Reader(address=0x48, continuous=False, ads1115=False) #MPPT
    ADC_p2 = adc.ADC_Reader(address=0x49, continuous=False, ads1115=False) #Load only
    ADC_p3 = adc.ADC_Reader(address=0x4A, continuous=False, ads1115=False) #Open circuit
    MPPT = mppt.MPPT(ADC_p1, mode=mppt_mode)
    I2C_bus = i2c.I2C()

    while True:
        MPPT.switch(mode=mppt_mode)
        #print("Getting values...")
        values = (ADC_p1.sample(), ADC_p2.sample(), ADC_p3.sample())
        #print("Voltage\t\tCurrent")
        ready_flag.value = 0
        for j in range(len(values)):
            with voltage_lock, current_lock:
                voltages[j] = values[j][0]
                currents[j] = values[j][1]
            #print("{0:.5f}\t\t{1:.5f}".format(voltages[j], currents[j]))
        led, pwm = MPPT.track(voltage=values[0][0], current=values[0][1]) #Set up MPPT to accept this information
        I2C_bus.send_data(led,pwm)
        ready_flag.value = 1
        print("\033[4;0HMPPT Voltage\tMPPT Current\tMPPT Power\n{0:0.3f}\t\t{1:0.3f}\t\t{2:0.3f}".format(voltages[0], currents[0], voltages[0]*currents[0]))
        sys.stdout.flush()
        time.sleep(0.5)
    pass


'''
An object to help upload_values' Pusher bundle data
'''
class Data(object):
    def __init__(self, voltage, current, time):
        self.voltage = voltage
        self.current = current
        self.time = time


'''
Uploads the data to the web server
voltages and currents parameters need to be from the Manager class
'''
def upload_values(voltages, currents, ready_flag):
    for i in range(120):
        while not ready_flag.value:
            #print("Upload waiting...")
            time.sleep(0.1)
        with voltage_lock, current_lock:
            data = []
            data_time = time.time()*1000
            for j in range(len(voltages)):
                data.append(Data(voltages[j], currents[j], data_time))
        #pusher.push_data(data)
        #print("Uploading panel #{0}'s values: {1:.1f}, {2:.1f}".format(j+1, voltages[j], currents[j]))
        ready_flag.value = 0
        time.sleep(0.4)

'''
Displays the Curse client on the screen and controls the MPPT mode
Also displays real-time voltage, current, and power
'''
def display_control(mode, keyboard_ready):
    with Listener(on_press=keyboard_listener) as listener:
        listener.join()
        print("Keyboard listener closed")

keyboard_input = []

def keyboard_listener(key):
    if key == Key.enter:
        input_string = "".join(keyboard_input).lower()
        if "perturb" in input_string:
            mppt_mode = mppt.Modes.OBSERVE
        elif "increment" in input_string:
            mppt_mode = mppt.Modes.CONDUCTANCE
        elif "debug" in input_string:
            mppt_mode = mppt.Modes.DEBUG
        else:
            print("\n'%s' is not a valid mode, please enter a valid mode...")
            time.sleep(1)
            refresh_screen()
    elif key == Key.backspace:
        try:
            del keyboard_input[-1]
            sys.stdout.write('\b')
            sys.stdout.flush()
        except IndexError:
            pass
    elif key == Key.esc:
        sys.exit(0)
    else:
        keyboard_input.append(key)
        print('\033[1;{0}H{1}'.format(55+len(keyboard_input),key), end='')

def refresh_screen():
    if 'win' in sys.platform:
        os.system('cls')
    else:
        os.system('clear')
    print('\033[0;0HCurrent mode: {0}\n'.format(["Perturb and Observe", "Incremental Conductance", "Debug"][mppt_mode]))
    print("\033[1;0HPlease enter the MPPT mode you would like to switch to: ", end='')
    sys.stdout.flush()

if __name__ == "__main__":
    if(len(sys.argv) > 1): #They set flags
        args = sys.argv[1:] #Ignore the filename (arg 0)
        if args[0] == '--help':
            print("\nPlease enter a mode when running the script by setting the 'mode=' flag.\n")
            print("Modes you can select:\nDebug: \"DEBUG\"\nObserve and Perturb: \"OBSERVE\"\nIncremental Conductance: \"CONDUCTANCE\"")
            print("Ex. 'python3 controller.py mode=OBSERVE'\n")
            sys.exit(0)
        elif 'mode' in args[0]:
            mode_arg = args[0][5:]
            if mode_arg.lower() == 'observe':
                mode = mppt.Modes.OBSERVE
            elif mode_arg.lower() == 'conductance':
                mode = mppt.Modes.CONDUCTANCE
            else:
                print("Invalid mode %s, please enter a valid mode." % (mode_arg))
                sys.exit(0)
    else:
        #print("Using DEBUG mode...")
        mode = mppt.Modes.CONDUCTANCE

    if 'win' in sys.platform:
        freeze_support() #ONLY FOR WINDOWS SYSTEMS
        os.system('cls')
    else:
        os.system('clear')
    value_manager = Manager()
    shared_voltages = value_manager.list([0.0, 0.0, 0.0])
    shared_currents = value_manager.list([0.0, 0.0, 0.0])
    ready = value_manager.Value('i', 0) #A ready flag that tells the upload process to wait until new values are ready

    panel_process = Process(target=run_monitor, args=(shared_voltages, shared_currents, mode, ready))
    web_process = Process(target=upload_values, args=(shared_voltages, shared_currents, ready))
    control_process = Process(target=display_control, args=(mode, ready))
    refresh_screen()
    control_process.start()
    panel_process.start()
    web_process.start()



    panel_process.join()
    web_process.join()
    control_process.join()

'''
TODO:
-Determine if the MPPT panel needs its own process
-Implement processes)
-Ensure the processes are being run on different cores
-Test the web process
'''
