from tcn.tcn import TemporalConvNet
import tensorflow as tf
import numpy as np
import random
import os

# disable warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.system('clear')


# customizable presets
TICKER = 'GDX'
NUM_CLASSES = 1
EPOCHS = 10
BATCHES_PER_EPOCH = 128
BATCH_SIZE = 512
WINDOW_BARS_SIZE = 120
INPUT_CHANNELS = 5
BLOCK_CONFIG = [{
    'filter_count': 16,
    'kernel_size': 9,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 16,
    'kernel_size': 9,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 16,
    'kernel_size': 9,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 16,
    'kernel_size': 9,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 16,
    'kernel_size': 9,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}]

# data constants
TOTAL_DAYS = 696
BARS_PER_DAY = 360
TOTAL_BARS = 250560


# fetch data
arrays = np.load('../data/proc.nosync/{}.npz'.format(TICKER))
x, y = arrays['x'], arrays['y']

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
    true_bars_per_day = BARS_PER_DAY - WINDOW_BARS_SIZE
    total_true_bars = true_bars_per_day * TOTAL_DAYS
    samples = random.sample(
        range(total_true_bars), 
        BATCHES_PER_EPOCH * BATCH_SIZE
    )

    # build batches
    batches_x, batches_y = [], []
    for e in range(BATCHES_PER_EPOCH):
        batch_x, batch_y = [], []
        
        # build epoch batches
        for b in range(BATCH_SIZE):
            sample = samples[e * BATCH_SIZE + b]
            day = sample // true_bars_per_day
            bar = sample % true_bars_per_day
            start = (day * BARS_PER_DAY) + bar
            end = start + WINDOW_BARS_SIZE
            batch_x.append(x[start:end])
            batch_y.append(y[end - 1])
        
        # append batch
        batches_x.append(np.array(batch_x))
        batches_y.append(np.array(batch_y))

    # iterate batches
    for batch in range(BATCHES_PER_EPOCH):
        batch_x = batches_x[batch]
        batch_y = batches_y[batch]

        # reset metrics
        reset_metrics = False
        if batch == 0:
            reset_metrics = True
        
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
