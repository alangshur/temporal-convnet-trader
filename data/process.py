import numpy as np
import random
import time
import csv

# customizable presets
TICKER = 'GDX'

# data constants
BARS_PER_DAY = 390
DAY_START_MARGIN = 15
DAY_END_MARGIN = 15

def convert_row_dtype(row_s, dtype=float):
    '''Convert data-type of row (except date string).'''

    return [dtype(val) for val in row_s[2:]]


def preload_data():
    '''Pre-load raw per-day data from CSV.'''

    raw_data = []
    with open('raw.nosync/{}.csv'.format(TICKER), 'r') as raw_file:
        reader = csv.reader(raw_file)
        
        # split data by day
        while True:
            day_data = []
            for i in range(BARS_PER_DAY):
                try: 
                    row_s = next(reader)
                    row = convert_row_dtype(row_s)
                    day_data.append(row)
                except StopIteration: break
            if not len(day_data): break
            else: raw_data.append(day_data)

    return raw_data


def get_label(index, day_data):
    # v = day_data[index][2]

    # # get future states
    # f_1 = bool(day_data[index + 1][2] > v)
    # f_3 = bool(day_data[index + 3][2] > v)
    # f_6 = bool(day_data[index + 6][2] > v)
    # f_9 = bool(day_data[index + 9][2] > v)
    # f_12 = bool(day_data[index + 12][2] > v)
    # f_15 = bool(day_data[index + 15][2] > v)

    # # return label
    # if f_1 and f_3 and f_6 and f_9 and f_12 and f_15: return 1.0
    # else: return 0.0

    v = day_data[index][2]
    v_5 = day_data[index + 15][2]
    if v_5 > v: return 1.0
    else: return 0.0


def process_data(raw_data):
    '''Process raw data and write each datapoint.'''

    x, y = [], []
    for day_data in raw_data:

        # loop over select bars
        for i in range(DAY_START_MARGIN, BARS_PER_DAY - DAY_END_MARGIN):
            last_row = day_data[i - 1]
            row = day_data[i]

            # add input data
            x.append([
                (row[0] - last_row[0]) / last_row[0],  # volume return
                # (row[1] - last_row[2]) / last_row[2],  # open/close return
                (row[2] - last_row[2]) / last_row[2],  # close/open return
                # (row[3] - row[1]) / row[1],  # high/open return
                # (row[4] - row[1]) / row[1],  # low/open return
            ])

            # add label data
            y.append(get_label(i, day_data))
    
    # save data as numpy files
    x, y = np.array(x), np.array(y)
    np.savez('proc.nosync/{}.npz'.format(TICKER), x=x, y=y)


if __name__ == '__main__':

    # pre-load data
    print('Pre-loading data...')
    raw_data = preload_data()
    
    # process data
    print('Processing data...')
    process_data(raw_data)
    print('Done!')