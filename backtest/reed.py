import backtrader as bt
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression


class ReedScore(bt.Indicator):
    lines = ('error', 'slope')
    params = dict(
        reg_len=60
    )

    def __init__(self):
        self.tp = (self.data.high + self.data.low + self.data.close) / 3

    def next(self):
        if len(self) >= self.p.reg_len:

            # fit regression
            x = np.arange(self.p.reg_len).reshape(-1, 1)
            y = self.tp.get(size=self.p.reg_len)
            reg = LinearRegression().fit(x, y)

            # calculate lines
            y_hat = reg.coef_ * np.arange(self.p.reg_len) + reg.intercept_
            error = np.linalg.norm(y - y_hat)
            slope = reg.coef_[0]

            # normalized lines
            self.lines.error[0] = error
            self.lines.slope[0] = slope


class ReedStrategy(bt.Strategy):
    params = dict(
        verbose=True,
        atr_period=13,
        ema_period=5,
        stop_factor=10.0,
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

        # init indicators
        # self.reed = ReedScore()  # two-month-long regression
        # self.ama = bt.indicators.AdaptiveMovingAverage(period=300, fast=6, slow=300)

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
            if order.isbuy():
                self.log('Buy @ {:,.3f} USD'.format(order.executed.price))
            elif order.issell():
                self.log('Sell @ {:,.3f} USD'.format(order.executed.price))
            self.order = None

        # order was cancelled/rejected
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Rejected')
            self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed: return
        self.log('Trade Result: {:,.3f}'.format(trade.pnl))

    def next(self):
        pass

        # if not self.position:
        #     if self.data[0] > self.ama[0] and self.reed.slope[0] > 0.05 and self.reed.score[0] < 40:
        #         self.order = self.buy()
        #         self.stop_long = self.stop[0]

        # else:
        #     self.stop_long = max(self.stop[0], self.stop_long)
        #     if self.data[0] <= self.stop_long: self.close()


class PercentRiskSizer(bt.Sizer):
    params = dict(
        perc_risk=0.005
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        risk = self.strategy.stop_dist[0]
        to_risk = self.broker.get_value() * self.p.perc_risk
        return to_risk // risk