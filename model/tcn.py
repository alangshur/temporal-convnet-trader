import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow.keras.layers as layers


class CausalConv1D(layers.Layer):
    def __init__(self, name,
                 filters=1,
                 kernel_size=3,
                 dilation_rate=1,
                 activation_func=tf.nn.relu,
                 dropout_rate=0.1,
                 **kwargs):

        # initialize abstract layer
        super(CausalConv1D, self).__init__(
            name=name,
            **kwargs
        )

        # weighted norm wrapper
        self.conv_wn_layer = tfa.layers.WeightNormalization(

            # causal convolution layer
            layers.Conv1D(
                filters,
                kernel_size,

                dilation_rate=dilation_rate,
                activation=activation_func,

                strides=1,  # required for causal conv
                padding='causal',  # requires causal padding
                data_format='channels_last',
                use_bias=True,

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

        # spatial dropout layer
        self.sdo_layer = layers.SpatialDropout1D(
            dropout_rate
        )

    def call(self, inputs, training=True):

        # execute pipeline
        a = self.conv_wn_layer(inputs)
        a = self.sdo_layer(a, training=training)
        return a


if __name__ == '__main__':
    causal_conv = CausalConv1D('conv',
                               filters=1,
                               kernel_size=3,
                               dilation_rate=1)

    x = tf.random.uniform((1, 6, 1))
    result = causal_conv(x, training=True)
    print(result)
