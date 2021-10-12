import subprocess

class ConvertToOnnx():
    def __init__(self, model_name=False):
        self.supported_models=['tf', 'pytorch']
        self.model_name=model_name

    def _convert_tf_model(self, model, opset):
        if not model.file:
            model.save('tf-model-intermediate')

        subprocess.run("python -m tf2onnx.convert --saved-model tensorflow-model-path --opset 14 --output model.onnx")


    def _convert_pytorch_model(self, model):
        input_shape=list(model.parameters())[0].shape

    def convert(self, model, opset=14):
        try:
            import onnx
        except ImportError:
            raise ImportError(f"You need to install ONNX and ONNX_TF to convert a model to \
                    TensorFlow/Keras format")

        if not model.type in self.supported_models:
            raise ValueError("Model type does not support conversion to ONNX")

        if model.type=='tf':
            return self._convert_tf_model(model, opset)
