import requests
import time
import csv


# customizable presets
TICKER = 'AAPL'

# api data
URL_START = 'https://api.polygon.io/v2/aggs/ticker/{}/range/1/minute/'.format(TICKER)
URL_END = '?apiKey=AK952QW390M7XSKYCHQQ'

# market timing data
LOCAL_MARKET_OPEN_HOUR = 8
LOCAL_MARKET_OPEN_MINUTE = 30
LOCAL_MARKET_CLOSE_HOUR = 15
MARKET_MINUTE_BAR_COUNT = 390
EARLY_CLOSE_DATES = set([
    '2017-07-03', '2018-07-03', '2019-07-03',
    '2017-11-24', '2018-11-23', '2019-11-29',
    '2018-12-24', '2019-12-24'
])


def validate_bar(last_time, date, hour, minute):
    '''Verifiy validity of minute bar timing.'''

    # verify market hours
    if hour < LOCAL_MARKET_OPEN_HOUR or hour >= LOCAL_MARKET_CLOSE_HOUR: return True, False
    elif hour == LOCAL_MARKET_OPEN_HOUR and minute < LOCAL_MARKET_OPEN_MINUTE: return True, False

    # verify continuity
    if last_time:
        if minute > 0 and (last_time[0] != hour or last_time[1] + 1 != minute): return False, True
        elif minute == 0 and (last_time[0] + 1 != hour or last_time[1] != 59): return False, True

    return True, True


def write_data(writer, date, results):
    '''Write valid input and label data to CSV.'''

    last_time = None
    minute_bars = 0

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

        # check invalid bar error
        if not valid_flag:
            print('Validation error on {} @ {}:{}'.format(date, hour, minute))
            return False

        # write valid bar
        elif mh_flag and hour < LOCAL_MARKET_CLOSE_HOUR - 1:
            bar_5 = results[i + 5]
            bar_15 = results[i + 15]
            bar_30 = results[i + 30]
            bar_60 = results[i + 60]

            # build data row
            data = [

                # input
                date,
                hour,
                minute,
                bar['n'],
                bar['v'],
                bar['vw'],
                bar['o'],
                bar['c'],
                bar['h'],
                bar['l'],

                # labels
                bar_5['c'],
                bar_15['c'],
                bar_30['c'],
                bar_60['c']
            ]

            # write data row
            writer.writerow(data)
            last_time = (hour, minute)
            minute_bars += 1

        # end after closing hours
        elif hour >= LOCAL_MARKET_CLOSE_HOUR - 1: break

    # verify valid bar count
    if minute_bars != MARKET_MINUTE_BAR_COUNT - 60: return False
    else: return True


def collect_data():
    '''Collect, verify, and write all market data in three year period.'''

    with open('raw.nosync/{}.csv'.format(TICKER), 'w+') as raw_file:
        file_writer = csv.writer(raw_file)

        # loop through years
        for y in range(3):
            year = 2017 + y
            year_str = str(year)
            valid_days = 0

            # loop through months
            for m in range(12):
                month = m + 1
                month_str = str(month) if month >= 10 else '0' + str(month)
                print('UPDATE: {}/{}'.format(month_str, year_str))

                # loop through days
                for d in range(31):
                    day = d + 1
                    day_str = str(day) if day >= 10 else '0' + str(day)

                    # build target date
                    date = '{}-{}-{}'.format(year_str, month_str, day_str)
                    if date in EARLY_CLOSE_DATES:
                        print('Market holiday on {}'.format(date))
                        continue

                    # fetch data
                    r = requests.get(URL_START + '{}/{}'.format(date, date) + URL_END)
                    r_data = r.json()

                    # verify data
                    if r_data['status'] == 'ERROR':
                        print('Retrieval error on {}: {}'.format(date, r_data['error']))
                    elif r_data['resultsCount'] == 0:
                        print('Market closed on {}'.format(date))
                    else:
                        valid_flag = write_data(file_writer, date, r_data['results'])
                        if valid_flag: valid_days += 1
                        else: return

            # print trading days count
            print('Total trading days in {}: {}'.format(year_str, valid_days))


if __name__ == '__main__':
    collect_data()
