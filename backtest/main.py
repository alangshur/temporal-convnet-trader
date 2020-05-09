from strategy import MACDCrossover, MovingAverageCrossover, RSIPosition
from backtest import BacktestManager

bt = BacktestManager(
    '../data/raw.nosync/AAPL.csv', 
    RSIPosition, 
    plot_date='2020-04-27'
    # target_date='2020-04-30'
)

bt.run()
# bt.plot()