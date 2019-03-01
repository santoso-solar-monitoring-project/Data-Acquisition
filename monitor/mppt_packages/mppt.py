from .adc import ADC_Reader
from enum import Enum
from multiprocessing import Value

class Modes(Enum):
    DEBUG = -1
    OBSERVE = 0
    CONDUCTANCE = 1


class MPPT(object): #Classes without a defined (base_class) are abstract

    MAX_POWER = 400

    def __init__(self, mode=Modes.DEBUG, adc):
        self._v = 0
        self._i = 0
        self._p = 0
        self._v_old = 0
        self._i_old = 0
        self._p_old = 0
        self._mode = mode
        self._debug = 0
        self._count = 0
        self._adc = adc

    def switch(self, mode):
        self._mode = mode
        if self._mode == Modes.DEBUG:
            print("MPPT now in Debug Mode")
        # P&O
        elif self._mode == Modes.OBSERVE:
            print("MPPT now in Perturb and Observe Mode")
        # Inc Cond
        elif self._mode == Modes.CONDUCTANCE:
            print("MPPT now in Incremental Conductance Mode")

    def track(self):
        # Debug Mode
        if self._mode == Modes.DEBUG:
            return self.mppt_debug()
        # P&O
        elif self._mode == Modes.OBSERVE:
            return self.mppt_perturb_observe()
        # Inc Cond
        elif self._mode == Modes.CONDUCTANCE:
            return self.mppt_incremental_conductance()

    def read_new_values(self):
        # Zach do here the adc stuff kinda
        # self._voltage = read
        # self._current = read
        # self._power = self._voltage * self._current
        self._v, self._c = self._adc.sample()
        self._p = self._v * self._c
        pass

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

    def mppt_perturb_observe(self):
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
        return led, ret

    def mppt_incremental_conductance(self):
        self.read_new_values()

        if self._v == self._v_old:
            if self._i == self._i_old:
                ret = 0
            elif self._i > self._i_old:
                ret = 1
            else:
                ret = -1
        else:
            di_dv = (self._i - self._i_old) / (self._v - self._v_old)
            var = -self._i / self._v
            if di_dv == var:
                ret = 0
            elif di_dv > var:
                ret = 1
            else:
                ret = -1
        led = self.led_gauge_level()
        print('IC_MODE:\nLED LEVEL - {}\nPWM COMMAND - {}'.format(led, ret))
        self.update_old_values()
        return led, ret

    def run(self):
        #Implement this to work with controller.py's run_monitor()
        #It needs to return the voltage, current, or a shutdown command
        #Like "return (voltage,current,"")" versus "return (0,0,"shutdown")"
        pass

if __name__ == "__main__": #This is only called if you start it with "python3 mppt.py", not if you're calling it from another file
    mppt = MPPT(adc=adc.ADC_Reader())
    #Do something here
