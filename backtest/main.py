import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
from datetime import datetime
import numpy as np


class PercentRiskSizer(bt.Sizer):
    params = dict(
        perc_risk=0.001
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        risk = self.strategy.stop_dist[0]
        to_risk = self.broker.get_value() * self.p.perc_risk
        return to_risk // risk


class CustomStrategy(bt.Strategy):
    params = dict(
        name='Custom Strat',
        verbose=True,
        atr_period=26,
        ema_period=10,
        stop_factor=3.0,
    )


    def __init__(self):

        # init state data
        self.order = None

        # volatility to determine stop distance
        atr = bt.ind.ATR(self.data, period=self.p.atr_period, plot=False)
        ema_atr = bt.ind.EMA(atr, period=self.p.ema_period, plot=False)
        self.stop_dist = ema_atr * self.p.stop_factor

        # running stop price calculation
        self.stop = self.data - self.stop_dist
        self.stop_long = None


    def log(self, msg, force_print=False):

        # log backtest message
        if self.params.verbose or force_print:
            dt = self.data.datetime.datetime()
            print('Backtest [{}]: {}'.format(dt, msg))


    def notify_order(self, order):

        # order was submitted/accepted
        if order.status in [order.Submitted, order.Accepted]:
            return

        # order was completed
        if order.status in [order.Completed]:
            if order.isbuy(): self.log('Buy @ {:,.3f} USD'.format(order.executed.price))
            elif order.issell(): self.log('Sell @ {:,.3f} USD'.format(order.executed.price))
            self.order = None

        # order was cancelled/rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Rejected')
            self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed: return
        self.log('Trade Result: {:,.3f}'.format(trade.pnl))


    def next(self):        
        if not self.position:
            if self.lrsi[-1] == 0.0 and self.lrsi[0] > 0.0:
                self.order = self.buy()
                self.stop_long = self.stop[0]

        else:
            self.stop_long = max(self.stop[0], self.stop_long)
            if self.data[0] <= self.stop_long: self.close()


# configure broker
cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.setcash(cash=100000.0)
cerebro.broker.setcommission(commission=0.0)
cerebro.broker.set_slippage_perc(perc=0.0005)
init_balance = cerebro.broker.get_value()


# add sizer
cerebro.addsizer(PercentRiskSizer)
# cerebro.addsizer(bt.sizers.FixedSize, stake=1)


# add observers
cerebro.addobserver(bt.observers.Value)
cerebro.addobserver(bt.observers.BuySell)


# load historical data
cerebro.adddata(btfeeds.GenericCSVData(
    dataname='../data/UNI/SPY.csv',
    fromdate=datetime(2016, 1, 1),
    todate=datetime(2018, 12, 31),
    openinterest=-1,
    timeframe=bt.TimeFrame.Minutes,
    compression=15
))


# add metrics
cerebro.addanalyzer(btanalyzers.Returns, _name='returns')
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(btanalyzers.SQN, _name='sqn')
cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='analyzer')


# run backtest
cerebro.addstrategy(CustomStrategy)
analysis = cerebro.run(maxcpus=1)[0].analyzers
cerebro.plot(
    start=datetime(2016, 1, 1),
    end=datetime(2018, 12, 31)
)


# print results
a = analysis.analyzer.get_analysis()
print('Starting Balance: {:,.2f} USD'.format(init_balance))
print('Ending Balance: {:,.2f} USD'.format(cerebro.broker.get_value()))
print('Total Return: {:,.3f}%'.format(analysis.returns.get_analysis()['rtot'] * 100))
print('Sharpe: {:,.3f}'.format(analysis.sharpe.get_analysis()['sharperatio']))
print('SQN: {:,.3f}'.format(analysis.sqn.get_analysis()['sqn']))
print('Max Drawdown: {:,.3f}%'.format(analysis.drawdown.get_analysis()['max']['drawdown']))
print('Win Rate: {:,.3f}%'.format(a['won']['total'] / (a['won']['total'] + a['lost']['total']) * 100))
print('\nTotal Trades: {} trades'.format(a['total']['total']))
print('Longest Winning Streak: {} trades'.format(a['streak']['won']['longest']))
print('Longest Losing Streak: {} trades'.format(a['streak']['lost']['longest']))
print('Average Trade Size: {:,.3f} USD'.format(a['pnl']['net']['average']))
print('Average Win Size: {:,.3f} USD'.format(a['won']['pnl']['average']))
print('Average Loss Size: {:,.3f} USD'.format(a['lost']['pnl']['average']))
print('\nAverage Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['average'], a['len']['average'] * 30))
print('Average Win Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['won']['average'], a['len']['won']['average'] * 30))
print('Average Loss Trade Time: {:,.3f} bars ({:,.0f}m)'.format(a['len']['lost']['average'], a['len']['lost']['average'] * 30))