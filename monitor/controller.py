from mppt_packages import adc
from mppt_packages import mppt
from multiprocessing import Process, Value
import signal, sys

def signal_handler(signum, frame):
    print("\nShutting down processes...")
    panel_process.terminate()
    web_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


shared_voltage = Value('d', 0.0)
shared_current = Value('d', 0.0)
shared_power = Value('d', 0.0) #Might not need this

def run_monitor(voltage, current):
    '''
    This function will be called as a Process later
    Assumes the ADC at 0x48 is connected to the MPPT panel

    '''
    ADC_p1 = adc.ADC(address=0x48)
    ADC_p2 = adc.ADC(address=0x49)
    ADC_p3 = adc.ADC(address=0x50)
    MPPT = mppt.MPPT(ADC_p1)
    pass


panel_process = Process(target=run_monitor, args=(shared_voltage, shared_current))
web_process = Process(target)

if __name__ == "__main__":
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
