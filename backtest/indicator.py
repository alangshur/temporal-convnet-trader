import numpy as np
from config import ROW_INDICES



class Indicator:
    def update(self, data):
        raise NotImplementedError



class SimpleMovingAverage(Indicator):
    def __init__(self, period=10, index=ROW_INDICES.CLOSE):

        # init base class
        super(SimpleMovingAverage, self).__init__()

        # init indicator values
        self.period = period
        self.index = index
        self.average = None


    def update(self, data):
        
        # compute SMA
        if data.shape[0] >= self.period:
            values = data[-self.period:, self.index]
            self.average = np.mean(values)

        return self.average



class ExpontentialMovingAverage(Indicator):
    def __init__(self, period=10, smoothing=2, index=ROW_INDICES.CLOSE):

        # init base class
        super(ExpontentialMovingAverage, self).__init__()

        # init indicator values
        self.period = period
        self.smoothing = smoothing
        self.index = index
        self.update_rate = smoothing / (1 + period)
        self.average = None


    def update(self, data):

        # initialize EMA as SMA
        if data.shape[0] >= self.period and self.average is None:
            values = data[-self.period:, self.index]
            self.average = np.mean(values)
        
        # compute EMA
        elif self.average is not None:
            value = data[-1, self.index]
            self.average = value * self.update_rate + \
                self.average * (1 - self.update_rate)

        return self.average