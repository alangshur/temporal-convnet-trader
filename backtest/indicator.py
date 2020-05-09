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


class MovingAverageConvDiv(Indicator):
    def __init__(self, short_period=12, long_period=26):

        # init base class
        super(MovingAverageConvDiv, self).__init__()

        # init indicator values
        self.ma_short = ExpontentialMovingAverage(period=short_period)
        self.ma_long = ExpontentialMovingAverage(period=long_period)


    def update(self, data):

        # update averages
        ma_short_val = self.ma_short.update(data)
        ma_long_val = self.ma_long.update(data)

        # compute MACD
        if ma_short_val is not None and ma_long_val is not None:
            return ma_short_val - ma_long_val
        else: return None



class RelativeStrengthIndex(Indicator):
    def __init__(self, period=14, index=ROW_INDICES.CLOSE):

        # init base class
        super(RelativeStrengthIndex, self).__init__()

        # init indicator values
        self.period = period
        self.index = index
        self.average_gain = None
        self.average_loss = None


    def update(self, data):
        
        # initialize RSI
        if data.shape[0] == self.period:
            pos, neg = [], []
            for i in range(1, self.period):
                ret = (data[i, self.index] - data[i - 1, self.index]) / data[i - 1, self.index]
                if ret > 0: pos.append(abs(ret))
                else: neg.append(abs(ret))
            self.average_gain = np.mean(pos)
            self.average_loss = np.mean(neg)            
            return 100 - 100 / (1 + self.average_gain / self.average_loss)

        # compute RSI
        elif data.shape[0] > self.period + 1:
            ret = (data[-1, self.index] - data[-2, self.index]) / data[-2, self.index]
            self.average_gain = ((self.period - 1) * self.average_gain + abs(max(ret, 0))) / self.period
            self.average_loss = ((self.period - 1) * self.average_loss + abs(min(ret, 0))) / self.period
            return 100 - 100 / (1 + self.average_gain / self.average_loss)

        else: return None
        
    

            
