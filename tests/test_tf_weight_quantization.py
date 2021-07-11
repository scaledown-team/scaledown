import scaledown as sd
from scaledown import quantization
import pytest

import tensorflow as tf

def test_tf_fcnn_saved_model_int8():
    model=tf.keras.models.load_model('tests/saved_models/tf_fcnn')
    sd_model=sd.load_model(model, model_type='tensorflow')
    try:
        print(dir(sd))
        quantizer=quantization.WeightQuantization(level='int8')
        quantized_model=quantizer.quantize(sd_model)
    except Exception as e:
        assert False, f"Could not quantize model. Error: {e}"

def test_tf_fcnn_saved_model_float16():
    model=tf.keras.models.load_model('tests/saved_models/tf_fcnn')
    sd_model=sd.load_model(model, model_type='tensorflow')
    try:
        print(dir(sd))
        quantizer=quantization.WeightQuantization(level='float16')
        quantized_model=quantizer.quantize(sd_model)
    except Exception as e:
        assert False, f"Could not quantize model. Error: {e}"

