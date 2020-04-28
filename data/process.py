import numpy as np
import random
import time
import csv


# customizable presets
TICKER = 'AAPL'
RETURN_MARGIN_5 = 0.00025
RETURN_MARGIN_15 = 0.00075
RETURN_MARGIN_30 = 0.0015
RETURN_MARGIN_60 = 0.003
DPS_PER_FILE = 5

# data constants
BARS_PER_DAY = 330
BARS_DAY_OFFSET = 60
MAX_BARS_PER_DP = 329
HOUR_MAX = 13
HOUR_MIN = 8
MINUTE_MAX = 59
MINUTE_MIN = 0


def get_prog_bar(current, total, barLength=20):
    '''Compute data for progress bar.'''

    percent = float(current) / total * 100
    arrow   = '-' * int(percent / 100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    return arrow, spaces, percent


def get_new_min_max(row):
    '''Pre-fill new min/max states with initial row data.'''

    return {
        'max_objects': row[3],
        'min_objects': row[3],
        'max_volume': row[4],
        'min_volume': row[4],
        'max_vwap': row[5],
        'min_vwap': row[5],
        'max_open': row[6],
        'min_open': row[6],
        'max_close': row[7],
        'min_close': row[7],
        'max_high': row[8],
        'min_high': row[8],
        'max_low': row[9],
        'min_low': row[9]
    }


def update_min_max(mm, row):
    '''Update min/max states for new row data.'''

    return {
        'max_objects': mm['max_objects'] if mm['max_objects'] >= row[3] else row[3],
        'min_objects': mm['min_objects'] if mm['min_objects'] <= row[3] else row[3],
        'max_volume': mm['max_volume'] if mm['max_volume'] >= row[4] else row[4],
        'min_volume': mm['min_volume'] if mm['min_volume'] <= row[4] else row[4],
        'max_vwap': mm['max_vwap'] if mm['max_vwap'] >= row[5] else row[5],
        'min_vwap': mm['min_vwap'] if mm['min_vwap'] <= row[5] else row[5],
        'max_open': mm['max_open'] if mm['max_open'] >= row[6] else row[6],
        'min_open': mm['min_open'] if mm['min_open'] <= row[6] else row[6],
        'max_close': mm['max_close'] if mm['max_close'] >= row[7] else row[7],
        'min_close': mm['min_close'] if mm['min_close'] <= row[7] else row[7],
        'max_high': mm['max_high'] if mm['max_high'] >= row[8] else row[8],
        'min_high': mm['min_high'] if mm['min_high'] <= row[8] else row[8],
        'max_low': mm['max_low'] if mm['max_low'] >= row[9] else row[9],
        'min_low': mm['min_low'] if mm['min_low'] <= row[9] else row[9]
    }


def normalize_time(val, min, max):
    '''Normalize time data to range [-1, 1].'''

    return 2 * (val - min) / (max - min) - 1


def normalize_data(val, label, mm):
    '''Normalize arbitrary data to range [-1, 1].'''

    max = mm['max_' + label]
    min = mm['min_' + label]
    if max - min == 0: return 0.0
    else: return 2 * (val - min) / (max - min) - 1


def convert_row_dtype(row_s, dtype=float):
    '''Convert data-type of row (except date string).'''

    ds = [row_s[0]]
    return ds + [dtype(val) for val in row_s[1:]]


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


def process_data(raw_data):
    '''Process raw data and write each datapoint.'''

    # loop over raw days
    cur_x, cur_y = [], []
    file_count = 0
    day_count = 0
    for day_data in raw_data:
        print('Progress: [%s%s] %d %%' % get_prog_bar(
            day_count, len(raw_data)), end='\r')

        # loop over each dp end
        for end in range(BARS_DAY_OFFSET + 1, BARS_PER_DAY + 1):
            dp = []

            # collect min/max
            min_max = get_new_min_max(day_data[0])
            for val in range(1, end):
                row = day_data[val]
                min_max = update_min_max(min_max, row)

            # build datapoint
            last_row = day_data[0]
            for val in range(1, end):
                row = day_data[val]
                dp.append([
                    normalize_time(row[1], HOUR_MIN, HOUR_MAX),  # normalized hour
                    normalize_time(row[2], MINUTE_MIN, MINUTE_MAX),  # normalized minute
                    normalize_data(row[3], 'objects', min_max),  # normalized objects
                    (row[3] - last_row[3]) / last_row[3],  # objects return
                    normalize_data(row[4], 'volume', min_max),  # normalized volume
                    (row[4] - last_row[4]) / last_row[4],  # volume return
                    normalize_data(row[5], 'vwap', min_max),  # normalized vwap
                    (row[5] - last_row[5]) / last_row[5],  # vwap return
                    normalize_data(row[6], 'open', min_max),  # normalized open
                    (row[6] - last_row[7]) / last_row[7],  # open return
                    normalize_data(row[7], 'close', min_max),  # normalized close
                    (row[7] - last_row[7]) / last_row[7],  # close return
                    normalize_data(row[8], 'high', min_max),  # normalized high
                    (row[8] - last_row[7]) / last_row[7],  # high return
                    normalize_data(row[9], 'low', min_max),  # normalized low
                    (row[9] - last_row[7]) / last_row[7],  # low return
                ])
                last_row = row
            
            # pad inputs
            dp_arr = np.array(dp)
            dp_pad = np.pad(
                dp_arr, 
                ((MAX_BARS_PER_DP - len(dp), 0), (0, 0)), 
                'constant'
            )

            # add inputs and labels
            cur_x.append(dp_pad)
            cur_y.append(np.array([
                int(((last_row[10] - last_row[7]) / last_row[7]) >= RETURN_MARGIN_5),  # 5-bar return label
                int(((last_row[11] - last_row[7]) / last_row[7]) >= RETURN_MARGIN_15),  # 15-bar return label
                int(((last_row[12] - last_row[7]) / last_row[7]) >= RETURN_MARGIN_30),  # 30-bar return label
                int(((last_row[13] - last_row[7]) / last_row[7]) >= RETURN_MARGIN_60),  # 60-bar return label
            ]))

            # save array as numpy file 
            if len(cur_x) >= DPS_PER_FILE:
                x, y = np.array(cur_x), np.array(cur_y)
                np.savez('proc.nosync/{}-{}.npz'.format(TICKER, file_count), x=x, y=y)
                file_count += 1
                cur_x, cur_y = [], []

        # increment day
        day_count += 1


if __name__ == '__main__':

    # pre-load data
    print('Pre-loading data...')
    raw_data = preload_data()
    
    # process data
    print('\nProcessing data...')
    process_data(raw_data)
    print('\n\nFinished!')