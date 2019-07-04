"""
@file
@brief Validates runtime for many :scikit-learn: operators.
The submodule relies on :epkg:`onnxconverter_common`,
:epkg:`sklearn-onnx`.
"""
import numpy
import pandas


def measure_absolute_difference(skl_pred, ort_pred):
    """
    Measures the differences between predictions
    between two ways of computing them.
    The functions returns nan if shapes are different.

    @param      skl_pred        prediction from :epkg:`scikit-learn`
                                or any other way
    @param      skl_ort         prediction from an :epkg:`ONNX` runtime
                                or any other way
    @return                     absolute max difference
                                or nan if it does not make any sense
    """
    if isinstance(skl_pred, tuple):
        diffs = []
        for i in range(len(skl_pred)):  # pylint: disable=C0200
            try:
                diff = measure_absolute_difference(
                    skl_pred[i], [_[i] for _ in ort_pred])
            except IndexError:
                return 1e9
            except RuntimeError as e:
                raise RuntimeError("Unable to compute differences between"
                                   "\n{}--------\n{}".format(
                                       skl_pred, ort_pred)) from e
            diffs.append(diff)
        return max(diffs)
    else:
        ort_pred_ = ort_pred
        if isinstance(ort_pred, list):
            if isinstance(ort_pred[0], dict):
                ort_pred = pandas.DataFrame(ort_pred).values
            elif (isinstance(ort_pred[0], list) and
                    isinstance(ort_pred[0][0], dict)):
                if len(ort_pred) == 1:
                    ort_pred = pandas.DataFrame(ort_pred[0]).values
                elif len(ort_pred[0]) == 1:
                    ort_pred = pandas.DataFrame(
                        [o[0] for o in ort_pred]).values
                else:
                    raise RuntimeError("Unable to compute differences between"
                                       "\n{}--------\n{}".format(
                                           skl_pred, ort_pred))
            else:
                ort_pred = numpy.array(ort_pred)

        if hasattr(skl_pred, 'todense'):
            skl_pred = skl_pred.todense()
        if hasattr(ort_pred, 'todense'):
            ort_pred = ort_pred.todense()

        if isinstance(ort_pred, list):
            raise RuntimeError("Issue with {}\n{}".format(ort_pred, ort_pred_))

        if skl_pred.shape != ort_pred.shape and skl_pred.size == ort_pred.size:
            ort_pred = ort_pred.ravel()
            skl_pred = skl_pred.ravel()

        if skl_pred.shape != ort_pred.shape:
            return 1e9

        diff = numpy.max(numpy.abs(skl_pred.ravel() - ort_pred.ravel()))

        if numpy.isnan(diff):
            raise RuntimeError("Unable to compute differences between {}-{}\n{}\n"
                               "--------\n{}".format(
                                   skl_pred.shape, ort_pred.shape,
                                   skl_pred, ort_pred))
        return diff
