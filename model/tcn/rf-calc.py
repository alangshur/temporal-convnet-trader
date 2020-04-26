import tensorflow as tf


def calculateReceptiveField(block_config):
    rf = 1

    for i in range(len(block_config)):
        kernel = block_config[i]['kernel_size']
        dilation = block_config[i]['dilation_rate']
        rf += dilation * (2 * kernel - 2)

    return rf

if __name__ == '__main__':
    
    # define network config
    block_config = [
        {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 1,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }, {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 2,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }, {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 4,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }, {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 8,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }, {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 16,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }, {
            'filter_count': 25,
            'kernel_size': 8,
            'dilation_rate': 32,
            'activation_func': tf.nn.elu,
            'res_activation_func': tf.nn.elu,
            'dropout_rate': 0.1
        }
    ]

    print('Receptive Field Size: ' + str(calculateReceptiveField(block_config)))
