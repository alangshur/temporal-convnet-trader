from indicator import SimpleMovingAverage



class Strategy:
    def __init__(self, order_manager):
        self.order_manager = order_manager

    def update(self, data, day_index):
        raise NotImplementedError



class MovingAverageCrossover(Strategy):
    def __init__(self, order_manager):

        # get moving averages
        self.ma_20 = SimpleMovingAverage(period=20)
        self.ma_60 = SimpleMovingAverage(period=60)

        # init base class
        super(MovingAverageCrossover, self).__init__(order_manager)

        # init prev state
        self.prev_state = None


    def update(self, day_data, day_index):

        # update averages
        ma_20_val = self.ma_20.update(day_data)
        ma_60_val = self.ma_60.update(day_data)
        if ma_20_val and ma_60_val:

            # update state
            if ma_20_val < ma_60_val: cur_state = 'short'
            else: cur_state = 'long'

            # compute signal
            if not self.prev_state: self.prev_state = cur_state
            elif self.prev_state != cur_state:
                self.prev_state = cur_state
                if cur_state == 'long':
                    self.order_manager.add_order('market', 'long', 1)
                elif cur_state == 'short':
                    self.order_manager.add_order('close')
