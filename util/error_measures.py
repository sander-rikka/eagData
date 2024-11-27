"""Error measures for SAR and wave spectra characterization."""
# copy from here -> https://idosi.org/wasj/wasj(ITMIES)13/28.pdf

"""
- If forecast performance is evaluated for time series with the same scale and the data preprocessing
procedures were performed (data cleaning, anomaly detection), it is reasonable to choose MAE, MdAE,
RMSE. In case of different scales, these error measures are not applicable. The following recommendations 
are provided for mutli-scales cases. 

- In spite of the fact that percentage errors are commonly used in real world forecast tasks, but due to 
the non-symmetry, they are not recommended. If the range of the values lies in the positive half-plane 
and there are no outliers in the data, it is advisable to use symmetric error measures. 

- If the data are "dirty", i.e. contain outliers, it is advisable to apply the scaled measures such as 
MASE, inRSE. In this case (i) the horizon should be large enough, (ii) no identical values should be, 
(iii) the normalized factor should be not equal to zero. 

- If predicted data have seasonal or cyclical patterns, it is advisable to use the normalized error measures, 
wherein the normalization factors could be calculated within the interval equal to the cycle or season. 

- If there is no results of prior analysis and a-prior information about the quality of the data, it is 
reasonable to use the defined set of error measures. After calculating, the results are analyzed with respect 
to division by zero errors and contradiction cases: 
    - For the same time series the results for model m1 is better than m2, based on the one error measure, 
    but opposite for another one; 
    - For different time series the results for model m1 is better in most cases, but worst for a few of cases
    
"""

import numbers
import numpy as np


def _num_samples(x):
    """Return number of samples in array-like x."""
    message = "Expected sequence or array-like, got %s" % type(x)
    if hasattr(x, "fit") and callable(x.fit):
        # Don't get num_samples from an ensembles length!
        raise TypeError(message)

    if not hasattr(x, "__len__") and not hasattr(x, "shape"):
        if hasattr(x, "__array__"):
            x = np.asarray(x)
        else:
            raise TypeError(message)

    if hasattr(x, "shape") and x.shape is not None:
        if len(x.shape) == 0:
            raise TypeError(
                "Singleton array %r cannot be considered a valid collection." % x
            )
        # Check that shape is returning an integer or default to len
        # Dask dataframes may not return numeric shape[0] value
        if isinstance(x.shape[0], numbers.Integral):
            return x.shape[0]


def check_consistent_length(*arrays):
    """Check that all arrays have consistent first dimensions.

    Checks whether all objects in arrays have the same shape or length.

    Parameters
    ----------
    *arrays : list or tuple of input objects.
        Objects that will be checked for consistent length.
    """

    lengths = [_num_samples(X) for X in arrays if X is not None]
    uniques = np.unique(lengths)
    if len(uniques) > 1:
        raise ValueError(
            "Found input variables with inconsistent numbers of samples: %r"
            % [int(l) for l in lengths]
        )


def _check_reg_targets(y_true, y_pred):
    check_consistent_length(y_true, y_pred)

    if y_true.ndim == 1:
        y_true = y_true.reshape((-1, 1))

    if y_pred.ndim == 1:
        y_pred = y_pred.reshape((-1, 1))

    if y_true.shape[1] != y_pred.shape[1]:
        raise ValueError(
            "y_true and y_pred have different number of output ({0}!={1})".format(
                y_true.shape[1], y_pred.shape[1]
            )
        )

    n_outputs = y_true.shape[1]

    y_type = "continuous" if n_outputs == 1 else "continuous-multioutput"

    return y_type, y_true, y_pred


class AbsoluteForecastErrors:

    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Expects column or row vector."""
        self.y_type, self.y_true, self.y_pred = _check_reg_targets(y_true, y_pred)
        self.e_t = (y_true - y_pred)
        self.n = y_true.shape[0]

    def mean_error(self, axis):
        return np.mean(self.e_t, axis=axis)

    def mean_absolute_error(self, axis):
        return np.mean(np.abs(self.e_t), axis=axis)

    def median_absolute_error(self, axis):
        return np.median(np.abs(self.e_t), axis=axis)

    def mean_square_error(self, axis):
        return np.mean(self.e_t ** 2, axis=axis)

    def root_mean_square_error(self, axis):
        return np.sqrt(np.mean(self.e_t ** 2, axis=axis))

    def normalised_rmse(self, axis):
        return np.sqrt(np.mean(np.power(self.e_t, 2), axis=axis)) / (np.mean(np.abs(self.y_true)))


class PercentageErrors:

    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        self.y_type, self.y_true, self.y_pred = _check_reg_targets(y_true, y_pred)
        self.p_t = np.abs(y_true - y_pred) / y_true
        self.n = y_true.shape[0]

    def mean_absolute_percentage_error(self, axis):
        return np.mean(100 * np.abs(self.p_t), axis=axis)

    def median_absolute_percentage_error(self, axis):
        return np.median(100 * np.abs(self.p_t), axis=axis)

    def root_mean_square_percentage_error(self, axis):
        return np.sqrt(100 * np.mean(self.p_t ** 2, axis=axis))

    def root_median_square_percentage_error(self, axis):
        return np.sqrt(100 * np.median(self.p_t ** 2, axis=axis))


class SymmetricErrors:

    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        self.y_type, self.y_true, self.y_pred = _check_reg_targets(y_true, y_pred)
        self.s_t = np.abs(y_true - y_pred) / (y_true + y_pred)
        self.n = y_true.shape[0]

    def symmetric_mean_absolute_percentage_error(self, axis):
        return np.mean(200 * np.abs(self.s_t), axis=axis)

    def symmetric_median_absolute_percentage_error(self, axis):
        return np.median(200 * np.abs(self.s_t), axis=axis)


class ScaledErrors:
    def __init__(self, y_true: np.ndarray, y_pred: np.ndarray):
        self.y_type, self.y_true, self.y_pred = _check_reg_targets(y_true, y_pred)
        self.n = y_true.shape[0]
        values = []
        for i in range(1, self.n):
            values.append(np.abs(y_true[i] - y_pred[i]) / (abs(y_true[i] - y_true[i - 1]) / len(y_true) - 1))
        self.q_t = np.array(values)

    def mean_absolute_scaled_error(self, axis):
        return np.mean(np.abs(self.q_t), axis=axis)


if __name__ == '__main__':
    a = np.array([1, 2, 3, 4, 5, 6, 7])
    b = np.array([7, 6, 5, 4, 3, 2, 0])
    print(ScaledErrors(a, b).mean_absolute_scaled_error())
