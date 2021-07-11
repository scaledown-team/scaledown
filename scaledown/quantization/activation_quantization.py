from quantization import Quantization
import numpy as np

class ActivationQuantization(Quantization):
    def __init__(self, level='int8', dataset=None):
        supported_levels=['int8', 'hybrid']
        supported_frameworks=['tf', 'keras']
        if level not in supported_levels:
            raise ValueError(f"level value of {level} not supported. Please choose between \
                    {' or '.join(supported_levels)} quantization")
        self.level=level
        self.quantized_model=None
        self.dataset=dataset
        super().__init__(supported_frameworks)

    def _quantize_with_tf(self, model):
        try:
            import tensorflow as tf
        except ImportError as e:
            raise ImportError("You are trying to quantize a Tensorflow Model without Tensorflow Installed. \
                    Please Install TensorFlow using pip install tensorflow")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)

        if self.type=='hybrid':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.representative_dataset = representative_dataset
        elif self.level=='int8':
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8

        quantized_model=converter.convert()
        self.quantized_model=quantized_model
        return self.quantized_model

    def get_representive_dataset(self):
        if not self.dataset:
            raise ValueError("You need a sample dataset to improve quantization results.")
        
        def representative_dataset():
            for i, data in enumerate(self.dataset):
                if i<150:
                    yield [data.astype(np.float32)]

        return representative_dataset

    def quantize(self, model):
        self._check_model_compatibility(model.type)
        if model.type in ['tf', 'keras']:
            return self._quantize_with_tf(model)
