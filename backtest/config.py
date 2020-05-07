from collections import namedtuple



# general data constants
BARS_PER_DAY = 390


# OHLC data indices
_R_I = namedtuple('_R_I', 'DATETIME VOLUME OPEN HIGH LOW CLOSE')
ROW_INDICES = _R_I(0, 1, 2, 3, 4, 5)


# order types 
_O_T = namedtuple('_O_T', 'MARKET CLOSE LIMIT STOP')
ORDER_TYPES = _O_T(0, 1, 2, 3)


# order directions
_O_D = namedtuple('_O_D', 'LONG SHORT')
ORDER_DIRS = _O_D(0, 1)