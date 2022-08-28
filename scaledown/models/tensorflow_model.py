try:
    import tensorflow as tf
except ImportError as e:
    raise ImportError("Cannot import Tensorflow. Make sure that you have TensorFlow installed")

class TensorflowModel():
    def __init__(self, model):
        if self._is_tf_model(model):
            self.model=model
        else:
            self.model=tf.keras.models.load_model(model)

        self._type="tensorflow"

    def _is_tf_model(self, model):
        #TODO: Include keras.Model
        model_classes = (tf.keras.Model, tf.estimator.Estimator)
        return isinstance(model, model_classes)

    def get_model(self):
        return self.model

