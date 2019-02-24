import numpy as np


class ADC:

    def __init__(self, debug=True):
        if debug:
            self._samples = np.arange(1, 100)
            self._index = 0
        else:
            pass

    def read_sample(self):
        # Zach implement here
        pass
        sample = self._samples[self._index]
        self._index += 1
        self._index %= 100
        return sample
