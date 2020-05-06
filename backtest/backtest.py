from order import OrderManager
from balance import BalanceManager
import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

BARS_PER_DAY = 390



class BacktestManager:
    def __init__(self, csv_file, strategy, balance=10000.0, 
                 plot_date=None):
        
        # init assets
        self.balance_manager = BalanceManager(init_balance=balance) 
        self.order_manager = OrderManager(self.balance_manager)
        self.strategy = strategy(self.order_manager)
        
        # load data
        self.data = pd.read_csv(
            csv_file,
            names=[
                'datetime', 'volume', 'open', 
                'high', 'low', 'close'
            ]
        ).to_numpy()

        # add plot data
        self.plot_date = plot_date
        self.positions = []
        self.long_markers = []
        self.close_markers = []


    def run(self, verbose=False):
        total_days = self.data.shape[0] // BARS_PER_DAY
        if verbose: print('Balance: {}'.format(self.balance_manager.get_balance()))

        for day_idx in range(total_days):
            date_index = day_idx * BARS_PER_DAY
            prev_date_index = date_index - BARS_PER_DAY

            # get backtest datetime
            datetime = self.data[date_index, config.ROW_INDICES.DATETIME]
            date_str = datetime.split(' ')[0]
            
            # get plot date
            if self.plot_date == date_str:
                self.plot_date_index = date_index

            for bar_idx in range(BARS_PER_DAY):
                true_bar_index = date_index + bar_idx
                day_data = self.data[date_index:true_bar_index + 1]
                bar_data = day_data[-1]

                # update assets
                self.order_manager.update(bar_data)
                result = self.strategy.update(day_data, bar_idx)

        # wrap-up backtest
        if not self.plot_date: 
            self.plot_date = date_str
            self.plot_date_index = date_index
        if verbose: print('Balance: {}'.format(self.balance_manager.get_balance()))


    def plot(self):

        # configure datetime axis
        datetime_data = self.data[self.plot_date_index:
            self.plot_date_index + BARS_PER_DAY, 
            config.ROW_INDICES.DATETIME]
        datetime_data = datetime_data.astype(np.datetime64)

        # configure close price axis
        close_data = self.data[self.plot_date_index:
            self.plot_date_index + BARS_PER_DAY,
            config.ROW_INDICES.CLOSE]

        # plot data
        plt.plot(datetime_data, close_data)
        plt.xlabel('Time (Minute Bar)')
        plt.ylabel('Closing Prices (Dollar)')
        plt.show()

