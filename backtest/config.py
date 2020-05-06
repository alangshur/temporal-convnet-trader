from collections import namedtuple
 
# OHLC data indices
_R_I = namedtuple('_R_I', 'DATETIME VOLUME OPEN HIGH LOW CLOSE')
ROW_INDICES = _R_I(0, 1, 2, 3, 4, 5)