# -*- encoding: utf-8 -*-
# pylint: disable=E0203,E1101,C0111
"""
@file
@brief Runtime operator.
"""
import numpy
from ._op import OpRunUnary, RuntimeTypeError


class Scaler(OpRunUnary):

    atts = {'offset': None, 'scale': None}

    def __init__(self, onnx_node, desc=None, **options):
        OpRunUnary.__init__(self, onnx_node, desc=desc,
                            expected_attributes=Scaler.atts,
                            **options)

    def _run(self, x):  # pylint: disable=W0221
        if (x.dtype in (numpy.float32, numpy.float64) and
                x.dtype != self.scale.dtype):
            raise RuntimeTypeError(
                "Input type mismatch: {} != {} (operator '{}')".format(
                    x.dtype, self.scale.dtype, self.__class__.__name__))
        return self._run_no_checks_(x)

    def _run_no_checks_(self, x):  # pylint: disable=W0221
        if self.inplaces.get(0, False):
            return self._run_inplace(x)
        return ((x - self.offset) * self.scale, )

    def _run_inplace(self, x):
        x -= self.offset
        x *= self.scale
        return (x, )

    def _infer_shapes(self, x):  # pylint: disable=W0221
        """
        Returns the same shape by default.
        """
        return (x, )
