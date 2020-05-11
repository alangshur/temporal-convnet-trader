from indicator import HeikinAshiCandle
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
        
        self.ha = HeikinAshiCandle()
        self.heikin_candles = []
        self.period = 7
    
    def update(self, data, bar_index):

        ha_candles = self.ha.update(data)
        if len(ha_candles) > self.period:

            down_bars = 0
            for i in range(self.period):
                bar = -i - 1
                delta = ha_candles[bar][0] - ha_candles[bar][3]
                if delta > 0: down_bars += 1
                else: break

            if down_bars == self.period:
                print('Identified trend: {}'.format(data[-1, 0]))
                return StrategyUpdate(direction=ORDER_DIRS.LONG)
        
        return StrategyUpdate()

