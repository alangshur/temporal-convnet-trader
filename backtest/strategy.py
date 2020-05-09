from indicator import SimpleMovingAverage, ExpontentialMovingAverage
from config import BARS_PER_DAY, ORDER_TYPES, ORDER_DIRS
from collections import namedtuple
import numpy as np



class Strategy:
    def __init__(self, order_manager):
        self.order_manager = order_manager

    def update(self, data, day_index):
        raise NotImplementedError



class StrategyUpdate:
    def __init__(self, direction=None, metrics=None, sub_metrics=None):
        self.direction = direction
        self.metrics = metrics
        self.sub_metrics = sub_metrics



class MovingAverageCrossover(Strategy):
    def __init__(self, order_manager, short_period=20, long_period=60):

        # init base class
        super(MovingAverageCrossover, self).__init__(order_manager)

        # get moving averages
        self.ma_short = SimpleMovingAverage(period=short_period)
        self.ma_long = SimpleMovingAverage(period=long_period)

        # init prev state
        self.prev_state = None


    def update(self, day_data, day_index):

        # update averages
        ma_short_val = self.ma_short.update(day_data)
        ma_long_val = self.ma_long.update(day_data)
        metrics = {
            'ma_short': ma_short_val if ma_short_val is not None else np.nan,
            'ma_long': ma_long_val if ma_long_val is not None else np.nan
        }
    
        # verify direction
        if ma_short_val is not None and ma_long_val is not None:
            
            # close position on last bar
            if day_index == BARS_PER_DAY - 1:
                self.order_manager.add_order(ORDER_TYPES.CLOSE)
                return StrategyUpdate(direction=ORDER_DIRS.SHORT, metrics=metrics)

            # update state
            if ma_short_val < ma_long_val: cur_state = ORDER_DIRS.SHORT
            else: cur_state = ORDER_DIRS.LONG

            # compute signal
            if self.prev_state is None: self.prev_state = cur_state
            elif self.prev_state != cur_state:
                self.prev_state = cur_state

                if cur_state == ORDER_DIRS.LONG:
                    self.order_manager.add_order(ORDER_TYPES.MARKET, ORDER_DIRS.LONG, 1)
                    return StrategyUpdate(direction=ORDER_DIRS.LONG, metrics=metrics)

                elif cur_state == ORDER_DIRS.SHORT:
                    self.order_manager.add_order(ORDER_TYPES.CLOSE)
                    return StrategyUpdate(direction=ORDER_DIRS.SHORT, metrics=metrics)
        
        # return metrics update
        return StrategyUpdate(metrics=metrics)



class MACDCrossover(Strategy):
    def __init__(self, order_manager, short_period=12, long_period=26, 
                 signal_period=26, signal_smoothing=2):

        # init base class
        super(MACDCrossover, self).__init__(order_manager)

        # init params
        self.signal_period = signal_period
        self.update_rate = signal_smoothing / (1 + signal_period)

        # get moving averages
        self.ma_short = ExpontentialMovingAverage(period=short_period)
        self.ma_long = ExpontentialMovingAverage(period=long_period)
        self.macd_ma_init = []
        self.macd_ma = None
        self.macd = None

        # init prev state
        self.prev_state = None


    def update(self, day_data, day_index):

        # update averages
        ma_short_val = self.ma_short.update(day_data)
        ma_long_val = self.ma_long.update(day_data)

        # compute macd
        if ma_short_val is not None and ma_long_val is not None:
            self.macd = ma_short_val - ma_long_val

            # initialize macd_ma
            if self.macd_ma is None:
                self.macd_ma_init.append(self.macd)
                if len(self.macd_ma_init) >= self.signal_period:
                    macd_ma_arr = np.array(self.macd_ma_init)
                    self.macd_ma = np.mean(macd_ma_arr)
            else:
                self.macd_ma = self.macd * self.update_rate + \
                    self.macd_ma * (1 - self.update_rate)

        # add metrics
        metrics, sub_metrics = {
            'ma_short': ma_short_val if ma_short_val is not None else np.nan,
            'ma_long': ma_long_val if ma_long_val is not None else np.nan
        }, {
            'macd': self.macd if self.macd is not None else np.nan,
            'macd_ma': self.macd_ma if self.macd_ma is not None else np.nan
        }

        if self.macd is not None and self.macd_ma is not None:
 
            # close position on last bar
            if day_index == BARS_PER_DAY - 1:
                self.order_manager.add_order(ORDER_TYPES.CLOSE)
                return StrategyUpdate(direction=ORDER_DIRS.SHORT, 
                    metrics=metrics, sub_metrics=sub_metrics)

            # update state
            if self.macd < self.macd_ma: cur_state = ORDER_DIRS.SHORT
            else: cur_state = ORDER_DIRS.LONG

            # compute signal
            if self.prev_state is None: self.prev_state = cur_state
            elif self.prev_state != cur_state:
                self.prev_state = cur_state

                if cur_state == ORDER_DIRS.LONG:
                    self.order_manager.add_order(ORDER_TYPES.MARKET, ORDER_DIRS.LONG, 1)
                    return StrategyUpdate(direction=ORDER_DIRS.LONG, metrics=metrics, 
                        sub_metrics=sub_metrics)

                elif cur_state == ORDER_DIRS.SHORT:
                    self.order_manager.add_order(ORDER_TYPES.CLOSE)
                    return StrategyUpdate(direction=ORDER_DIRS.SHORT, metrics=metrics, 
                        sub_metrics=sub_metrics)

        return StrategyUpdate(metrics=metrics, sub_metrics=sub_metrics)