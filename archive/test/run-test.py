import csv
from matplotlib import pyplot as plt
import numpy as np
import talib

# init constants
DT_INDEX = 0
OPEN_INDEX = 1
HIGH_INDEX = 2
LOW_INDEX = 3
CLOSE_INDEX = 4
VOL_INDEX = 5
START = 45606
END = 58597

# open file
f = open('../data/SPY_25/AAPL.csv', 'r')
data = np.array(list(csv.reader(f)))[START:END]
dt = data[:, DT_INDEX].astype(np.datetime64)
op = data[:, OPEN_INDEX].astype(np.float64)
hi = data[:, HIGH_INDEX].astype(np.float64)
lo = data[:, LOW_INDEX].astype(np.float64)
cl = data[:, CLOSE_INDEX].astype(np.float64)
vol = data[:, VOL_INDEX].astype(np.float64)


# atr = talib.ATR(hi, lo, cl, timeperiod=7)
sd = talib.STDDEV(cl, timeperiod=260)

run_dir = None
total_runs = 0
total_sessions = 0
rrs = []

for i in range(data.shape[0]):
    o, c = op[i], cl[i]
    bar_dir = int(c > o)
    if run_dir is None: run_dir = bar_dir
    elif run_dir != bar_dir: 
        total_runs += 1
        run_dir = bar_dir
    total_sessions += 1
    
    if total_sessions % 260 == 0:
        rrs.append(total_runs / total_sessions)
        run_dir = None
        total_runs = 0
        total_sessions = 0

rrs = np.array(rrs)
print('RR Mean: {}'.format(rrs.mean()))
print('RR STD: {}'.format(rrs.std()))
print('SD Mean: {}'.format(sd[260:].mean()))
print('SD STD: {}'.format(sd[260:].std()))
