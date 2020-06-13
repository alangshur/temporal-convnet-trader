import backtrader as bt
from datetime import datetime
from reed import ReedStrategy, PercentRiskSizer


if __name__ == '__main__':
    
    # configure broker
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(cash=100000.0)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.broker.set_slippage_perc(perc=0.0005)
    init_balance = cerebro.broker.get_value()

    # add sizer
    # cerebro.addsizer(PercentRiskSizer)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # add observers
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.BuySell)

    # load historical data
    cerebro.adddata(bt.feeds.GenericCSVData(
        dataname='../data/UNI/SPY.csv',
        fromdate=datetime(2016, 1, 5),
        todate=datetime(2016, 1, 13),
        openinterest=-1,
        timeframe=bt.TimeFrame.Minutes,
        compression=5
    ))

    # add metrics
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='analyzer')

    # run backtest
    cerebro.addstrategy(ReedStrategy)
    analysis = cerebro.run(maxcpus=1)[0].analyzers
    cerebro.plot(
        start=datetime(2016, 1, 5),
        end=datetime(2016, 1, 13)
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
