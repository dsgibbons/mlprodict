"""
@file
@brief :epkg:`numpy` functions implemented with :epkg:`onnx`
and compiled with this python runtime.

.. versionadded:: 0.6
"""
from .onnx_numpy_annotation import (
    NDArraySameType,
    NDArraySameTypeSameShape)
from .numpy_onnx_impl import (
    abs as nx_abs,
    acos as nx_acos,
    acosh as nx_acosh,
    amin as nx_min,
    amax as nx_max,
    argmax as nx_argmax,
    argmin as nx_argmin,
    asin as nx_asin,
    asinh as nx_asinh,
    atan as nx_atan,
    atanh as nx_atanh,
    ceil as nx_ceil,
    cos as nx_cos,
    cosh as nx_cosh,
    erf as nx_erf,
    exp as nx_exp,
    isnan as nx_isnan,
    log as nx_log,
    mean as nx_mean,
    prod as nx_prod,
    reciprocal as nx_reciprocal,
    relu as nx_relu,
    round as nx_round,
    sign as nx_sign,
    sin as nx_sin,
    sinh as nx_sinh,
    sqrt as nx_sqrt,
    sum as nx_sum,
    tan as nx_tan,
    tanh as nx_tanh,
)
from .onnx_numpy_wrapper import onnxnumpy_np


@onnxnumpy_np(signature=NDArraySameTypeSameShape("all"))
def abs(x):
    "abs"
    return nx_abs(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def acos(x):
    "acos"
    return nx_acos(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def acosh(x):
    "acosh"
    return nx_acosh(x)


@onnxnumpy_np(signature=NDArraySameType("all"))
def amax(x, axis=None, keepdims=0):
    "amax"
    return nx_max(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameType("all"))
def amin(x, axis=None, keepdims=0):
    "amin"
    return nx_min(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameType("all_int"))
def argmax(x, axis=None, keepdims=0):
    "argmax"
    return nx_argmax(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameType("all_int"))
def argmin(x, axis=None, keepdims=0):
    "argmin"
    return nx_argmin(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def asin(x):
    "asin"
    return nx_asin(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def asinh(x):
    "asinh"
    return nx_asinh(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def atan(x):
    "atan"
    return nx_atan(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def atanh(x):
    "atanh"
    return nx_atanh(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def ceil(x):
    "ceil"
    return nx_ceil(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def cos(x):
    "cos"
    return nx_cos(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def cosh(x):
    "cosh"
    return nx_cosh(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def erf(x):
    "erf"
    return nx_erf(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def exp(x):
    "exp"
    return nx_exp(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("all_bool"))
def isnan(x):
    "isnan"
    return nx_isnan(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def log(x):
    "log"
    return nx_log(x)


@onnxnumpy_np(signature=NDArraySameType("all"))
def prod(x, axis=None, keepdims=0):
    "prod"
    return nx_prod(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameType("all"))
def mean(x, axis=None, keepdims=0):
    "mean"
    return nx_mean(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def reciprocal(x):
    "reciprocal"
    return nx_reciprocal(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def relu(x):
    "relu"
    return nx_relu(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def round(x):
    "round"
    return nx_round(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def sign(x):
    "sign"
    return nx_sign(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def sin(x):
    "sin"
    return nx_sin(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def sinh(x):
    "sinh"
    return nx_sinh(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def sqrt(x):
    "sqrt"
    return nx_sqrt(x)


@onnxnumpy_np(signature=NDArraySameType("all"))
def sum(x, axis=None, keepdims=0):
    "sum"
    return nx_sum(x, axis=axis, keepdims=keepdims)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def tan(x):
    "tan"
    return nx_tan(x)


@onnxnumpy_np(signature=NDArraySameTypeSameShape("floats"))
def tanh(x):
    "tanh"
    return nx_tanh(x)
