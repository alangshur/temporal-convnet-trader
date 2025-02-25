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
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 1,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}, {
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 2,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}, {
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 4,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}, {
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 8,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}, {
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 16,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}, {
    'filter_count': 16,
    'kernel_size': 10,
    'dilation_rate': 32,
    'activation_func': tf.nn.relu,
    'res_activation_func': tf.nn.relu,
    'dropout_rate': 0.25
}]


# print(calculateReceptiveField(config))