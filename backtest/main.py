import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from datetime import datetime
import numpy as np


class TestStrategy(bt.Strategy):
    params = (
        ('name', 'MA Crossover'),
        ('maperiod', 15),
        ('verbose', False)
    )


    def __init__(self):

        # init state data
        self.dataclose = self.datas[0].close
        self.order = None

        # init indicators
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], 
            period=self.params.maperiod
        )


    def log(self, msg, force_print=False):
        if self.params.verbose or force_print:
            dt = self.datas[0].datetime.datetime()
            print('Backtest [{}]: {}'.format(dt, msg))


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


# configure broker
cerebro = bt.Cerebro()
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
cerebro.broker.setcommission(commission=0.0)
cerebro.broker.set_slippage_perc(perc=0.0005)
init_balance = cerebro.broker.get_value()


# load historical data
data = btfeeds.GenericCSVData(
    dataname='../data/SPY.nosync/15m.csv',
    fromdate=datetime(2017, 1, 1),
    todate=datetime(2018, 12, 31),
    openinterest=-1,
    timeframe=bt.TimeFrame.Minutes,
    compression=15
)


# add metrics
cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='analyzer')


# run backtest
cerebro.adddata(data)
cerebro.addstrategy(TestStrategy, maperiod=26, verbose=False)
analysis = cerebro.run()[0].analyzers
# cerebro.plot(
#     start=datetime(2018, 6, 1),
#     end=datetime(2018, 6, 30)
# )


# print results
a = analysis.analyzer.get_analysis()
print('Starting Balance: {:,.2f} USD'.format(init_balance))
print('Ending Balance: {:,.2f} USD'.format(cerebro.broker.get_value()))
print('Total Return: {:,.3f}%'.format(analysis.returns.get_analysis()['rtot'] * 100))
print('Sharpe: {:,.3f}'.format(analysis.sharpe.get_analysis()['sharperatio']))
print('SQN: {:,.3f}'.format(analysis.sqn.get_analysis()['sqn']))
print('Max Drawdown: {:,.3f}%'.format(analysis.drawdown.get_analysis()['max']['drawdown']))
print('Win Rate: {:,.3f}%'.format(a['won']['total'] / (a['won']['total'] + a['lost']['total'])))
print('\nTotal Trades: {} trades'.format(a['total']['total']))
print('Longest Winning Streak: {} trades'.format(a['streak']['won']['longest']))
print('Longest Losing Streak: {} trades'.format(a['streak']['lost']['longest']))
print('Average Trade Size: {:,.3f} USD'.format(a['pnl']['net']['average']))
print('Average Win Size: {:,.3f} USD'.format(a['won']['pnl']['average']))
print('Average Loss Size: {:,.3f} USD'.format(a['lost']['pnl']['average']))
print('\nAverage Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['average'], a['len']['average'] * 15))
print('Average Win Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['won']['average'], a['len']['won']['average'] * 15))
print('Average Loss Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['lost']['average'], a['len']['lost']['average'] * 15))
# print('\nAverage Long Win Rate: {:,.3f}%'.format(a['long']['won'] / (a['long']['won'] + a['long']['lost'])))
# print('Average Long Win Size: {:,.3f} USD'.format(a['long']['pnl']['won']['average']))
# print('Average Long Loss Size: {:,.3f} USD'.format(a['long']['pnl']['lost']['average']))
# print('Average Short Win Rate: {:,.3f}%'.format(a['short']['won'] / (a['short']['won'] + a['short']['lost'])))
# print('Average Short Win Size: {:,.3f} USD'.format(a['short']['pnl']['won']['average']))
# print('Average Short Loss Size: {:,.3f} USD'.format(a['short']['pnl']['lost']['average']))