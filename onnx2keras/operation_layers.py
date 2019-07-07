import keras.layers
import keras.backend as K
import logging
from .utils import ensure_tf_type, ensure_numpy_type
from collections.abc import Iterable


def convert_clip(node, params, layers, node_name):
    """
    Convert clip layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    logger = logging.getLogger('onnx2keras:clip')
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for clip layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    if params['min'] == 0:
        logger.debug("Using ReLU({0}) instead of clip".format(params['max']))
        layer = keras.layers.ReLU(max_value=params['max'], name=node_name)
    else:
        def target_layer(x, vmin=params['min'], vmax=params['max']):
            import tensorflow as tf
            return tf.clip_by_value(x, vmin, vmax)
        layer = keras.layers.Lambda(target_layer, name=node_name)

    layers[node_name] = layer(input_0)


def convert_log(node, params, layers, node_name):
    """
    Convert Log layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for log layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    def target_layer(x):
        import keras.backend as K
        return K.log(x)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)


def convert_exp(node, params, layers, node_name):
    """
    Convert Exp layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for log layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    def target_layer(x):
        import keras.backend as K
        return K.exp(x)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)


def convert_reduce_sum(node, params, layers, node_name):
    """
    Convert reduce sum.
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for reduce sum layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    axis = params['axes']

    def target_layer(x, axis=axis):
        import keras.backend as K
        return K.sum(x, keepdims=True, axis=axis)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)
    layers[node_name].set_shape(layers[node_name]._keras_shape)


def convert_reduce_mean(node, params, layers, node_name):
    """
    Convert reduce mean.
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for reduce mean layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    def target_layer(x, axis=params['axes'], keepdims=params['keepdims']):
        import keras.backend as K
        return K.mean(x, keepdims=(keepdims == 1), axis=axis)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)
    layers[node_name].set_shape(layers[node_name]._keras_shape)


def convert_pow(node, params, layers, node_name):
    """
    Convert Pow layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 2:
        assert AttributeError('More than 2 inputs for pow layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])
    power = ensure_numpy_type(layers[node.input[1]])

    def target_layer(x, a=power):
        import keras.backend as K
        return K.pow(x, a)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)


def convert_sqrt(node, params, layers, node_name):
    """
    Convert Sqrt layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for sqrt layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])

    def target_layer(x):
        import keras.backend as K
        return K.sqrt(x)

    lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
    layers[node_name] = lambda_layer(input_0)


def convert_split(node, params, layers, node_name):
    """
    Convert Split layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 1:
        assert AttributeError('More than 1 input for split layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])
    splits = params["split"]
    axis = params.get("axis", 0)
    if not isinstance(splits, Iterable):
        # This might not work if `split` is a tensor.
        chunk_size = K.int_size(input_0)[axis] // splits
        splits = (chunk_size,) * splits

    cur = 0
    for i, split in enumerate(splits):
        node_name = params['_outputs'][i]

        def target_layer(x, axis=axis, start_i=cur, end_i=cur+split):
            slices = [slice(None, None)] * len(K.int_shape(x))
            slices[axis] = slice(start_i, end_i)
            return x[tuple(slices)]

        lambda_layer = keras.layers.Lambda(target_layer, name=node_name)
        layers[node_name] = lambda_layer(input_0)
        cur += split


def convert_max(node, params, layers, node_name):
    """
    Convert Max layer
    :param node: current operation node
    :param params: operation attributes
    :param layers: available keras layers
    :param node_name: resulting layer name
    :return: None
    """
    if len(node.input) != 2:
        assert AttributeError('More than 2 inputs for pow layer.')

    input_0 = ensure_tf_type(layers[node.input[0]])
    input_1 = ensure_tf_type(layers[node.input[1]])

    layers[node_name] = keras.layers.Maximum(name=node_name)([input_0, input_1])
