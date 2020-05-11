import numpy as np
from config import ROW_INDICES



class Indicator:
    def update(self, data):
        raise NotImplementedError
    

    def clear(self):
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

    
    def clear(self):
        self.average = None



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
    

    def clear(self):
        self.average = None



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


    def clear(self):
        self.ma_short.clear()
        self.ma_long.clear()



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
            if self.average_gain == 0: return 0.0
            elif self.average_loss == 0: return 100.0
            else: return 100 - 100 / (1 + self.average_gain / self.average_loss)

        else: return None
    
    
    def clear(self):
        self.average_gain = None
        self.average_loss = None



class AverageTrueRange(Indicator):
    def __init__(self, period=14):

        # init base class
        super(AverageTrueRange, self).__init__()

        # init indicator values
        self.period = period
        self.atr = None
        self.atr_list = []


    def update(self, data):
        if data.shape[0] <= 1: return None
        else: true_range = max(data[-1, ROW_INDICES.HIGH], data[-2, ROW_INDICES.CLOSE]) \
            - min(data[-1, ROW_INDICES.LOW], data[-2, ROW_INDICES.CLOSE])
        
        # calculate ATR average
        if self.atr is None:
            self.atr_list.append(true_range)
            if len(self.atr_list) >= self.period:
                self.atr = np.mean(self.atr_list)
                return self.atr
            else: return None
        else: 
            self.atr = (self.atr * (self.period - 1) + true_range) / self.period
            return self.atr


    def clear(self):
        self.atr = None
        self.atr_list = []



class AverageDirectionalIndex(Indicator):
    def __init__(self, period=14):

        # init base class
        super(AverageDirectionalIndex, self).__init__()

        # init indicator values
        self.period = period
        self.average_true_range = AverageTrueRange(period)
        self.p_di_list = []
        self.n_di_list = []
        self.p_di = None
        self.n_di = None
        self.adx_list = []
        self.adx = None


    def update(self, data):
        atr = self.average_true_range.update(data)
        
        # update p/n direction moves
        if data.shape[0] <= 1: return None
        else:
            up_move = data[-1, ROW_INDICES.HIGH] - data[-2, ROW_INDICES.HIGH]
            down_move = data[-2, ROW_INDICES.LOW] - data[-1, ROW_INDICES.LOW]
            if up_move > down_move and up_move > 0: p_dm = up_move
            else: p_dm = 0.0
            if down_move > up_move and down_move > 0: n_dm = down_move
            else: n_dm = 0.0

        # update p/n direction indices
        if self.p_di is None:
            self.p_di_list.append(p_dm)
            self.n_di_list.append(n_dm)
            if len(self.p_di_list) >= self.period:
                self.p_di = np.mean(self.p_di_list)
                self.n_di = np.mean(self.n_di_list)
            else: return None
        else:
            self.p_di = (self.p_di * (self.period - 1) + p_dm) / self.period
            self.n_di = (self.n_di * (self.period - 1) + n_dm) / self.period

        # compute adx
        p_di = 100 * self.p_di / atr
        n_di = 100 * self.n_di / atr
        adx = abs((p_di - n_di) / (p_di + n_di))

        # update adx
        if self.adx is None:
            self.adx_list.append(adx)
            if len(self.adx_list) >= self.period:
                self.adx = np.mean(self.adx_list)
                return 100 * self.adx
            else: return None
        else:
            self.adx = (self.adx * (self.period - 1) + adx) / self.period
            return 100 * self.adx


    def clear(self):
        self.average_true_range.clear()
        self.p_di_list = []
        self.n_di_list = []
        self.p_di = None
        self.n_di = None
        self.adx_list = []
        self.adx = None



class HeikinAshiCandle(Indicator):
    def __init__(self):

        # init base class
        super(HeikinAshiCandle, self).__init__()

        # init indicator values
        self.last_candles = []


    def update(self, data):

        # compute first candle
        if data.shape[0] == 1:
            self.last_candles = []
            b_open = data[0, ROW_INDICES.OPEN]
            b_high = data[0, ROW_INDICES.HIGH]
            b_low = data[0, ROW_INDICES.LOW]
            b_close = data[0, ROW_INDICES.CLOSE]
            ha_open = (b_open + b_close) / 2
            ha_close = (b_open + b_high + b_low + b_close) / 4
            self.last_candles.append((ha_open, b_high, b_low, ha_close))
            return self.last_candles

        # compute HA candle
        elif data.shape[0] > 1:
            b_open = data[-1, ROW_INDICES.OPEN]
            b_high = data[-1, ROW_INDICES.HIGH]
            b_low = data[-1, ROW_INDICES.LOW]
            b_close = data[-1, ROW_INDICES.CLOSE]
            ha_open = (self.last_candles[-1][0] + self.last_candles[-1][3]) / 2
            ha_close = (b_open + b_high + b_low + b_close) / 4
            ha_high = max(b_high, ha_open, ha_close)
            ha_low = max(b_low, ha_open, ha_close)
            self.last_candles.append((ha_open, ha_high, ha_low, ha_close))
            return self.last_candles


    def clear(self):
        self.last_candles = []
