import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow.keras.layers as layers
import time


class CausalConv1D(layers.Layer):
    def __init__(self, name, filter_count, kernel_size, dilation_rate,
                 activation_func=tf.nn.relu,
                 dropout_rate=0.2,
                 **kwargs):

        # initialize abstract layer
        super(CausalConv1D, self).__init__(
            name=name,
            **kwargs
        )

        # add weighted norm wrapper
        self.conv_wn_relu_layer = tfa.layers.WeightNormalization(

            # add causal convolution layer
            layers.Conv1D(
                filter_count, kernel_size,
                dilation_rate=dilation_rate,
                activation=activation_func,
                use_bias=True,

                strides=1,  # required for causal convolution
                padding='causal',  # required for causal convolution
                data_format='channels_last',  # required for spatial dropout

                kernel_initializer='glorot_uniform',
                bias_initializer='zeros',
                kernel_regularizer=None,
                bias_regularizer=None,
                activity_regularizer=None,
                kernel_constraint=None,
                bias_constraint=None
            ),

            data_init=True
        )

        # add spatial dropout layer
        self.sdo_layer = layers.SpatialDropout1D(
            dropout_rate
        )

    def call(self, inputs, training=True):

        # execute pipeline
        a = self.conv_wn_relu_layer(inputs, training=training)
        a = self.sdo_layer(a, training=training)
        return a


class ResidualBlock(layers.Layer):
    def __init__(self, name, filter_count, kernel_size, dilation_rate,
                 activation_func=tf.nn.relu,
                 res_activation_func=tf.nn.relu,
                 dropout_rate=0.2,
                 **kwargs):

        # initialize abstract layer
        self.filter_count = filter_count
        super(ResidualBlock, self).__init__(
            name=name,
            **kwargs
        )

        # add first convolution layerr
        self.conv_layer_1 = CausalConv1D(
            name + '/conv1', filter_count, kernel_size, dilation_rate,
            activation_func=activation_func,
            dropout_rate=dropout_rate
        )

        # add second convolution layerr
        self.conv_layer_2 = CausalConv1D(
            name + '/conv2', filter_count, kernel_size, dilation_rate,
            activation_func=activation_func,
            dropout_rate=dropout_rate
        )

        # add residual 1x1 convolution
        self.residual_conv = layers.Conv1D(
            filter_count, 1,
            activation=res_activation_func,
            use_bias=True,

            dilation_rate=1,  # superposed dilation
            strides=1,  # 1-for-1 mapped strides
            padding='valid',  # padding ignored
            data_format='channels_last',  # consistent data format

            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )

    def call(self, inputs, training=True):

        # execute pipeline
        act_1 = self.conv_layer_1(inputs, training=training)
        act_2 = self.conv_layer_2(act_1, training=training)
        res_act = self.residual_conv(inputs)
        block_act = tf.nn.relu(res_act + act_2)
        return block_act


class DenseClassifier(layers.Layer):
    def __init__(self, name, output_n, **kwargs):

        # initialize abstract layer
        super(DenseClassifier, self).__init__(
            name=name,
            **kwargs
        )

        # add flattening layer
        self.flatten_layer = layers.Flatten()

        # add dense output layer
        self.output_layer = layers.Dense(
            output_n,

            activation=None,
            use_bias=True,
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            kernel_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None
        )

    def call(self, inputs, training=True):

        # execute pipeline
        flat_inputs = self.flatten_layer(inputs)
        act = self.output_layer(flat_inputs)
        return act


class TemporalConvNet(tf.keras.Model):
    def __init__(self, name, block_config, output_n, **kwargs):

        # initialize abstract model
        build_start_ms = time.time() * 1000
        print(name + ': Building network... ', end='')
        super(TemporalConvNet, self).__init__(
            name=name,
            **kwargs
        )

        # add residual blocks
        self.blocks = []
        block_n = len(block_config)
        for i in range(block_n):

            # fetch block config
            filter_count = block_config[i]['filter_count']
            kernel_size = block_config[i]['kernel_size']
            dilation_rate = block_config[i]['dilation_rate']
            activation_func = block_config[i]['activation_func']
            res_activation_func = block_config[i]['res_activation_func']
            dropout_rate = block_config[i]['dropout_rate']

            # add next residual block
            self.blocks.append(ResidualBlock(
                'resblock-' + str(i), filter_count, kernel_size, dilation_rate,
                activation_func=activation_func,
                res_activation_func=res_activation_func,
                dropout_rate=dropout_rate
            ))

        # add dense output
        self.output_layer = DenseClassifier(
            'dense-out', output_n
        )

        # terminate initialization
        build_finish_ms = time.time() * 1000
        print('Took ' + str(build_finish_ms - build_start_ms) + 'ms')

    def call(self, inputs, training=True):

        # execute pipeline
        prev_act = inputs
        for block in self.blocks:
            prev_act = block(prev_act, training=training)
        y = self.output_layer(prev_act, training=training)
        return y
