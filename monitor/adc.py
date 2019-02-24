#import numpy as np


class ADC:

    def __init__(self, debug=True):
        if debug:
            self._samples = [1,2,3,4,5,6,7,8,9,10]
#np.arange(1, 100)
            self._index = 0
        else:
            pass

    def read_sample(self):
        # Zach implement here
        pass
        sample = self._samples[self._index]
        self._index += 1
        self._index %= 10
        return sample
