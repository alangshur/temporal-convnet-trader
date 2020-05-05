import tensorflow as tf
from tensorflow.keras import losses


class MulticlassBinaryCrossEntropy(losses.Loss):
    def __init__(self, name='weighted_binary_crossentropy', **kwargs):
        '''Initialize multi-class cross-entropy loss.'''

        super(MulticlassBinaryCrossEntropy, self).__init__(name=name, **kwargs)

    def call(self, y_true, y_pred):
        '''Calculate loss from network logits and labels.'''

        return losses.binary_crossentropy(
            y_true, 
            y_pred, 
            from_logits=False
        )