from os import walk
from tqdm import tqdm
import csv

# get filenames
fs = []
for (dirpath, dirnames, filenames) in walk('min'): 
    fs.extend(filenames)
fs = [f.split('.')[0] for f in fs]

# get number of rows
lengths = []
for f in tqdm(fs):
    df = open('min/' + f + '.csv', 'r')
    length = len(list(csv.reader(df)))
    lengths.append(length)
    df.close()

# print results
print()
for f, length in zip(fs, lengths):
    print('{}: {} rows'.format(f, length))