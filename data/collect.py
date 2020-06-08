import pandas_market_calendars as mcal
from datetime import datetime
from json.decoder import JSONDecodeError
import requests
import time
import csv


# market timing data
MULT = 30
LOCAL_MARKET_OPEN_HOUR = 8
LOCAL_MARKET_OPEN_MINUTE = 30
LOCAL_MARKET_CLOSE_HOUR = 15
EARLY_LOCAL_MARKET_CLOSE_HOUR = 12
MARKET_BAR_COUNT = int(390 / MULT)
EARLY_MARKET_BAR_COUNT = int(210 / MULT)


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


def validate_bar(last_time, date, hour, minute):

    # verify market hours
    if hour < LOCAL_MARKET_OPEN_HOUR or hour >= LOCAL_MARKET_CLOSE_HOUR: return True, False
    elif hour == LOCAL_MARKET_OPEN_HOUR and minute < LOCAL_MARKET_OPEN_MINUTE: return True, False

    # verify continuity
    if last_time:
        if minute > 0 and (last_time[0] != hour or last_time[1] + MULT != minute): return False, True
        elif minute == 0 and (last_time[0] + 1 != hour or last_time[1] != 60 - MULT): return False, True

    return True, True


def write_data(writer, date, early_flag, results):
    last_time = None
    data_all = []
    bars = 0

    # write each bar in results
    for i in range(len(results)):
        bar = results[i]

        # get bar timing
        timestamp = bar['t']
        localtime = time.localtime(timestamp / 1000)
        hour = int(time.strftime('%H', localtime))
        minute = int(time.strftime('%M', localtime))

        # format time strings
        hour_str, min_str = str(hour), str(minute)
        hour_str = '0' + hour_str if len(hour_str) == 1 else hour_str
        min_str = '0' + min_str if len(min_str) == 1 else min_str
        time_str = date + ' ' + hour_str + ':' + min_str + ':00'

        # verify bar
        if hour >= LOCAL_MARKET_CLOSE_HOUR: break
        elif early_flag and hour >= EARLY_LOCAL_MARKET_CLOSE_HOUR: break
        else: valid_flag, mh_flag = validate_bar(last_time, date, hour, minute)

        # add bar
        if not valid_flag: break
        elif mh_flag:
            data_all.append([time_str, bar['o'], bar['h'], \
                bar['l'], bar['c'], bar['v']])
            last_time = (hour, minute)
            bars += 1
    
    # bulk write bars   
    if (not early_flag and bars == MARKET_BAR_COUNT) or \
        (early_flag and bars == EARLY_MARKET_BAR_COUNT):
        writer.writerows(data_all)
        return True
    else: return False


def collect_data(ticker, ticker_class, start_date='2010-01-01', end_date='2020-06-05'):

    # fetch market holidays
    dates, early_dates = get_market_holidays(start_date, end_date)        
    errors = 0

    # write data iteratively
    with open('{}/{}.csv'.format(ticker_class, ticker), 'w+') as raw_file:
        file_writer = csv.writer(raw_file)

        for date in dates:
            print('{}: {}'.format(ticker, date), end='\r')

            # fetch data
            while True:
                try:
                    url_mid = '{}/{}'.format(date, date)
                    r_data = requests.get(
                        'https://api.polygon.io/v2/aggs/ticker/{}/range/{}/minute/'.format(ticker, MULT) \
                        + url_mid \
                        + '?apiKey=AK952QW390M7XSKYCHQQ'
                    ).json()
                    break
                except JSONDecodeError:
                    continue

            # verify data
            if r_data['status'] == 'ERROR': continue
            elif r_data['resultsCount'] == 0: continue
            else: 
                early_flag = bool(date in early_dates)
                res = write_data(file_writer, date, early_flag, r_data['results'])
                if not res: errors += 1
    
    return errors


if __name__ == '__main__':

    # specify ticker targets
    # target_tickers = ['TQQQ', 'UPRO', 'TECL', 'TNA', 'NUGT']
    target_tickers = ['SSO', 'SDS']
    ticker_class = 'UNI'

    # iteratively collet ticker data
    for ticker in target_tickers:
        errors = collect_data(ticker, ticker_class)
        print('Loaded {}: {} errors'.format(ticker, errors))