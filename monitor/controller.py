from mppt_packages import adc, mppt, pusher
from multiprocessing import Process, Manager, Lock, freeze_support
import signal, sys, time

'''
A signal handler for when you press Ctrl+class
Cleans up the processes before exiting
'''
def signal_handler(signum, frame):
    print("\nShutting down processes...")
    panel_process.terminate()
    web_process.terminate()
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
    ADC_p1 = adc.ADC_Reader(address=0x48, continuous=True)
    ADC_p2 = adc.ADC_Reader(address=0x49, continuous=True)
    ADC_p3 = adc.ADC_Reader(address=0x4A, continuous=True)
    MPPT = mppt.MPPT(ADC_p1, mode=mppt_mode)

    for i in range(10):
        values = (ADC_p1.sample(), ADC_p2.sample(), ADC_p3.sample())
        print("Voltage\t\tCurrent")
        ready_flag.value = 0
        for j in range(3):
            with voltage_lock, current_lock:
                voltages[j] = values[j][0]
                currents[j] = values[j][1]
            print("{0:.5f}\t\t{1:.5f}".format(voltages[j], currents[j]))
        ready_flag.value = 1
        time.sleep(2)
    pass


'''
An object to help upload_values' Pusher bundle data
'''
class Data(object):
    def __init__(self, voltage, current, power=0.0):
        self.voltage = voltage
        self.current = current
        self.power = power


'''
Uploads the data to the web server
voltages and currents parameters need to be from the Manager class
'''
def upload_values(voltages, currents, ready_flag):
    for i in range(10):
        while not ready_flag.value:
            print("Upload waiting...")
            time.sleep(0.1)
        with voltage_lock, current_lock:
            data = []
            for j in range(len(voltages)):
                data.append(Data(voltages[j], currents[j]))
        pusher.push_data(data)
        print("Uploading panel #{0}'s values: {1:.1f}, {2:.1f}".format(j+1, voltages[j], currents[j]))
        ready_flag.value = 0
        time.sleep(1)

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
        print("Using DEBUG mode...")
        mode = mppt.Modes.DEBUG

    if 'win' in sys.platform:
        freeze_support() #ONLY FOR WINDOWS SYSTEMS

    value_manager = Manager()
    shared_voltages = value_manager.list([0.0, 0.0, 0.0])
    shared_currents = value_manager.list([0.0, 0.0, 0.0])
    ready = value_manager.Value('i', 0) #A ready flag that tells the upload process to wait until new values are ready

    panel_process = Process(target=run_monitor, args=(shared_voltages, shared_currents, mode, ready))
    web_process = Process(target=upload_values, args=(shared_voltages, shared_currents, ready))
    panel_process.start()
    web_process.start()


    panel_process.join()
    web_process.join()

'''
TODO:
-Determine if the MPPT panel needs its own process
-Implement processes
-Ensure the processes are being run on different cores
-Test the web process
'''
