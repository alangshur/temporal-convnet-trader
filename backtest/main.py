from strategy import MovingAverageCrossover
from backtest import BacktestManager



bt = BacktestManager(
    '../data/raw.nosync/AAPL-m.csv', 
    MovingAverageCrossover, 
    plot_date='2020-04-30'
)

bt.run(verbose=True)
bt.plot()