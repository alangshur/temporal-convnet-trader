from indicator import SimpleMovingAverage
from config import BARS_PER_DAY, ORDER_TYPES, ORDER_DIRS
from collections import namedtuple
import numpy as np



class Strategy:
    def __init__(self, order_manager):
        self.order_manager = order_manager

    def update(self, data, day_index):
        raise NotImplementedError



class StrategyUpdate:
    def __init__(self, direction=None, metrics=None):
        self.direction = direction
        self.metrics = metrics



class MovingAverageCrossover(Strategy):
    def __init__(self, order_manager, period_short=20, 
                 period_long=60):

        # get moving averages
        self.ma_short = SimpleMovingAverage(period=period_short)
        self.ma_long = SimpleMovingAverage(period=period_long)

        # init base class
        super(MovingAverageCrossover, self).__init__(order_manager)

        # init prev state
        self.prev_state = None


    def update(self, day_data, day_index):

        # update averages
        ma_short_val = self.ma_short.update(day_data)
        ma_long_val = self.ma_long.update(day_data)
        metrics = {
            'ma_short': ma_short_val if ma_short_val else np.nan,
            'ma_long': ma_long_val if ma_short_val else np.nan
        }
    
        # verify direction
        if ma_short_val and ma_long_val:
            
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