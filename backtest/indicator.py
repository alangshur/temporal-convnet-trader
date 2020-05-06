import numpy as np
import config



class Indicator:
    def update(self, data):
        raise NotImplementedError



class SimpleMovingAverage(Indicator):
    def __init__(self, period=10):

        # init base class
        super(SimpleMovingAverage, self).__init__()

        # init indicator values
        self.period = period
        self.average = None
        self.moving_values = None


    def update(self, data):
        average_val = None

        # compute SMA
        if data.shape[0] >= self.period:
            self.moving_values = np.copy(data[-self.period:, config.ROW_INDICES.CLOSE])
            self.average = np.mean(self.moving_values)
            average_val = self.average

        return average_val
