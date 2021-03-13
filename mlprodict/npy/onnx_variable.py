"""
@file
@brief Intermediate class between :epkg:`numpy` and :epkg:`onnx`.

.. versionadded:: 0.6
"""
import numpy
from onnx.helper import make_tensor
from skl2onnx.common.data_types import guess_numpy_type
from skl2onnx.common._topology import Variable  # pylint: disable=E0611,E0001
from skl2onnx.algebra.onnx_ops import (  # pylint: disable=E0611
    OnnxAdd, OnnxAnd,
    OnnxCast, OnnxConstantOfShape,
    OnnxDiv,
    OnnxEqual,
    OnnxFlatten,
    OnnxGather, OnnxGreater,
    OnnxIdentity,
    OnnxLess,
    OnnxMatMul, OnnxMod, OnnxMul,
    OnnxNeg, OnnxNot,
    OnnxOr,
    OnnxPow,
    OnnxReduceSum, OnnxReshape,
    OnnxScatterElements, OnnxShape, OnnxSize, OnnxSlice,
    OnnxSqueeze, OnnxSub,
    OnnxTopK, OnnxTranspose
)
from ..tools.onnx2py_helper import guess_proto_dtype


try:
    numpy_bool = numpy.bool_
except AttributeError:  # pragma: no cover
    numpy_bool = bool
try:
    numpy_str = numpy.str
except AttributeError:  # pragma: no cover
    numpy_str = str


class OnnxVar:
    """
    Variables used into :epkg:`onnx` computation.

    :param inputs: variable name or object
    :param op: :epkg:`ONNX` operator
    :param select_output: if multiple output are returned by
        ONNX operator *op*, it takes only one specifed by this
        argument
    :param dtype: specifies the type of the variable
        held by this class (*op* is None) in that case
    :param kwargs: addition argument to give operator *op*

    .. versionadded:: 0.6
    """

    def __init__(self, *inputs, op=None, select_output=None,
                 dtype=None, **kwargs):
        self.inputs = inputs
        self.select_output = select_output
        self.onnx_op = op
        self.alg_ = None
        self.onnx_op_kwargs = kwargs
        if dtype is not None and (op is not None or len(inputs) != 1):
            raise RuntimeError(
                "dtype can only be used if op is None or len(inputs) == 1.")
        for i, inp in enumerate(self.inputs):
            if isinstance(inp, type):
                raise TypeError(
                    "Unexpected type for input %d - %r." % (i, inp))
        self.dtype = self._guess_dtype(dtype)

    def _guess_dtype(self, dtype):
        "Guesses dtype when not specified."
        if dtype is not None:
            return dtype
        dtypes = []
        for i, inp in enumerate(self.inputs):
            if isinstance(inp, str):
                return None
            if isinstance(inp, numpy.ndarray):
                dtypes.append(inp.dtype)
            elif isinstance(inp, Variable):
                dt = guess_numpy_type(inp.type)
                dtypes.append(dt)
            elif isinstance(inp, OnnxVar):
                dtypes.append(inp.dtype)
            elif isinstance(inp, (numpy.float32, numpy.float64, numpy.int32,
                                  numpy.int64)):
                dtypes.append(inp.dtype)
            elif isinstance(inp, numpy_str):
                dtypes.append(numpy_str)
            elif isinstance(inp, numpy_bool):
                dtypes.append(numpy_bool)
            elif isinstance(inp, int):
                dtypes.append(numpy.int64)
            elif isinstance(inp, float):
                dtypes.append(numpy.float64)
            else:
                raise TypeError(
                    "Unexpected type for input %i type=%r." % (i, type(inp)))
        dtypes = [_ for _ in dtypes if _ is not None]
        unique = set(dtypes)
        if len(unique) != 1:
            return None
        return dtypes[0]

    def __repr__(self):
        "usual"
        args = []
        for inp in self.inputs:
            args.append(repr(inp))
        if self.onnx_op is not None:
            if isinstance(self.onnx_op, str):
                args.append("op=%r" % self.onnx_op)
            else:
                args.append("op=%s" % self.onnx_op.__name__)
        if self.select_output is not None:
            args.append("select_output=%r" % self.select_output)
        if self.dtype is not None and self.dtype != self._guess_dtype(None):
            args.append("dtype=%r" % self.dtype)
        for k, v in sorted(self.onnx_op_kwargs.items()):
            args.append("%s=%r" % (k, v))
        res = "%s(%s)" % (self.__class__.__name__, ", ".join(args))
        return res

    def to_algebra(self, op_version=None):
        """
        Converts the variable into an operator.
        """
        if self.alg_ is None:
            if self.onnx_op is None:
                if len(self.inputs) != 1:
                    raise RuntimeError(  # pragma: no cover
                        "Unexpected number of inputs, 1 expected, "
                        "got {} instead.".format(self.inputs))
                self.alg_ = self.inputs[0]
            else:
                if isinstance(self.onnx_op, str):
                    var = self._custom_op(*self.inputs, op_version=op_version,
                                          **self.onnx_op_kwargs)
                    alg = var.to_algebra(op_version=op_version)
                    if not hasattr(self, 'alg_'):
                        raise RuntimeError(  # pragma: no cover
                            "Missing attribute 'alg_'.")
                    self.alg_ = alg
                    return alg

                new_inputs = []
                for inp in self.inputs:
                    if isinstance(inp, (
                            int, float, str, numpy.ndarray, numpy.int32,
                            numpy.int64, numpy.float32, numpy.float64,
                            numpy_bool, numpy_str, numpy.int8, numpy.uint8,
                            numpy.int16, numpy.uint16, numpy.uint32, numpy.uint64)):
                        new_inputs.append(inp)
                    else:
                        new_inputs.append(
                            inp.to_algebra(op_version=op_version))

                res = self.onnx_op(*new_inputs, op_version=op_version,
                                   **self.onnx_op_kwargs)
                if self.select_output is None:
                    self.alg_ = res
                else:
                    self.alg_ = res[self.select_output]
        return self.alg_

    def _custom_op(self, *args, op_version=None, runtime=None, **kwargs):
        """
        This could be handled before a call to this method
        but this method can change the conversion of an non-existing
        operator depending on the given opset.
        """
        if self.onnx_op == 'filter':
            return self._custom_op_filter(*args, op_version=op_version,
                                          runtime=runtime, **kwargs)
        raise NotImplementedError(  # pragma: no cover
            "Unexpected custom operator %r." % self.onnx_op)

    def _custom_op_filter(self, *args, op_version=None, runtime=None, **kwargs):
        """
        This could be handled before a call to this method
        but this method can change the conversion of an non-existing
        operator depending on the given opset.
        """
        if len(args) != 2:
            raise RuntimeError(  # pragma: no cover
                "Custom op 'filter' expects two inputs not %r." % len(args))
        if len(kwargs) != 0:
            raise RuntimeError(  # pragma: no cover
                "Custom op 'filter' expects no arguments but got %r." % kwargs)
        mat, index = args
        cast = OnnxVar(index.astype(numpy.int64), op=OnnxSqueeze)
        n1 = OnnxVar(cast, op=OnnxReduceSum, keepdims=1)
        indices = OnnxVar(cast, n1, op=OnnxTopK, select_output=1)
        return OnnxVar(mat, indices, op=OnnxGather)

    @property
    def T(self):
        "Transpose."
        return OnnxVar(self, op=OnnxTranspose)

    def astype(self, dtype):
        "Cast"
        return OnnxVar(self, op=OnnxCast, to=guess_proto_dtype(dtype))

    @property
    def shape(self):
        "Shape"
        return OnnxVar(self, op=OnnxShape)

    @property
    def size(self):
        "Size"
        return OnnxVar(self, op=OnnxSize)

    def reshape(self, shape):
        "Reshape"
        if isinstance(shape, (tuple, list)):
            shape = numpy.array(shape, dtype=numpy.int64)
        return OnnxVar(self, shape, op=OnnxReshape)

    def __add__(self, y):
        "Addition."
        return OnnxVar(self, y, op=OnnxAdd)

    def __sub__(self, y):
        "Subtraction."
        return OnnxVar(self, y, op=OnnxSub)

    def __mul__(self, y):
        "Multiplication."
        return OnnxVar(self, y, op=OnnxMul)

    def __pow__(self, y):
        "Power."
        return OnnxVar(self, y, op=OnnxPow)

    def __mod__(self, y):
        "Modulo."
        return OnnxVar(self, y, op=OnnxMod)

    def __matmul__(self, y):
        "Matrix multiplication."
        return OnnxVar(self, y, op=OnnxMatMul)

    def __truediv__(self, y):
        "Division, no difference between `/` and `//`."
        return OnnxVar(self, y, op=OnnxDiv)

    def __floordiv__(self, y):
        "Division, no difference between `/` and `//`."
        return OnnxVar(self, y, op=OnnxDiv)

    def __eq__(self, y):
        "Equality."
        return OnnxVar(self, y, op=OnnxEqual)

    def __ne__(self, y):
        "Difference."
        return OnnxVar(OnnxVar(self, y, op=OnnxEqual), op=OnnxNot)

    def __gt__(self, y):
        "Greater."
        return OnnxVar(self, y, op=OnnxGreater)

    def __lt__(self, y):
        "Less."
        return OnnxVar(self, y, op=OnnxLess)

    def __and__(self, y):
        "And."
        return OnnxVar(self, y, op=OnnxAnd)

    def __or__(self, y):
        "And."
        return OnnxVar(self, y, op=OnnxOr)

    def not_(self):
        "Not."
        return OnnxVar(self, op=OnnxNot)

    def __neg__(self):
        "Neg."
        return OnnxVar(self, op=OnnxNeg)

    def __getitem__(self, index):
        """
        Deals with multiple scenarios.
        * *index* is an integer or a slice, a tuple of integers and slices,
          example: `[0, 1]`, `[:5, :6]`, `[::2]` (**scenario 1**)
        * *index* is an *ONNX* object (more precisely an instance of
          @see cl OnnxVar), then the method assumes it is an array of
          boolean to select a subset of the tensor along the first axis,
          example: `mat[mat == 0]` (**scenario 2**)
        """
        if isinstance(index, OnnxVar):
            # scenario 2
            return OnnxVar(self, index, op='filter')

        if not isinstance(index, tuple):
            index = (index, )

        # scenario 1
        starts = []
        ends = []
        axes = []
        steps = []
        axis_squeeze = []
        for i, ind in enumerate(index):
            if isinstance(ind, int):
                starts.append(ind)
                ends.append(ind + 1)
                axes.append(i)
                steps.append(1)
                axis_squeeze.append(i)
                continue
            if isinstance(ind, slice):
                if ind.start is None and ind.stop is None and ind.step is None:
                    continue
                start = 0 if ind.start is None else ind.start
                end = -1 if ind.stop is None else ind.stop
                step = 1 if ind.step is None else ind.step
                starts.append(start)
                ends.append(end)
                axes.append(i)
                steps.append(step)
                continue
            raise NotImplementedError(  # pragma: no cover
                "Not implemented for type %r." % type(ind))
        if max(steps) == min(steps) == 1:
            steps = None
        else:
            steps = numpy.array(steps, dtype=numpy.int64)
        starts = numpy.array(starts, dtype=numpy.int64)
        ends = numpy.array(ends, dtype=numpy.int64)
        axes = numpy.array(axes, dtype=numpy.int64)
        if steps is None:
            sliced = OnnxVar(self, starts, ends, axes, op=OnnxSlice)
        else:
            sliced = OnnxVar(self, starts, ends, axes, steps, op=OnnxSlice)
        if len(axis_squeeze) > 0:
            return OnnxVar(
                sliced, numpy.array(axis_squeeze, dtype=numpy.int64),
                op=OnnxSqueeze)
        return sliced

    def __setitem__(self, index, value):
        """
        Only supports vectors (1D tensor).
        * *index* is an integer or a slice, a tuple of integers and slices,
          example: `[0]`, `[:5]`, `[::2]` (**scenario 1**)
        * *index* is an *ONNX* object (more precisely an instance of
          @see cl OnnxVar), then the method assumes it is an array of
          boolean to select a subset of the tensor along the first axis,
          example: `mat[mat == 0]` (**scenario 2**)
        This processing is applied before the operator it contains.
        A copy should be made (Identity node or copy method).
        """
        if self.onnx_op is not None and self.onnx_op is not OnnxIdentity:
            raise RuntimeError(
                "A copy should be made before setting new values on a matrix. "
                "Method copy() would do that.")

        if isinstance(index, OnnxVar):
            # scenario 2
            raise NotImplementedError()  # pragma: no cover

        if not isinstance(index, tuple):
            index = (index, )

        # scenario 1
        if len(index) == 1:
            return self._setitem1i_(index[0], value)
        raise NotImplementedError(
            "Indices in %d dimensions are not implemented yet." % len(index))

    def _setitem1i_(self, index, value):
        sl = None
        if isinstance(index, slice):
            start = 0 if index.start is None else index.start
            stop = index.stop
            step = index.step
            sl = [start, stop, step]
        elif isinstance(index, int):
            sl = [index, index + 1, 1]
        else:
            raise NotImplementedError(  # pragma: no cover
                "Unable to assign new values due to unexpected type %r."
                "" % type(index))

        if sl[1] is None and isinstance(value, numpy.ndarray):
            sl[1] = sl[0] + value.size
        if sl[1] is None:
            if sl[2] is not None and sl[2] != 1:
                raise NotImplementedError(
                    "If the length is not known, step must be 1 not %d." % sl[2])
            value = make_tensor(
                "value", guess_proto_dtype(value.dtype), (1, ), [value])  # pylint: disable=E1101
            inp = self.inputs[0]
            if not isinstance(inp, OnnxVar):
                raise RuntimeError(
                    "Input must be an instance of OnnxVar not %r." % type(inp))
            cst = OnnxVar(inp.shape, op=OnnxConstantOfShape, value=value)
            ext = inp[:sl[0]]
            indices = numpy.arange(0, sl[0]).astype(numpy.int64)
            add_step = OnnxVar(cst, indices, ext,
                               op=OnnxScatterElements, axis=0)
        else:
            indices = numpy.arange(sl[0], sl[1], sl[2]).astype(numpy.int64)
            if isinstance(value, numpy.ndarray):
                values = value
            else:
                values = numpy.full(indices.shape, value)
            add_step = OnnxVar(self.inputs[0], indices, values,
                               op=OnnxScatterElements, axis=0)

        self.inputs = [add_step]
        return self

    def copy(self):
        """
        Returns a copy of self (use of Identity node).
        """
        return OnnxVar(self, op=OnnxIdentity)

    def flatten(self, axis=0):
        """
        Flattens a matrix (see :epkg:`numpy:ndarray:flatten`).

        :param axis: only flatten from axis to the end.
        :return: @see cl OnnxVariable
        """
        fl = OnnxVar(self, op=OnnxFlatten, axis=axis)
        if axis == 0:
            return OnnxVar(fl, numpy.array([0], dtype=numpy.int64),
                           op=OnnxSqueeze)
        return fl
