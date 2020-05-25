import alpaca_trade_api as tradeapi
from datetime import datetime
import numpy as np
import talib


class ScalpStrategy:
    def __init__(self, target_atr=0.4, start_size=0.20, take_size=0.07, 
                 stop_size=-0.04, timeout_time=30, verbose=False, test=False):

        # set meta params
        self.verbose = verbose
        self.test = test

        # set account params
        self.key_id = 'PKYREM6HRZ8CS4BISSPY'
        self.secret_key = 'JDLct0wvUQEmdGvYmwRC4uTrpUqPBe6HYk0kjHAr'
        self.base_url = 'https://paper-api.alpaca.markets'

        # connect to API
        self.api = tradeapi.REST(
            key_id=self.key_id, 
            secret_key=self.secret_key,
            base_url=self.base_url
        )

        # set trade parameters
        self.symbol = 'SPY'
        self.qty = 1
        self.target_atr = target_atr
        self.start_size = start_size
        self.take_size = take_size
        self.stop_size = stop_size
        self.timeout_time = timeout_time

        # set state parameters
        self.current_order = None
        self.seconds = 0
        self.min_his = []
        self.min_los = []
        self.min_cls = []

        # get active positions
        self.api.cancel_all_orders()
        try: self.position = int(self.api.get_position(self.symbol).qty)
        except: self.position = 0

        # log initialization
        self.log(info='Scalping strategy initialized.')


    def log(self, info=None, error=None):
        t = str(datetime.now()).split('.')[0]
        if info is not None: print('Trader [' +  t + '] - INFO: {}'.format(info))
        elif error is not None: print('Trader [' +  t + '] - ERROR: {}'.format(error))


    def _run(self):
        
        # connect to stream
        conn = tradeapi.StreamConn(
            key_id=self.key_id,
            secret_key=self.secret_key,
            base_url=self.base_url,
            data_stream='polygon'
        )

        # add second-agg stream
        @conn.on(r'^A$', [self.symbol])
        async def handle_agg_s(conn, channel, data):
            self.seconds += 1

            # cancel expired order
            if self.current_order is not None and self.seconds > self.timeout_time:
                self.api.cancel_order(self.current_order.id)

        # add minute-agg stream
        @conn.on(r'^AM$', [self.symbol])
        async def handle_agg_m(conn, channel, data):
            self.seconds = 0

            # append minute data
            self.min_his.append(data.high)
            self.min_los.append(data.low)
            self.min_cls.append(data.close)

            # calculate atr
            atr = talib.ATR(np.array(self.min_his), np.array(self.min_los), 
                np.array(self.min_cls), timeperiod=14)
            curr_atr = atr[-1] if not np.isnan(atr[-1]) else 0.0
            if self.verbose: self.log(info='Price at {}, ATR at {}.'.format(data.close, curr_atr))

            # submit order
            if curr_atr >= self.target_atr and self.current_order is None and self.position == 0:
                self.log(info='Submitting order {}.'.format(self.current_order.id))
                if not self.test:
                    self.current_order = self.api.submit_order(
                        symbol=self.symbol,
                        side='buy',
                        qty=self.qty,
                        type='limit',
                        order_class='bracket',
                        time_in_force='day',

                        limit_price=data.close + self.start_size,
                        take_profit=dict(limit_price=data.close + self.start_size + self.take_size),
                        stop_loss=dict(stop_price=data.close + self.start_size + self.stop_size)
                    )

        # add trade update stream
        @conn.on(r'trade_updates')
        async def handle_trade(conn, channel, data):
            event_type = data.event
            side = data.order['side']
            oid = data.order['id']
            price = data.order['price']

            # order is filled
            if event_type == 'fill':
                self.log(info='{} order {} filled at {}.'.format(side.title(), oid, price))
                self.position = int(data.position_qty)
                if self.current_order is not None and self.current_order.id == oid:
                    self.current_order = None

            # order is partially filled
            elif event_type == 'partial_fill':
                self.log(info='{} order {} partially filled at {}.'.format(side.title(), oid, price))
                self.position = int(data.position_qty)

            # order is rejected/cancelled
            elif event_type == 'rejected' or event_type == 'canceled':
                self.log(info='Order {} {}.'.format(oid, event_type))
                if self.current_order is not None and self.current_order.id == oid:
                    self.current_order = None

            # handle other events
            elif event_type != 'new':
                self.log(error='Unexpected event for order {}: {}.'.format(oid, event_type))

        # run all streams
        self.conn = conn
        self.log(info='Scalping strategy running.')
        conn.run([f'A.{self.symbol}', f'AM.{self.symbol}', 'trade_updates'])


    def run(self):
        try: self._run()
        except KeyboardInterrupt: self.log(info='Scalping strategy stopping.')
        except Exception as e: self.log(error=str(e))

        # stop strategy
        self.api.cancel_all_orders()



if __name__ == '__main__':
    trader = ScalpStrategy(verbose=True, test=True)
    trader.run()