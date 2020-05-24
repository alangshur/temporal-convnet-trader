import csv

def preload_data():
    raw_data = []

    with open('raw.nosync/{}.csv'.format('GDX'), 'r') as raw_file:
        reader = csv.reader(raw_file)
        
        while True:
            day_data = []
            for i in range(390):
                try: 
                    row = next(reader)
                    day_data.append(row)
                except StopIteration: break
                
            if not len(day_data): break
            else: raw_data.append(day_data)

    return raw_data

def write_data(raw_data):

    with open('raw.nosync/{}.csv'.format('GDX'), 'w+') as raw_file:
        writer = csv.writer(raw_file)

        for day in data:
            for i in range(390):
                h = str(8 + (30 + i) // 60)
                h = '0' + h if len(h) == 1 else h
                m = str((30 + i) % 60)
                m = '0' + m if len(m) == 1 else m
                time = h + ':' + m + ':00'

                # custom row format
                row = [day[i][0] + ' ' + time] \
                    + [day[i][2]] + [day[i][3]] \
                    + [day[i][5]] + [day[i][6]] \
                    + [day[i][4]]
                
                writer.writerow(row)

data = preload_data()
write_data(data)