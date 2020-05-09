from strategy import MACDCrossover, MovingAverageCrossover
from backtest import BacktestManager

macd_params = {

}

bt = BacktestManager(
    '../data/raw.nosync/AAPL-m.csv', 
    MACDCrossover, 
    strategy_params=macd_params,
    plot_date='2020-04-30',
    target_date='2020-04-30'
)

bt.run()
bt.plot()