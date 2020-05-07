from config import ROW_INDICES, ORDER_TYPES, ORDER_DIRS



class OrderManager:
    def __init__(self, balance_manager):

        # attach balance
        self.balance_manager = balance_manager

        # init position data
        self.position = 0
        self.limit_orders = []
        self.stop_orders = []

        # init market data
        self.market_price = None


    def update(self, bar):
        self.market_price = bar[ROW_INDICES.CLOSE]


    def add_order(self, o_type, o_dir=None, o_size=None, o_price=None):

        # market order
        if o_type == ORDER_TYPES.MARKET:
            
            # increase long position
            if o_dir == ORDER_DIRS.LONG and o_size > 0:
                self.position += o_size
                self.balance_manager.update(-(self.market_price * o_size))

            # decrease long position
            elif o_dir == ORDER_DIRS.SHORT and o_size > 0 and self.position >= o_size:
                self.position -= o_size
                if self.position == 0: self.balance_manager.update(self.market_price * o_size, position_closed=True)
                else: self.balance_manager.update(self.market_price * o_size)

        # close-position order
        elif o_type == ORDER_TYPES.CLOSE:
            if self.position > 0:
                self.balance_manager.update(self.market_price * self.position, position_closed=True)
                self.position = 0