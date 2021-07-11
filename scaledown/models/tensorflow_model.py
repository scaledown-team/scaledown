try:
    import tensorflow as tf
except ImportError as e:
    raise ImportError("Cannot import Tensorflow. Make sure that you have TensorFlow installed")

class TensorflowModel():
    def __init__(self, model):
        self.model=model
        self._type="tensorflow"

    def get_model(self):
        return self.model

