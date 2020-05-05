from tool import SimpleMovingAverage
import numpy as np


class Strategy:
    def __init__(self, name, tools):
        self.name = name
        self.tools = tools


    def update(self, data, day_index):
        for tool in self.tools:
            tool.update(data)
        return self.signal(data, day_index)


    def signal(self, data, day_index):
        raise NotImplementedError


class MovingAverageCrossover(Strategy):
    def __init__(self, name):

        # get moving averages
        self.ma_20 = SimpleMovingAverage('ma_20', 20)
        self.ma_60 = SimpleMovingAverage('ma_60', 60)

        # init base class
        super(MovingAverageCrossover, self).__init__(
            name, [self.ma_20, self.ma_60]
        )

        self.prev_state = None


    def signal(self, data, day_index):
        ma_20_val = self.ma_20.get_values()
        ma_60_val = self.ma_60.get_values()

        # update state
        if not ma_20_val or not ma_60_val: return None
        cur_state = 'short' if ma_20_val < ma_60_val else 'long'

        # compute signal
        if not self.prev_state: self.prev_state = cur_state
        elif self.prev_state != cur_state:
            self.prev_state = cur_state
            return cur_state
            
        return None
