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
    def __init__(self, batch_size, validation_size):
        '''Initializes the processed data sequence.'''

        # initialize parameters
        self.batch_size = int(batch_size)
        self.validation_size = float(validation_size)
        self.dp_count = int(TOTAL_DAYS * DPS_PER_DAY)
        self.file_count = int(self.dp_count // DPS_PER_FILE)
        self.file_batch_size = int(batch_size // DPS_PER_FILE)

        # add validation parameters
        self.v_file_count = math.floor(self.file_count * self.validation_size)
        self.file_count -= self.v_file_count

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
        x = np.concatenate(x_arrs, axis=0)
        y = np.concatenate(y_arrs, axis=0)
        return x, y

    def on_epoch_end(self):
        '''Re-randomizes batches at the end of an epoch.'''

        self.randomize_batch_indices()

    def randomize_batch_indices(self):
        '''Randomizes file indices for a new set of batches.'''

        cur_batch = []
        self.batch_indices = []
        file_indices = list(range(self.file_count))
        random.shuffle(file_indices)

        # sort indices into batches
        for idx in file_indices:
            if len(cur_batch) >= self.file_batch_size: 
                self.batch_indices.append(cur_batch)
                cur_batch = []
            else: cur_batch.append(idx)
    
    def get_validation_set(self):   
        '''Fetches and concatenates processed arrays for validation set.'''

        x_arrs, y_arrs = [], []

        # load indexed files
        for f_idx in range(self.file_count, self.file_count + self.v_file_count):
            arrs = np.load('../data/proc.nosync/{}-{}.npz'.format(TICKER, f_idx))
            x_arrs.append(arrs['x'])
            y_arrs.append(arrs['y'])

        # concatenate arrays
        x = np.concatenate(x_arrs, axis=0)
        y = np.concatenate(y_arrs, axis=0)
        return x, y


seq = ProcessedSequence(50, 0.05)
x, y = seq[0]
print(x.shape)