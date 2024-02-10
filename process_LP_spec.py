import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy.ma as ma
import numpy as np
import os
import pathlib
from scipy import io

import pandas as pd
import re
import datetime as dt

bphiiupaths = [r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\Web\web.txt",
               r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_04",
               r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_05",
               r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_06",
               r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_07"]


def mat2df(paths):
    df_param = pd.DataFrame()
    df_spec = pd.DataFrame()

    for path in paths:

        if path.endswith('.txt'):
            webdf = pd.read_csv(paths[0], header=None, sep=' ')
            meastime = pd.to_datetime(webdf[0]+' ' +webdf[1])

        else:
            data = []  # parameters data

            matfile = os.path.join(path,'spec.mat')
            mat = io.loadmat(matfile)

            for param in mat['lp_param'].dtype.names:
                if param not in ['f']:
                    arr = mat['lp_param'][0][param][0].T
                    data.append(arr)
                else:
                    freq = mat['lp_param'][0][param][0].T

            data = np.array(data).T.reshape(np.array(data).shape[1], np.array(data).shape[0])
            df_param = pd.concat([df_param, pd.DataFrame(data)], axis=0)

            specarr = mat['lp_specs'][:].T
            # specdata.append(specarr)

            # specdata = np.array(specdata).T.reshape(np.array(specdata).shape[1], np.array(specdata).shape[0])
            df_spec = pd.concat([df_spec, pd.DataFrame(specarr)], axis=0)
            # print(df_spec.shape)

    df_param.columns = mat['lp_param'].dtype.names[:-1]
    df_param.set_index(meastime, inplace=True, drop=True)
    df_param.index.name = 'Datetime'

    df_spec.columns = [str(z) for z in freq[0]]
    df_spec.set_index(meastime, inplace=True, drop=True)
    df_spec.index.name = 'Datetime'

    #df_param.insert(loc=0, column='datetime', value=meastime)
    #df_spec.insert(loc=0, column='datetime', value=meastime)

    return df_param, df_spec


if __name__ == '__main__':
    dfparam, dfspec = mat2df(bphiiupaths)
    dfparam.to_csv('bphiiu_param.csv')
    dfspec.to_csv('bphiiu_spec.csv')
    print('a')

