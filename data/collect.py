import requests
import time
import csv


# customizable presets
TICKER = 'AAPL'
START_YEAR = 2015
END_YEAR = 2020

# api data
URL_START = 'https://api.polygon.io/v2/aggs/ticker/{}/range/1/minute/'.format(TICKER)
URL_END = '?apiKey=AK952QW390M7XSKYCHQQ'

# market timing data
LOCAL_MARKET_OPEN_HOUR = 8
LOCAL_MARKET_OPEN_MINUTE = 30
LOCAL_MARKET_CLOSE_HOUR = 15
MARKET_MINUTE_BAR_COUNT = 390


def validate_bar(last_time, date, hour, minute):

    # verify market hours
    if hour < LOCAL_MARKET_OPEN_HOUR or hour >= LOCAL_MARKET_CLOSE_HOUR: return True, False
    elif hour == LOCAL_MARKET_OPEN_HOUR and minute < LOCAL_MARKET_OPEN_MINUTE: return True, False

    # verify continuity
    if last_time:
        if minute > 0 and (last_time[0] != hour or last_time[1] + 1 != minute): return False, True
        elif minute == 0 and (last_time[0] + 1 != hour or last_time[1] != 59): return False, True

    return True, True


def write_data(writer, date, results):
    last_time = None
    minute_bars = 0
    data_all = []

    # write each bar in results
    for i in range(len(results)):
        bar = results[i]

        # get bar timing
        timestamp = bar['t']
        localtime = time.localtime(timestamp / 1000)
        hour = int(time.strftime('%H', localtime))
        minute = int(time.strftime('%M', localtime))

        # verify bar
        valid_flag, mh_flag = validate_bar(last_time, date, hour, minute)
        if hour >= LOCAL_MARKET_CLOSE_HOUR: break

        # check invalid bar error
        if not valid_flag:
            print('Missing full data on {}'.format(date))
            break

        # write valid bar
        elif mh_flag:
            
            # format time strings
            hour_str = str(hour)
            hour_str = '0' + hour_str if len(hour_str) == 1 else hour_str
            min_str = str(minute)
            min_str = '0' + min_str if len(min_str) == 1 else min_str
            time_str = date + ' ' + hour_str + ':' + min_str + ':00'

            # build data row
            data = [
                time_str,
                bar['v'],
                bar['o'],
                bar['h'],
                bar['l'],
                bar['c'],
            ]

            # write data row
            data_all.append(data)
            last_time = (hour, minute)
            minute_bars += 1

    # bulk write bars
    if minute_bars == MARKET_MINUTE_BAR_COUNT: 
        writer.writerows(data_all)


def collect_data():
    with open('raw.nosync/{}.csv'.format(TICKER), 'w+') as raw_file:
        file_writer = csv.writer(raw_file)

        # loop through years
        for year in range(START_YEAR, END_YEAR + 1):
            year_str = str(year)

            # loop through months
            if year == 2020: months = 4
            else: months = 12
            for month in range(1, months + 1):
                month_str = str(month) if month >= 10 else '0' + str(month)
                print('\nProgress: {}/{}\n'.format(month_str, year_str))

                # loop through days
                for day in range(1, 32):
                    day_str = str(day) if day >= 10 else '0' + str(day)

                    # fetch data
                    date = '{}-{}-{}'.format(year_str, month_str, day_str)
                    r = requests.get(URL_START + '{}/{}'.format(date, date) + URL_END)
                    r_data = r.json()

                    # verify data
                    if r_data['status'] == 'ERROR': continue
                    elif r_data['resultsCount'] == 0: print('Market closed on {}'.format(date))
                    else: write_data(file_writer, date, r_data['results'])

if __name__ == '__main__':
    collect_data()
