from order import OrderManager
from balance import BalanceManager
from config import BARS_PER_DAY, ROW_INDICES, ORDER_DIRS
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import math


class BacktestManager:
    def __init__(self, csv_file, strategy, strategy_params={},
                 plot_date=None, balance=10000.0, target_date=None):
        
        # init assets
        print('\nInitializing backtest.')
        self.balance_manager = BalanceManager(balance) 
        self.order_manager = OrderManager(self.balance_manager)
        self.strategy = strategy(self.order_manager, **strategy_params)
        
        # load data
        print('Loading data.')
        self.data = pd.read_csv(
            csv_file,
            names=[
                'datetime', 'volume', 'open', 
                'high', 'low', 'close'
            ]
        ).to_numpy()

        # add target data
        self.plot_date = plot_date
        self.target_date = target_date
        if target_date is not None: self.plot_date = target_date
        else: self.plot_date = plot_date

        # add plot data
        self.metrics = {}
        self.sub_metrics = {}
        self.long_markers = []
        self.short_markers = []
        print('Backtest ready.')


    def run(self):
        total_days = self.data.shape[0] // BARS_PER_DAY
        print('\nRunning backtest.')

        deltas = 0

        for date_index in range(total_days):
            true_date_index = date_index * BARS_PER_DAY

            # get backtest datetime
            datetime = self.data[true_date_index, ROW_INDICES.DATETIME]
            date_str = datetime.split(' ')[0]
            print('Backtesting on: {}'.format(date_str), end='\r')
            
            # prepare plot data
            record_metrics = False
            if self.plot_date == date_str:
                self.plot_date_index = true_date_index
                record_metrics = True
            elif self.target_date: continue

            for bar_index in range(BARS_PER_DAY):
                true_bar_index = true_date_index + bar_index
                date_data = self.data[true_date_index:true_bar_index + 1]
                bar_data = date_data[-1]

                # update assets
                self.order_manager.update(bar_data)
                update = self.strategy.update(date_data, bar_index)

                # record data
                if record_metrics:

                    # update main metrics
                    if update.metrics is not None:
                        for m_name, metric in update.metrics.items():
                            if m_name in self.metrics: self.metrics[m_name].append(metric)
                            else: self.metrics[m_name] = [metric]

                    # update sub metrics
                    if update.sub_metrics is not None:
                        for m_name, metric in update.sub_metrics.items():
                            if m_name in self.sub_metrics: self.sub_metrics[m_name].append(metric)
                            else: self.sub_metrics[m_name] = [metric]

                    # update positions
                    if update.direction == ORDER_DIRS.LONG: 
                        self.long_markers.append(bar_data[ROW_INDICES.CLOSE])
                        self.short_markers.append(np.nan)
                    elif update.direction == ORDER_DIRS.SHORT:
                        self.long_markers.append(np.nan)
                        self.short_markers.append(bar_data[ROW_INDICES.CLOSE])
                    else:
                        self.long_markers.append(np.nan)
                        self.short_markers.append(np.nan)
                
            # quit after target
            if self.target_date: break

        print(deltas)

        # wrap-up backtest
        print('\n\n--- Results for {} ---\n'.format(
            self.strategy.__class__.__name__))
        for k, v in self.balance_manager.get_report().items():
            print('{}: {}'.format(k, round(v, 3)))
        print('\n--------------------{}'.format(
            '-' * len(self.strategy.__class__.__name__)
        ))

    def plot(self):
        if self.plot_date is not None:
            print('\nPlotting results.')

            # configure datetime axis
            date_fmt = mdates.DateFormatter('%H:%M')
            datetime_data = self.data[self.plot_date_index:
                self.plot_date_index + BARS_PER_DAY, ROW_INDICES.DATETIME]
            datetime_data = datetime_data.astype(np.datetime64)

            # configure close price axis
            close_data = self.data[self.plot_date_index:
                self.plot_date_index + BARS_PER_DAY, ROW_INDICES.CLOSE]

            # plot close data
            fig, ax = plt.subplots(1 + int(len(self.sub_metrics) > 0), figsize=(12, 8))
            if len(self.sub_metrics) == 0: ax = [ax]
            ax[0].plot(datetime_data, close_data)
            ax[0].xaxis.set_major_formatter(date_fmt)
            metric_labels = ['close']

            # plot metric data
            for m_name, metric in self.metrics.items():
                metric_arr = np.array(metric)
                ax[0].plot(datetime_data, metric_arr)
                metric_labels.append(m_name)

            # plot sub-metric data
            sub_metric_labels = []
            for m_name, metric in self.sub_metrics.items():
                metric_arr = np.array(metric)
                if math.isnan(metric_arr[0]): 
                    metric_arr[0] = 0.0
                    metric_arr[1] = np.nan
                if math.isnan(metric_arr[-1]): 
                    metric_arr[-1] = 0.0
                    metric_arr[-2] = np.nan
                ax[1].plot(datetime_data, metric_arr)
                sub_metric_labels.append(m_name)

            # plot signal data
            long_markers = np.array(self.long_markers) - 1
            short_markers = np.array(self.short_markers) + 1
            ax[0].plot(datetime_data, long_markers, marker='^', color='g', markersize=10, linestyle='None')
            ax[0].plot(datetime_data, short_markers, marker='v', color='r', markersize=10, linestyle='None')
            metric_labels.extend(['l_signal', 's_signal'])

            # finalize plots
            ax[0].legend(metric_labels)
            if len(sub_metric_labels) > 0: 
                ax[1].legend(sub_metric_labels)
                ax[1].xaxis.set_major_formatter(date_fmt)
            plt.show()
