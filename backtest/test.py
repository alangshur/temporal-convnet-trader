import csv
import numpy as np
from matplotlib import pyplot as plt
import talib

# init constants
DT_INDEX = 0
OPEN_INDEX = 1
HIGH_INDEX = 2
LOW_INDEX = 3
CLOSE_INDEX = 4
VOL_INDEX = 5
START = 1073251
END = 1463580

# open file
f = open('../data/UNI/SPY-1m.csv', 'r')
data = np.array(list(csv.reader(f)))[START:END]
dt = data[:, DT_INDEX].astype(np.datetime64)
op = data[:, OPEN_INDEX].astype(np.float64)
hi = data[:, HIGH_INDEX].astype(np.float64)
lo = data[:, LOW_INDEX].astype(np.float64)
cl = data[:, CLOSE_INDEX].astype(np.float64)
vol = data[:, VOL_INDEX].astype(np.float64)


kama = talib.KAMA(cl, timeperiod=8190)
sma = talib.SMA(cl, timeperiod=98280)

total = 0
event = 0
start_price = None
cur_duration = 0
durations = []

for i in range(data.shape[0]):
    if cl[i] > kama[i] and cl[i] > sma[i]:
        total += 1

        if start_price is None:
            start_price = cl[i]
        
        elif cl[i] < start_price:
            cur_duration += 1
            durations.append(cur_duration)

            start_price = None
            cur_duration = 0

        elif cl[i] > start_price + 0.10:
            cur_duration += 1
            durations.append(cur_duration)

            start_price = None
            cur_duration = 0

            event += 1

        else:
            cur_duration += 1



print('Win Rate: {}%'.format(round(event / total * 100, 3)))

# plot results
# plt.plot(dt, cl)
# plt.plot(dt, kama)
# plt.plot(dt, sma)
# plt.show()
