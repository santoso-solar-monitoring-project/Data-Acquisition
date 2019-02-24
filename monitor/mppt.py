from .adc import ADC


class MPPT:

    MAX_POWER = 400

    def __init__(self, mode=-1):
        self._v = 0
        self._i = 0
        self._p = 0
        self._v_old = 0
        self._i_old = 0
        self._p_old = 0
        self._mode = mode
        self._debug = 0
        self._count = 0
        self._adc = ADC()

    def switch(self, mode):
        self._mode = mode
        if self._mode == -1:
            print("MPPT now in Debug Mode")
        # P&O
        elif self._mode == 0:
            print("MPPT now in Perturb and Observe Mode")
        # Inc Cond
        elif self._mode == 1:
            print("MPPT now in Incremental Conductance Mode")

    def track(self):
        # Debug Mode
        if self._mode == -1:
            return self.mppt_debug()
        # P&O
        elif self._mode == 0:
            return self.mppt_perturb_observe()
        # Inc Cond
        elif self._mode == 1:
            return self.mppt_incremental_conductance()

    def read_new_values(self):
        # Zach do here the adc stuff kinda
        # self._voltage = read
        # self._current = read
        # self._power = self._voltage * self._current
        self._adc.read_sample()
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
