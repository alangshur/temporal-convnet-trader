from tcn.tcn import TemporalConvNet
from utils.field import config
import tensorflow as tf
import numpy as np
import random
import os
import csv

# disable warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.system('clear')


# customizable presets
TICKER = 'SPY'
MULT = 5
NUM_CLASSES = 1
EPOCHS = 10
BATCHES_PER_EPOCH = 32
BATCH_SIZE = 64
WINDOW_BARS_SIZE = 1170
INPUT_CHANNELS = 1
BLOCK_CONFIG = config
TOTAL_DAYS = 2508
DAYS_BUFFER = 30


def preload_data(t_file):
    with open(t_file, 'r') as f:
        reader = csv.reader(f)
        raw_data, data = [], []
        cur_idx = -1

        while True:
            try: 
                row = next(reader)
                idx = row[0]
                val = float(row[1])

                if idx != cur_idx:
                    if len(data): raw_data.append(data)
                    data = []
                    cur_idx = idx
                
                data.append(val)
            except StopIteration: 
                raw_data.append(data)
                break

    return raw_data


# fetch data
x = preload_data('../data/{}.nosync/{}m-x.csv'.format(TICKER, MULT))
y = preload_data('../data/{}.nosync/{}m-y.csv'.format(TICKER, MULT))

# build model
print('Building model...')
net = TemporalConvNet('temp-convnet', BLOCK_CONFIG, NUM_CLASSES)
net.build((None, WINDOW_BARS_SIZE, INPUT_CHANNELS))
net.summary()

# compile model
print('\nCompiling model...')
net.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.BinaryCrossentropy(),
    metrics=[
        tf.keras.metrics.Accuracy(),
        tf.keras.metrics.Precision(),
        tf.keras.metrics.Recall()
    ]
)

# train model
for epoch in range(EPOCHS):
    print('\n\nEpoch {}...'.format(epoch + 1))
    
    # get instance indices
    samples = random.sample(
        range(DAYS_BUFFER, TOTAL_DAYS), 
        BATCHES_PER_EPOCH * BATCH_SIZE
    )

    # build batches
    batches_x, batches_y = [], []
    for e in range(BATCHES_PER_EPOCH):
        batch_x, batch_y = [], []
        
        # build epoch batches
        for b in range(BATCH_SIZE):
            idx = samples[e * BATCH_SIZE + b]
            data_seg = []

            for buf in range(DAYS_BUFFER):
                space = WINDOW_BARS_SIZE - len(data_seg)
                data = x[idx - buf]
                if space > len(data): 
                    data_seg = data + data_seg
                else:
                    data_seg = data[-space:] + data_seg
                    break

            batch_x.append(data_seg)
            batch_y.append(y[idx][-1])
        
        # append batch
        batches_x.append(np.expand_dims(np.array(batch_x), -1))
        batches_y.append(np.array(batch_y))
    
    # iterate batches
    for batch in range(BATCHES_PER_EPOCH):
        batch_x = batches_x[batch]
        batch_y = batches_y[batch]

        # reset metrics
        reset_metrics = False
        if batch == 0: reset_metrics = True
        
        # train on batch
        metrics = net.train_on_batch(
            batch_x,
            batch_y,
            reset_metrics=reset_metrics
        )

        # print batch data
        print('Batch {}/{} | Loss: {}, Accuracy: {}, Precision: {}, Recall: {}'.format(
            batch + 1, BATCHES_PER_EPOCH, metrics[0], metrics[1], metrics[2], metrics[3]
        ), end='\r')
