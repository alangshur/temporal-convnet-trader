import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
import csv
import talib

MODE = 'test'
INDICES = (19527, 29279) # 2016-2018

DT_INDEX = 0
OPEN_INDEX = 1
HIGH_INDEX = 2
LOW_INDEX = 3
CLOSE_INDEX = 4
VOL_INDEX = 5


# load data
print('Loading data... ', end='', flush=True)
with open('../data/UNI/UPRO.csv', 'r') as f:
    data = np.array(list(csv.reader(f)))[INDICES[0]:INDICES[1]]
    dt = data[:, DT_INDEX].astype(np.datetime64)
    op = data[:, OPEN_INDEX].astype(np.float64)
    hi = data[:, HIGH_INDEX].astype(np.float64)
    lo = data[:, LOW_INDEX].astype(np.float64)
    cl = data[:, CLOSE_INDEX].astype(np.float64)
    vol = data[:, VOL_INDEX].astype(np.float64)
print('Done.', flush=True)

# init stats
profit = 0
event_count = 0
total_count = 0
correct_dir = 0
next_body_sizes = []
next_tail_sizes = []
next_neck_sizes = []
next_neck_sizes_l = []
avg_bar_sizes = []

# calculate indicators
atr = talib.ATR(hi, lo, cl, timeperiod=7)
rsi = talib.RSI(cl, timeperiod=7)

# test hypothesis
print('Testing... ', end='', flush=True)
for i in range(data.shape[0] - 1):
    time = dt[i].astype(object)


    event_flag = (atr[i] >= 1)


    # long scalp event
    if event_flag:
        event_count += 1

        # calculate next bar data
        next_bar_range = hi[i + 1] - cl[i + 1]
        next_body_size = abs(cl[i + 1] - op[i + 1])
        next_bar_dir = int(cl[i + 1] > op[i + 1])

        # record next bar stats
        if next_bar_dir == 1:
            next_body_sizes.append(next_body_size)
            next_tail_sizes.append(op[i + 1] - lo[i + 1])
            next_neck_sizes.append(hi[i + 1] - cl[i + 1])
            correct_dir += 1

        elif next_bar_dir == 0:
            next_neck_sizes_l.append(hi[i + 1] - op[i + 1])


    # record general stats
    total_count += 1
    cur_bar_size = abs(cl[i] - op[i])
    avg_bar_sizes.append(cur_bar_size)
print('Done.\n', flush=True)

# print results
print('-----------RESULTS-----------')
print('Total bars tested: {}'.format(total_count))
print('Event rate: {}%'.format(round(event_count / total_count * 100, 3)))
print('Average bar size: {} USD'.format(round(np.mean(avg_bar_sizes), 3)))
print('Next body size (win) mean: {} USD'.format(round(np.mean(next_body_sizes), 3)))
print('Next body size (win) median: {} USD'.format(round(np.median(next_body_sizes), 3)))
print('Next body size (win) std: {} USD'.format(round(np.std(next_body_sizes), 3)))
print('Next body size (win) std-error: {} USD'.format(round(np.std(next_body_sizes) / np.sqrt(len(next_neck_sizes)), 3)))
print('Next tail size (win) mean: {} USD'.format(round(np.mean(next_tail_sizes), 3)))
print('Next tail size (win) median: {} USD'.format(round(np.median(next_tail_sizes), 3)))
print('Next tail size (win) std: {} USD'.format(round(np.std(next_tail_sizes), 3)))
print('Next neck size (win) mean: {} USD'.format(round(np.mean(next_neck_sizes), 3)))
print('Next neck size (win) median: {} USD'.format(round(np.median(next_neck_sizes), 3)))
print('Next neck size (win) std: {} USD'.format(round(np.std(next_neck_sizes), 3)))
print('Next neck size (loss) mean: {} USD'.format(round(np.mean(next_neck_sizes_l), 3)))
print('Next neck size (loss) median: {} USD'.format(round(np.median(next_neck_sizes_l), 3)))
print('Next neck size (loss) std: {} USD'.format(round(np.std(next_neck_sizes_l), 3)))
print('Prediction accuracy: {}%'.format(round(correct_dir / event_count * 100, 3)))
print('Simulation profit: {} USD'.format(round(profit, 3)))
print('-----------------------------')