from config import ROW_INDICES, ORDER_TYPES, ORDER_DIRS



class OrderManager:
    def __init__(self, balance_manager):

        # attach balance
        self.balance_manager = balance_manager

        # init position data
        self.position = None
        self.limit_orders = []
        self.stop_orders = []

        # init market data
        self.market_price = None


    def update(self, bar):
        self.market_price = bar[ROW_INDICES.CLOSE]


    def add_order(self, o_type, o_dir=None, o_size=None, o_price=None):

        # market order
        if o_type == ORDER_TYPES.MARKET:

            # modify existing position
            if self.position:
                pos_dir, pos_size = self.position

                # reinforce long position
                if pos_dir == ORDER_DIRS.LONG and o_dir == ORDER_DIRS.LONG:
                    self.position = (pos_dir, pos_size + o_size)
                    self.balance_manager.update(-(self.market_price * o_size))

                # reinforce short position
                elif pos_dir == ORDER_DIRS.SHORT and o_dir == ORDER_DIRS.SHORT:
                    self.position = (pos_dir, pos_size + o_size)
                    self.balance_manager.update(-(self.market_price * o_size))

                # change position to short
                elif pos_dir == ORDER_DIRS.LONG and o_dir == ORDER_DIRS.SHORT:
                    if o_size > pos_size:
                        self.position = (ORDER_DIRS.SHORT, o_size - pos_size)
                        size_change = 2 * pos_size - o_size
                    elif pos_size > o_size: 
                        self.position = (pos_dir, pos_size - o_size)
                        size_change = o_size
                    else: 
                        self.position = None
                        size_change = pos_size
                    self.balance_manager.update(self.market_price * size_change)

                # change position to long
                elif pos_dir == ORDER_DIRS.SHORT and o_dir == ORDER_DIRS.LONG:
                    if o_size > pos_size: 
                        self.position = (ORDER_DIRS.LONG, o_size - pos_size)
                        size_change = 2 * pos_size - o_size
                    elif pos_size > o_size: 
                        self.position = (pos_dir, pos_size - o_size)
                        size_change = o_size
                    else: 
                        self.position = None
                        size_change = pos_size
                    self.balance_manager.update(self.market_price * size_change)

            # add new position
            else: 
                self.position = (o_dir, o_size)
                self.balance_manager.update(-(self.market_price * o_size))

        # close-position order
        elif o_type == ORDER_TYPES.CLOSE:
            if self.position:
                pos_dir, pos_size = self.position
                self.balance_manager.update(self.market_price * pos_size)
                self.position = None