from strategy import MovingAverageCrossover
from backtest import BacktestManager



bt = BacktestManager('../data/raw.nosync/AAPL-m.csv', MovingAverageCrossover)
bt.run(verbose=True)
bt.plot()