import tensorflow as tf
import numpy as np
import random
import csv
import math 


# customizable presets
TICKER = 'AAPL'

# data constants
ROWS_PER_DAY = 52245
BARS_PER_DAY = 330
BARS_DAY_OFFSET = 60
TOTAL_DAYS = 746
DPS_PER_DAY = 270
BD_LENGTH = 16
BD_LABEL_POS = -4


class ProcessedSequence(tf.keras.utils.Sequence):
    def __init__(self):
        self.files = []
        for i in range(TOTAL_DAYS):
            f = open('../data/proc.nosync/{}-{}'.format(TICKER, i), 'r')
            r = csv.reader(f)
            self.files.append((f, r))

        self.batch_size = DPS_PER_DAY
        self.batch_count = TOTAL_DAYS
        self.dataset_size = TOTAL_DAYS * DPS_PER_DAY
        self.indices = random.shuffle(list(range(self.batch_count)))
    
    def __del__(self):
        for f, _ in self.files:
            f.close()

    def __len__(self):
        return self.batch_count 

    def __getitem__(self, index):
        true_index = self.indices[index]
        _, r = self.files[true_index]
        X, Y = [], []

        # add all dps
        for row in r:
            dp = []
            for i in range(len(row) // BD_LENGTH):
                dp.append(row[i * BD_LENGTH:(i + 1) * BD_LENGTH])

            # add data/labels
            X.append(dp)
            Y.append(row[BD_LABEL_POS:])
        
        # convert data formats
        X = np.array(X, dtype=np.float64)
        Y = np.array(Y, dtype=np.uint32)
        return X, Y

    def on_epoch_end(self):
        self.indices = random.shuffle(list(range(self.batch_count)))

seq = ProcessedSequence()