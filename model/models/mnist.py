from tcn.tcn1 import TemporalConvNet
from tensorflow.keras.datasets import mnist
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

# data parameters
input_channels = 1
timesteps = 28 * 28
num_classes = 10

# load data
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.astype(np.float32)
x_test = x_test.astype(np.float32)

# reshape data
x_train = tf.reshape(x_train, (x_train.shape[0], timesteps, input_channels))
x_test = tf.reshape(x_test, (x_test.shape[0], timesteps, input_channels))
y_train = tf.keras.utils.to_categorical(y_train, num_classes)
y_test = tf.keras.utils.to_categorical(y_test, num_classes)

# convert data to tensors
x_train = tf.convert_to_tensor(x_train)
x_test = tf.convert_to_tensor(x_test)
y_train = tf.convert_to_tensor(y_train)
y_test = tf.convert_to_tensor(y_test)

# block config
block_config = [
    {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 1,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }, {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 2,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }, {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 4,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }, {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 8,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }, {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 16,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }, {
        'filter_count': 24,
        'kernel_size': 8,
        'dilation_rate': 32,
        'activation_func': tf.nn.relu,
        'res_activation_func': tf.nn.relu,
        'dropout_rate': 0.15
    }
]

# build model
net = TemporalConvNet('temp-convnet', block_config, num_classes)
net.build((None, timesteps, input_channels))
net.summary()

# compile model
net.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

# fit model
history = net.fit(
    x_train, y_train,
    batch_size=64,
    epochs=5,
    validation_split=0.05,
    verbose=True
)

# print classification examples
for i in range(100):
    index = int(tf.random.uniform((1,)) * x_test.shape[0])
    x = tf.reshape(x_test[index], (1, timesteps, 1))
    y = int(tf.math.argmax(tf.squeeze(y_test[index])))
    logits = tf.squeeze(net.predict(x))
    y_hat = int(tf.math.argmax(tf.nn.softmax(logits)))
    print('Prediction: {}/{}'.format(y_hat, y))

# print training plot
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['training', 'validation'], loc='best')
plt.show()

# print test results
loss, accuracy = net.evaluate(x_test, y_test, verbose=True)
print(f'Test loss: {loss:.3}')
print(f'Test accuracy: {accuracy:.3}')
