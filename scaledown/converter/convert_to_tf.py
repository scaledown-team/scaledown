from .convert_to_onnx import ConvertToOnnx

class ConvertToTF():
    def __init__(self, onnx_model_name=False, tf_model_name=False):
        self.model_type=model.type
        self.supported_models=['pytorch']
        self.converted_model=None

    def _convert_pytorch_model(self, model):
        onnx_converter=ConvertToOnnx(model_name=self.onnx_model_name)
        onnx_model=onnx_converter.convert(model)
        tf_model=prepare(onnx_model)
        self.converted_model=tf_model
        self._save_models(tf_model)
        return self.converted_model

    def convert(model):
        try:
            from onnx_tf.backend import prepare
        except ImportError:
            raise ImportError(f"You need to install ONNX and ONNX_TF to convert a model to TensorFlow/Keras format")

        if model.type=='pytorch':
            return self._convert_pytorch_model(model)
        else:
            raise ValueError("Model type does not support conversion \
                    to Tensorflow/Keras")

    def get_model(self):
        return self.converted_model

