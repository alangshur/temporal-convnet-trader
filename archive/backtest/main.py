from strategy import CustomStrategy
from backtest import BacktestManager

bt = BacktestManager(
    '../data/raw.nosync/AAPL-m.csv', 
    CustomStrategy, 
    plot_date='2020-04-28',
    target_date='2020-04-28',
)

bt.run()
bt.plot()