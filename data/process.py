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
    return [dtype(val) for val in row_s[2:]]


def preload_data():
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
    return day_data[index + 5][2] 


def process_data(raw_data):
    x, y = [], []
    for day_data in raw_data:

        # loop over select bars
        for i in range(DAY_START_MARGIN, BARS_PER_DAY - DAY_END_MARGIN):
            row = day_data[i]
            x.append(row)
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