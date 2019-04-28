from .adc import ADC_Reader
from enum import Enum
from multiprocessing import Value

class Modes(Enum):
    DEBUG = -1
    OBSERVE = 0
    CONDUCTANCE = 1


class MPPT(object): #Classes without a defined (base_class) are abstract

    MAX_POWER = 400

    def __init__(self, adc_object=None, mode=Modes.DEBUG):
        self._v = 0
        self._i = 0
        self._p = 0
        self._v_old = 0
        self._i_old = 0
        self._p_old = 0
        if type(mode) == type(0): #It's an int, we need a Mode
            self._mode = Modes(mode)
        else:
            self._mode = mode
        self._debug = 0
        self._count = 0
        if not adc_object:
            self._adc = ADC_Reader(address=0x48)
        else:
            self._adc = adc_object

        self._test = False
        self._adc_error = 0
        self._measurement_error= 0

    def switch(self, mode):
        if type(mode) == type(0): #It's an int, we need a Mode
            self._mode = Modes(mode)
        else:
            self._mode = mode
        if self._mode == Modes.DEBUG:
            print("MPPT now in Debug Mode")
        # P&O
        elif self._mode == Modes.OBSERVE:
            print("MPPT now in Perturb and Observe Mode")
        # Inc Cond
        elif self._mode == Modes.CONDUCTANCE:
            print("MPPT now in Incremental Conductance Mode")

    def track(self, test=False, voltage=None, current=None):
        # Initialize error tracking values
        self._test = test
        self._adc_error = 0
        self._measurement_error = 0

        _voltage = voltage
        _current = current

        # Debug Mode
        if self._mode == Modes.DEBUG:
            return self.mppt_debug()
        # P&O
        elif self._mode == Modes.OBSERVE:
            return self.mppt_perturb_observe(voltage=_voltage, current=_current)
        # Inc Cond
        elif self._mode == Modes.CONDUCTANCE:
            return self.mppt_incremental_conductance(voltage=_voltage, current=_current)

    def read_new_values(self):
        # Zach do here the adc stuff kinda
        # self._voltage = read
        # self._current = read
        # self._power = self._voltage * self._current
        try:
            self._v, self._i = self._adc.sample()
            '''
            if self._v < 0 or self._v > 40:
                self._measurement_error += 1

            if self._i < 0 or self._i > 10:
                self._measurement_error += 1

            if self._measurement_error > 0:
                print("...error measuring data...")
            '''
            self._v = max(min(self._v, 40.), 0.)
            self._i = max(min(self._i, 10.), 0.)
        except IOError:
            print("...Using old values...")
            self._v = self._v_old
            self._i = self._i_old
            self._adc_error = 1

        self._p = self._v * self._i
        print("Voltage\tCurrent\tPower")
        print("{0[0]:.3f}\t{0[1]:.3f}\t{0[2]:.3f}\n".format((self._v, self._i, self._p)))

    def update_old_values(self):
        self._v_old = self._v
        self._i_old = self._i
        self._p_old = self._p
        self._v = 0
        self._i = 0
        self._p = 0

    def led_gauge_level(self):
        level = round(5 * self._p / self.MAX_POWER)
        return level

    def mppt_debug(self):
        self._debug += 1
        self._debug %= 3
        ret = self._debug - 1
        led = self._count % 6
        self._count += 1
        print('DEBUG_MODE:\nLED LEVEL - {}\nPWM COMMAND - {}'.format(led, ret))
        return led, ret

    def mppt_perturb_observe(self, voltage=None, current=None):
        if(voltage != None and current != None):
            self._v = voltage
            self._i = current
        else:
            self.read_new_values()

        if self._p > self._p_old:
            if self._v > self._v_old:
                ret = 1
            else:
                ret = -1
        else:
            if self._v > self._v_old:
                ret = -1
            else:
                ret = 1

        led = self.led_gauge_level()
        print('PO_MODE:\nLED LEVEL - {}\nPWM COMMAND - {}'.format(led, ret))
        self.update_old_values()
        if self._test:
            return led, ret, self._adc_error, self._measurement_error
        else:
            return led, ret

    def mppt_incremental_conductance(self, voltage=None, current=None):
        if(voltage != None and current != None):
            self._v = voltage
            self._i = current
        else:
            self.read_new_values()

        if self._v == self._v_old:
            if self._i == self._i_old:
                ret = 0
            elif self._i > self._i_old:
                ret = 1
            else:
                ret = -1
        else:
            if round(self._v, 3) == 0.0:
                ret = 1
            else:
                print(self._v)
            di_dv = (self._i - self._i_old) / (self._v - self._v_old)
            try:
                var = -self._i / self._v
            except:
                print("in the exception")
                ret = 1
                led = 0
                self.update_old_values()
                return led, ret
            #print("i: {}\tv: {}".format(self._i, self._v))
            #print("di_dv: {}".format(di_dv))
            #print("-i/v: {}".format(var))
            if di_dv == var:
                ret = 0
            elif di_dv > var:
                ret = 1
            else:
                ret = -1
        led = self.led_gauge_level()
        print('IC_MODE:\nLED LEVEL - {}\nPWM COMMAND - {}'.format(led, ret))
        self.update_old_values()
        if self._test:
            return led, ret, self._adc_error, self._measurement_error
        else:
            return led, ret

    def run(self):
        #Implement this to work with controller.py's run_monitor()
        #It needs to return the voltage, current, or a shutdown command
        #Like "return (voltage,current,"")" versus "return (0,0,"shutdown")"
        pass

if __name__ == "__main__": #This is only called if you start it with "python3 mppt.py", not if you're calling it from another file
    mppt = MPPT(adc=adc.ADC_Reader())
    #Do something here
