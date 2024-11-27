"""Holds functions to calculate relevant statistics for spectra and calculated params"""
import numpy as np
import pandas as pd

from wave_parameters import WaveParameters as Wp
from util.error_measures import AbsoluteForecastErrors as AFE
from util.error_measures import PercentageErrors as PE
from util.error_measures import ScaledErrors as SclE
from util.error_measures import SymmetricErrors as SymE


def calculate_wave_params(array, frequency):
    """
    Calculates predefined bulk wave parameters
    :param array: input spectrum / spectra. 1D spectra only, either one or many in one array
    :param frequency: frequency axis values
    :return: bulk wave parameters in numpy array.
    """
    params = np.vstack([Wp(np.array(array), frequency).tp(),
                        Wp(np.array(array), frequency).hs(),
                        Wp(np.array(array), frequency).tm01(),
                        Wp(np.array(array), frequency).tm_10(),
                        Wp(np.array(array), frequency).tm02(),
                        Wp(np.array(array), frequency).fm(),
                        Wp(np.array(array), frequency).wm()
                        ])
    return params.T


def data_descriptor(true_array: np.ndarray, pred_array: np.ndarray,
                    axis,
                    spectra_errors=False,
                    percentage_errors=False,
                    symmetric_errors=False,
                    scaled_errors=False) -> tuple[np.ndarray, list]:
    """
    Calculates statistical values between spectra or bulk wave parameters
    :param true_array:
    :param pred_array:
    :param axis:
    :param spectra_errors:
    :param percentage_errors:
    :param symmetric_errors:
    :param scaled_errors:
    :return:
    """

    try:
        assert true_array.shape == pred_array.shape
    except AssertionError:
        exit(f'True and prediction arrays have different shapes: {true_array.shape} vs {pred_array.shape}')

    if len(true_array.shape) == 1:
        true_array = true_array.reshape((1, true_array.shape[0]))
        pred_array = pred_array.reshape((1, pred_array.shape[0]))
        #rows, cols = true_array.shape
    #elif len(true_array.shape) == 2:  # kas see vajalik?
    rows, cols = true_array.shape

    # default errors
    rho_numbers = []
    for i in range(0, rows):
        rho_numbers.append(np.corrcoef(true_array[i, :], pred_array[i, :])[0, 1])
    rho = np.array(rho_numbers)
    me = AFE(true_array, pred_array).mean_error(axis=axis)
    mae = AFE(true_array, pred_array).mean_absolute_error(axis=axis)
    mse = AFE(true_array, pred_array).mean_square_error(axis=axis)
    rmse = AFE(true_array, pred_array).root_mean_square_error(axis=axis)
    nrmse = AFE(true_array, pred_array).normalised_rmse(axis=axis)
    goodness_numbers = np.stack([rho, me, mae, mse, rmse, nrmse], axis=1)
    columns = ['rho', 'me', 'mae', 'mse', 'rmse', 'nrmse']

    if spectra_errors:

        delta_max_val = np.max(true_array, axis=1) - np.max(pred_array, axis=1)
        delta_max_loc = true_array.argmax(axis=1) - pred_array.argmax(axis=1)
        goodness_numbers = np.hstack([goodness_numbers, delta_max_val.reshape(rows, 1),
                                      delta_max_loc.reshape(rows, 1)])
        columns.append('delta_max_loc')
        columns.append('delta_max_val')

    if percentage_errors:
        mape = PE(true_array, pred_array).mean_absolute_percentage_error(axis=1)
        rmspe = PE(true_array, pred_array).root_mean_square_percentage_error(axis=1)
        goodness_numbers = np.hstack([goodness_numbers, mape.reshape(rows, 1), rmspe.reshape(rows, 1)])
        columns.append('mape')
        columns.append('rmspe')

    if symmetric_errors:
        smape = SymE(true_array, pred_array).symmetric_mean_absolute_percentage_error(axis=1)
        goodness_numbers = np.hstack([goodness_numbers, smape.reshape(rows, 1)])
        columns.append('smape')

    if scaled_errors:
        mase = SclE(true_array, pred_array).mean_absolute_scaled_error(axis=1)
        # add 0 at the beginning since mase is 1 element shorter.
        mase = np.insert(mase, 0, values=0)
        goodness_numbers = np.hstack([goodness_numbers, mase.reshape(rows, 1)])
        columns.append('mase')

    return goodness_numbers, columns


def wave_param_descriptor(true_params: np.ndarray, pred_params: np.ndarray) -> pd.DataFrame:
    """
    Wrapper for bulk wave parameter descriptor
    :param true_params: true bulk parameters
    :param pred_params: predicted bulk parameters
    :param freq: frequency axis of spectra
    :return: dataframe of descriptive statistics for bulk wave parameters
    """

    rows, cols = true_params.shape
    param_stats = []
    for i in range(cols):
        i_stats, col_names = data_descriptor(true_params[:, i], pred_params[:, i], axis=1)
        param_stats.append(i_stats)

    df = pd.DataFrame(np.array(param_stats).reshape(cols, len(col_names)).T, index=col_names,
                      columns=['tp', 'hs', 'tm01', 'tm_10', 'tm02', 'fm', 'wm'])
    return df


def spectra_descriptor(true_array: np.ndarray, pred_array: np.ndarray, freq: np.ndarray) -> \
        tuple[pd.DataFrame, pd.DataFrame]:
    """
    Wrapper for spectra descriptor
    :param true_array: true spectra
    :param pred_array: predicted spectra
    :param freq: frequency axis
    :return: dataframes of descriptive statistics: 1. per spectra statistics, 2. per frequency statistics
    """
    rows, cols = true_array.shape
    per_spec_stats, col_names = data_descriptor(true_array, pred_array, axis=1,
                                                spectra_errors=True,
                                                percentage_errors=True,
                                                symmetric_errors=True)
    df_spectra_stats = pd.DataFrame(per_spec_stats, columns=col_names)

    frequency_stats = []
    for i in range(cols):
        i_stats, col_names = data_descriptor(true_array[:, i], pred_array[:, i], axis=1,
                                             percentage_errors=True,
                                             symmetric_errors=True)
        frequency_stats.append(i_stats)

    df_freq_stats = pd.DataFrame(np.array(frequency_stats).reshape(cols, len(col_names)).T,
                                 index=col_names, columns=[str(x) for x in freq])
    return df_spectra_stats, df_freq_stats


if __name__ == '__main__':
    # for testing and developing
    arr = np.random.random(size=(55, 30))
    brr = np.random.random(size=(55, 30))
    test, col_names = data_descriptor(arr[:, 0], brr[:, 0], axis=1, percentage_errors=True, symmetric_errors=True)

    freq = np.arange(0.08, 0.38, 0.01)
    df1 = wave_param_descriptor(arr, brr, freq)
    df2, df3 = spectra_descriptor(arr, brr, freq)

    test2, col_names2 = data_descriptor(arr, brr, axis=1, percentage_errors=True, symmetric_errors=True)

    mse = SclE(arr, brr).mean_absolute_scaled_error(axis=1)
