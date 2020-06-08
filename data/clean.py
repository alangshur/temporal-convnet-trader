import pandas_market_calendars as mcal
from datetime import datetime
from os import walk
from tqdm import tqdm
import csv

def get_market_holidays(start_date, end_date):
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    valid_days = nyse.valid_days(start_date=start_date, end_date=end_date)
    early_days = nyse.early_closes(schedule=schedule)
    valid_dates = [str(t.date()) for t in valid_days.to_list()]
    early_dates = [str(t.date()) for t in early_days.index.to_list()]
    comb_dates = list(set(valid_dates).union(set(early_dates)))
    dates = sorted(comb_dates, key=lambda d: datetime.strptime(d, '%Y-%m-%d'))
    return dates, set(early_dates)

def get_filenames(path):
    fs = []
    for (dirpath, dirnames, filenames) in walk(path): 
        fs.extend(filenames)
    return fs

def open_files(targets, path):
    datas = []
    for target in targets:
        reader = csv.reader(open(path + target, 'r'))
        datas.append(list(reader))
    return datas

def write_files(targets, datas, path):
    for target, data in zip(targets, datas):
        writer = csv.writer(open(path + target, 'w+'))
        writer.writerows(data)


if __name__ == "__main__":
    path = 'UNI/'
    clean_path = 'UNI_clean/'

    # get dates
    start_date, end_date = '2010-01-01', '2020-06-05'
    dates, early_dates = get_market_holidays(start_date, end_date)
    total_errors = 0
    max_errors = 0

    # get files
    targets = get_filenames(path)
    datas = open_files(targets, path)

    # clean data
    clean_datas = []
    for data in tqdm(datas):
        clean_data = []
        last_dp = None
        index = 0
        errors = 0

        for date in dates:
            if date in early_dates: bars = 7
            else: bars = 13

            for bar in range(bars):
                minute = (30 + bar * 30) % 60
                hour = 8 + (30 + bar * 30) // 60
                minute_str = str(minute) if minute >= 10 else '0' + str(minute)
                hour_str = str(hour) if hour >= 10 else '0' + str(hour)
                time_str = hour_str + ':' + minute_str + ':00'
                dt_str = date + ' ' + time_str
                
                dp = data[index]
                if dp[0] != dt_str: 
                    clean_data.append([dt_str] + last_dp[1:])
                    errors += 1
                else: 
                    clean_data.append(dp)
                    index += 1
                last_dp = dp

        total_errors += errors
        if errors > max_errors: max_errors = errors
        clean_datas.append(clean_data)

    # write files
    write_files(targets, clean_datas, clean_path)

    # print errors
    print('\nTotal errors: {}'.format(total_errors))
    print('Max errors: {}'.format(max_errors))
