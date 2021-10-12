from .quantization import Quantization
import os
import pathlib

class WeightQuantization(Quantization):
    def __init__(self, level='float16'):
        if level not in ['float16', 'int8', 'hybrid']:
            raise ValueError(f"level value of {level} not supported. Please choose between int8 \
                    or float16 quantization")
        self.level=level
        self.quantized_model=None
        supported_frameworks=['tf']
        super().__init__(supported_frameworks)

    def _quantize_with_tf(self, model):
        try:
            import tensorflow as tf
        except ImportError as e:
            raise ImportError("You are trying to quantize a Tensorflow Model without Tensorflow Installed. \
                    Please Install TensorFlow using pip install tensorflow")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)

        if self.level in ['float16', 'hybrid']:
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
        elif self.level=='int8':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

        quantized_model=converter.convert()
        self.quantized_model=quantized_model
        return self.quantized_model

    def quantize(self, model):
        self._check_model_compatibility(model._type)
        if model._type in ['tf', 'tensorflow', 'keras']:
            return self._quantize_with_tf(model.get_model())
        else:
            raise ValueError("Model type does not support weight quantization")

    def get_model(self):
        return self.quantized_model

    def save_model(self, file_name='quant_model.tflite'):
        if not file_name.endswith('.tflite'):
            file_name+='.tflite'
        file_name= pathlib.Path(file_name)
        file_name.mkdir(exist_ok=True, parents=True)
        file_name.write_bytes(self.get_model())

