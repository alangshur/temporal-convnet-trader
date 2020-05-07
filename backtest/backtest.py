from order import OrderManager
from balance import BalanceManager
from config import BARS_PER_DAY, ROW_INDICES, ORDER_DIRS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 



class BacktestManager:
    def __init__(self, csv_file, strategy, plot_date=None, 
                 balance=10000.0):
        
        # init assets
        self.balance_manager = BalanceManager(balance) 
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
        self.metrics = {}
        self.long_markers = []
        self.short_markers = []


    def run(self, verbose=False):
        total_days = self.data.shape[0] // BARS_PER_DAY

        for date_index in range(total_days):
            true_date_index = date_index * BARS_PER_DAY

            # get backtest datetime
            datetime = self.data[true_date_index, ROW_INDICES.DATETIME]
            date_str = datetime.split(' ')[0]
            
            # prepare plot data
            record_metrics = False
            if self.plot_date == date_str:
                self.plot_date_index = true_date_index
                record_metrics = True

            for bar_index in range(BARS_PER_DAY):
                true_bar_index = true_date_index + bar_index
                date_data = self.data[true_date_index:true_bar_index + 1]
                bar_data = date_data[-1]

                # update assets
                self.order_manager.update(bar_data)
                update = self.strategy.update(date_data, bar_index)

                # record metrics
                if record_metrics and update:

                    for k, v in update.metrics.items():
                        if k in self.metrics: self.metrics[k].append(v)
                        else: self.metrics[k] = [v]

                    if update.direction == ORDER_DIRS.LONG: 
                        self.long_markers.append(bar_data[ROW_INDICES.CLOSE])
                        self.short_markers.append(np.nan)
                    elif update.direction == ORDER_DIRS.SHORT:
                        self.long_markers.append(np.nan)
                        self.short_markers.append(bar_data[ROW_INDICES.CLOSE])
                    else:
                        self.long_markers.append(np.nan)
                        self.short_markers.append(np.nan)

        # wrap-up backtest
        if verbose: 
            for k, v in self.balance_manager.get_report().items():
                print('{}: {}'.format(k, v))

    def plot(self):
        if self.plot_date:

            # configure datetime axis
            datetime_data = self.data[self.plot_date_index:
                self.plot_date_index + BARS_PER_DAY, ROW_INDICES.DATETIME]
            datetime_data = datetime_data.astype(np.datetime64)

            # configure close price axis
            close_data = self.data[self.plot_date_index:
                self.plot_date_index + BARS_PER_DAY, ROW_INDICES.CLOSE]

            # plot close data
            plt.plot(datetime_data, close_data)
            labels = ['close']

            # plot metric data
            for k, v in self.metrics.items():
                metric_arr = np.array(v)
                plt.plot(datetime_data, metric_arr)
                labels.append(k)

            # plot signal data
            long_markers = np.array(self.long_markers) - 1.25
            short_markers = np.array(self.short_markers) + 1.25
            plt.plot(datetime_data, long_markers, marker='^', color='g', markersize=11, linestyle='None')
            plt.plot(datetime_data, short_markers, marker='v', color='r', markersize=11, linestyle='None')
            labels.extend(['l_signal', 's_signal'])

            # display plot
            plt.legend(labels)
            plt.xlabel('Time (Minute Bars)')
            plt.ylabel('Closing Prices (USD)')
            plt.show()

