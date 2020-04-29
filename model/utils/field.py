import tensorflow as tf


def calculateReceptiveField(block_config):
    rf = 1

    # build rfield by block
    for i in range(len(block_config)):
        kernel = block_config[i]['kernel_size']
        dilation = block_config[i]['dilation_rate']
        rf += dilation * (2 * kernel - 2)

    return rf


config = [{
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 3,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}, {
    'filter_count': 128,
    'kernel_size': 15,
    'dilation_rate': 3,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.1
}]

print(calculateReceptiveField(config))