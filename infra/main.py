import alpaca_trade_api as tradeapi
import numpy as np
import talib


class ScalpStrategy:


    def __init__(self, target_atr=0.4, start_size=0.20, take_size=0.07, 
                 stop_size=-0.04, timeout_time=30):

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

        # get account info
        account_info = self.api.get_account()
        self.equity = float(account_info.equity)
        self.multiplier = float(account_info.multiplier)


    def start_trading(self):

        # connect to stream
        conn = tradeapi.StreamConn(
            self.key_id,
            self.secret_key,
            self.base_url
        )


        @conn.on(r'A$', [self.symbol])
        async def handle_agg_s(conn, channel, data):
            self.seconds += 1

            # cancel expired order
            if self.current_order is not None and self.seconds > self.timeout_time:
                self.api.cancel_all_orders()


        @conn.on(r'AM$', [self.symbol])
        async def handle_agg_m(conn, channel, data):
            self.seconds = 0

            # append minute data
            self.min_his.append(data.high)
            self.min_los.append(data.low)
            self.min_cls.append(data.close)

            # calculate atr
            atr = talib.ATR(np.array(self.min_his), np.array(self.min_los), 
                np.array(self.min_cls), timeperiod=14)
            current_atr = atr[-1] if not np.isnan(atr[-1]) else 0.0

            # set order
            if current_atr >= self.target_atr and self.current_order is None and self.position == 0:
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


        @conn.on(r'trade_updates')
        async def handle_trade(conn, channel, data):
            event_type = data.event
            side = data.order['side']
            oid = data.order['id']

            # order is filled
            if event_type == 'fill' or event_type == 'partial_fill'
                self.position = int(data.position_qty)
                if self.current_order is not None and self.current_order.id == oid):
                    self.current_order = None

            # order is partially filled
            elif event_type == 'partial_fill':
                self.position = int(data.position_qty)

            # order is rejected/cancelled
            elif event_type == 'rejected' or event_type == 'canceled':
                if self.current_order and self.current_order.id == oid:
                    self.current_order = None

            elif event_type != 'new':
                print(f'Unexpected order event type received: {event_type}')

        conn.run([f'A.{self.symbol}', 'trade_updates'])




strat = ScalpStrategy()
