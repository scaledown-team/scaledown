
def load_model(model, model_type):
    if model_type=='tensorflow' or model_type=='keras':
        from scaledown.models import TensorflowModel
        model=TensorflowModel(model)
    elif model_type=='pytorch':
        model=PytorchModel(model)
    else:
        raise ValueError("Unsupported Model Type. Please specify 'tensorflow', 'keras' or 'pytorch' as model_type")
    return model
