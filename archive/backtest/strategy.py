from indicator import SimpleMovingAverage
from config import BARS_PER_DAY, ORDER_TYPES, ROW_INDICES, ORDER_DIRS
from collections import namedtuple
import numpy as np



class Strategy:
    def __init__(self, order_manager):
        self.order_manager = order_manager

    def update(self, data, bar_index):
        raise NotImplementedError



class StrategyUpdate:
    def __init__(self, direction=None, metrics=None, sub_metrics=None):
        self.direction = direction
        self.metrics = metrics
        self.sub_metrics = sub_metrics



class CustomStrategy(Strategy):
    def __init__(self, order_manager):
        super(CustomStrategy, self).__init__(order_manager)
        self.sma = SimpleMovingAverage(period=100)


    def update(self, data, bar_index):
        average = self.sma.update(data)
        return StrategyUpdate(metrics={
            'avg': np.nan if average is None else average
        })



