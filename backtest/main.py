import backtrader as bt
import backtrader.feeds as btfeeds
from datetime import datetime


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy(): self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell(): self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed: return
        self.log('OPERATION PROFIT, GROSS %.2f' % trade.pnl)

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order: return
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
            (self.params.maperiod, self.broker.getvalue()), doprint=True)

cerebro = bt.Cerebro()
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
cerebro.broker.setcommission(commission=0.0)
cerebro.broker.set_slippage_perc(perc=0.0005)

data = btfeeds.GenericCSVData(
    dataname='../data/SPY.nosync/15m.csv',
    fromdate=datetime(2019, 1, 1),
    todate=datetime(2020, 1, 1),
    openinterest=-1,
    timeframe=bt.TimeFrame.Minutes,
    compression=10
)

cerebro.adddata(data)
cerebro.addstrategy(TestStrategy, maperiod=26, printlog=True)
# strats = cerebro.optstrategy(
#         TestStrategy,
#         maperiod=range(10, 31)
# )
        
cerebro.run(maxcpus=1)
# cerebro.plot()
