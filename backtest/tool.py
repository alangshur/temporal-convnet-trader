import numpy as np
import config


class Tool:
    def __init__(self, name):
        self.name = name


    def get_name():
        return self.name


    def update(self, data):
        raise NotImplementedError


    def get_values(self):
        raise NotImplementedError


class SimpleMovingAverage(Tool):
    def __init__(self, name, period=10):
        super(SimpleMovingAverage, self).__init__(name)
        self.period = period
        self.average = None
        self.moving_values = None


    def update(self, data):
        if data.shape[0] < self.period: return
        else:
            self.moving_values = np.copy(data[-self.period:, config.ROW_INDICES.CLOSE])
            self.average = np.mean(self.moving_values)
            
            
    def get_values(self):
        return self.average