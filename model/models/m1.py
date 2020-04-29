from tcn.tcn1 import TemporalConvNet
from utils.seq import ProcessedSequence
from utils.loss import MulticlassBinaryCrossEntropy
# from utils.metric import FiveMinuteAccuracy
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import random
import math
import os

# disable warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.system('clear')

# customizable presets
TICKER = 'AAPL'
DPS_PER_FILE = 5
NUM_CLASSES = 4
INPUT_CHANNELS = 16
TIMESTEPS = 329
BLOCK_CONFIG = [{
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 1,
    'activation_func': tf.nn.elu,
    'res_activation_func': tf.nn.elu,
    'dropout_rate': 0
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 2,
    'activation_func': tf.nn.elu,
    'res_activation_func': tf.nn.elu,
    'dropout_rate': 0
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 2,
    'activation_func': tf.nn.elu,
    'res_activation_func': tf.nn.elu,
    'dropout_rate': 0
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 3,
    'activation_func': tf.nn.elu,
    'res_activation_func': tf.nn.elu,
    'dropout_rate': 0
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 3,
    'activation_func': tf.nn.elu,
    'res_activation_func': tf.nn.elu,
    'dropout_rate': 0
}]

# data constants
TOTAL_DAYS = 746
DPS_PER_DAY = 270

# build model
print('Building model...')
net = TemporalConvNet('temp-convnet', BLOCK_CONFIG, NUM_CLASSES)
net.build((None, TIMESTEPS, INPUT_CHANNELS))
net.summary()

# compile model
print('\nCompiling model...')
net.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=MulticlassBinaryCrossEntropy(),
    metrics=[
        tf.keras.metrics.Precision(),
        tf.keras.metrics.Recall()
    ]
)

# get data sequence
print('\nFetching data sequence...')
seq = ProcessedSequence(50, 0.1, 0.1)
validation_set = seq.get_validation_set()
test_set = seq.get_test_set()

# fit model
print('\nFitting model...')
history = net.fit(
    x=seq,
    epochs=1,
    verbose=True,
    validation_data=validation_set,
    use_multiprocessing=True
)

# # print classification examples
# x_test, y_test = test_set
# for i in range(100):
#     index = int(tf.random.uniform((1,)) * x_test.shape[0])
#     x = tf.reshape(x_test[index], (1, TIMESTEPS, INPUT_CHANNELS))
#     logits = tf.squeeze(net.predict(x))
#     print(tf.nn.sigmoid(logits))
#     # labels = tf.squeeze(y_test[index])
#     # print('Prediction: {}/{}'.format(y_hat, y))