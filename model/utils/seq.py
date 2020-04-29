import tensorflow as tf
import numpy as np
import random
import math 


# customizable presets
TICKER = 'AAPL'
DPS_PER_FILE = 5

# data constants
TOTAL_DAYS = 746
DPS_PER_DAY = 270


class ProcessedSequence(tf.keras.utils.Sequence):
    def __init__(self, batch_size, validation_size, test_size):
        '''Initializes the processed data sequence.'''

        # initialize parameters
        self.batch_size = int(batch_size)
        self.validation_size = float(validation_size)
        self.test_size = float(test_size)
        self.dp_count = int(TOTAL_DAYS * DPS_PER_DAY)
        self.file_count = int(self.dp_count // DPS_PER_FILE)
        self.file_batch_size = int(batch_size // DPS_PER_FILE)

        # add validation/test parameters
        self.v_file_count = math.floor(self.file_count * self.validation_size)
        self.t_file_count = math.floor(self.file_count * self.test_size)
        self.file_count -= self.v_file_count
        self.file_count -= self.t_file_count

        # randomize batch indices
        self.batch_count = int(self.file_count // self.file_batch_size)
        self.randomize_batch_indices()

    def __len__(self):
        '''Returns the number of batches.'''

        return self.batch_count

    def __getitem__(self, index):
        '''Fetches and concatenates arrays in indexed batch.'''

        file_indices = self.batch_indices[index]
        x_arrs, y_arrs = [], []

        # load indexed files
        for f_idx in file_indices:
            arrs = np.load('../data/proc.nosync/{}-{}.npz'.format(TICKER, f_idx))
            x_arrs.append(arrs['x'])
            y_arrs.append(arrs['y'])

        # concatenate arrays
        x = np.concatenate(x_arrs, axis=0).astype(np.float64)
        y = np.concatenate(y_arrs, axis=0).astype(np.float64)
        return x, y

    def on_epoch_end(self):
        '''Re-randomizes batches at the end of an epoch.'''

        self.randomize_batch_indices()

    def randomize_batch_indices(self):
        '''Randomizes file indices for a new set of batches.'''

        self.batch_indices = []
        file_indices = list(range(self.file_count))
        random.shuffle(file_indices)

        # sort indices into batches
        for i in range(self.batch_count):
            cur_batch = []
            for j in range(self.file_batch_size):
                pos = i * self.file_batch_size + j
                cur_batch.append(file_indices[pos])
            self.batch_indices.append(cur_batch)

    def get_validation_set(self):   
        '''Fetches and concatenates processed arrays for validation set.'''

        x_arrs, y_arrs = [], []

        # load indexed files
        start = self.file_count
        end = self.file_count + self.v_file_count
        for f_idx in range(start, end):
            arrs = np.load('../data/proc.nosync/{}-{}.npz'.format(TICKER, f_idx))
            x_arrs.append(arrs['x'])
            y_arrs.append(arrs['y'])

        # concatenate arrays
        x = np.concatenate(x_arrs, axis=0).astype(np.float64)
        y = np.concatenate(y_arrs, axis=0).astype(np.float64)
        return x, y

    def get_test_set(self):
        '''Fetches and concatenates processed arrays for test set.'''

        x_arrs, y_arrs = [], []

        # load indexed files
        start = self.file_count + self.v_file_count
        end = self.file_count + self.v_file_count + self.t_file_count
        for f_idx in range(start, end):
            arrs = np.load('../data/proc.nosync/{}-{}.npz'.format(TICKER, f_idx))
            x_arrs.append(arrs['x'])
            y_arrs.append(arrs['y'])

        # concatenate arrays
        x = np.concatenate(x_arrs, axis=0).astype(np.float64)
        y = np.concatenate(y_arrs, axis=0).astype(np.float64)
        return x, y