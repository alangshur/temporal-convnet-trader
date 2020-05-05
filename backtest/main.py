from strategy import MovingAverageCrossover
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 


BARS_PER_DAY = 390


class Backtest:
    def __init__(self, csv_file, strategy, balance=10000.0):
        
        # load data
        self.data = pd.read_csv(
            csv_file,
            names=[
                'datetime', 'volume', 'open', 
                'high', 'low', 'close'
            ]
        ).to_numpy()

        # build trades
        self.strategy = strategy
        self.balance = balance
        self.position = None

        # record trades
        self.orders = []
        self.long_markers = []
        self.close_markers = []


    def go_market_long(self, buy_value):
        if not self.position:
            self.position = (1, buy_value)
            

    def close_position(self, sell_value, verbose=False):
        if self.position:
            shares, buy_value = self.position
            profit = shares * (sell_value - buy_value)

            # print results
            if verbose:
                if profit > 0: print('PROFIT: Closed position with {}'.format(profit))
                else: print('LOSS: Closed position with {}'.format(profit))

            # record close results 
            self.balance += shares * (sell_value - buy_value)
            self.position = None


    def run(self):
        total_days = self.data.shape[0] // BARS_PER_DAY
        print('Starting balance: {}'.format(self.balance))

        for i in range(total_days):
            day_index = i * BARS_PER_DAY

            for j in range(BARS_PER_DAY):
                bar_index = day_index + j
                data = self.data[day_index:bar_index + 1]
                result = self.strategy.update(data, j)
                close = self.data[bar_index, config.ROW_INDICES.CLOSE]

                # execute position
                if result == 'long' and not self.position: 
                    self.go_market_long(close)
                    self.long_markers.append(bar_index)

                elif result == 'short' and self.position: 
                    self.close_position(close)
                    self.close_markers.append(bar_index)

        print('Ending balance: {}'.format(self.balance))
        

    def plot(self):
        datetime_data = self.data[:, ROW_INDICES.DATE_TIME]
        datetime_data = datetime_data.astype(np.datetime64)
        close_data = self.data[:, ROW_INDICES.CLOSE]
        plt.plot(datetime_data, close_data)
        plt.show()


if __name__ == '__main__':

    strat = MovingAverageCrossover('ma-cross')
    bt = Backtest('../data/raw.nosync/AAPL-m.csv', strat)
    bt.run()
    bt.plot()



