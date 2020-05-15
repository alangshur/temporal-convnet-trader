import numpy as np
import random
import time
import csv


# customizable presets
TICKER = 'SPY'
MULT = 5

# data constants
MARKET_BAR_COUNT = int(390 / MULT)
EARLY_MARKET_BAR_COUNT = int(210 / MULT)


def preload_data():
    with open('{}.nosync/{}m.csv'.format(TICKER, MULT), 'r') as raw_file:
        reader = csv.reader(raw_file)
        raw_data, data = [], []
        cur_date = ''

        while True:
            try: 
                row = next(reader)
                date = row[0].split(' ')[0]
                val = float(row[1])

                if date != cur_date:
                    if len(data): raw_data.append(data)
                    data = []
                    cur_date = date
                
                data.append(val)
            except StopIteration: 
                raw_data.append(data)
                break

    return raw_data


def process_data(raw_data):
    x, y = [], []
    for i in range(1, len(raw_data[:-1])):
        end = raw_data[i][-1]
        next_end = raw_data[i + 1][-1]
        s_ret = (next_end - end) / end

        for j in range(len(raw_data[i])):
            val = raw_data[i][j]
            if j == 0: prev = raw_data[i - 1][-1]
            else: prev = raw_data[i][j - 1]
            ret = (val - prev) / prev
            x.append([i - 1, ret])
            y.append([i - 1, int(s_ret > 0)])
    
    x_file = open('{}.nosync/{}m-x.csv'.format(TICKER, MULT), 'w+')
    y_file = open('{}.nosync/{}m-y.csv'.format(TICKER, MULT), 'w+')
    csv.writer(x_file).writerows(x)
    csv.writer(y_file).writerows(y)
    x_file.close()
    y_file.close()


if __name__ == '__main__':

    # pre-load data
    print('Pre-loading data...')
    raw_data = preload_data()

    # process data
    print('Processing data...')
    process_data(raw_data)
    print('Done!')