import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy.ma as ma
import numpy as np
import os
import sys
import pathlib
from scipy import io

import pandas as pd
import re
import datetime as dt


def mat2df(paths):
    df_param = pd.DataFrame()
    df_spec = pd.DataFrame()

    for path in paths:

        if path.endswith('.txt'):
            webdf = pd.read_csv(paths[0], header=None, sep=' ')
            meastime = pd.to_datetime(webdf[0] + ' ' + webdf[1])

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
    peipsipaths = [
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\Web\Sent\web.txt",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_05\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_06\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_07\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_08\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_09\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_10\Sent",
        r"D:\Project_data\2023-eag249\LP_data\12-Peipsi\WaveParam_LTE\2022_11\Sent"]

    kihnu1paths = [
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\Web\web.txt",
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\2023_04",
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\2023_05",
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\2023_06",
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\2023_07",
        r"D:\Project_data\2023-eag249\LP_data\14-Kihnu\WaveParam_LTE\2023_08"]

    bphiiupaths = [
        r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\Web\web.txt",
        r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_04",
        r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_05",
        r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_06",
        r"C:\Users\sander.rikka\OneDrive - Tallinna Tehnikaülikool\Projektid\2023-eag249\Lainepoiss\21-BP-Hiiumaa\2023_07"]

    liivipaths = [
        r"D:\Project_data\2023-eag249\LP_data\23-Liivi\WaveParam_LTE\Web\web.txt",
        r"D:\Project_data\2023-eag249\LP_data\23-Liivi\WaveParam_LTE\2023_04",
        r"D:\Project_data\2023-eag249\LP_data\23-Liivi\WaveParam_LTE\2023_05",
        r"D:\Project_data\2023-eag249\LP_data\23-Liivi\WaveParam_LTE\2023_06",
        r"D:\Project_data\2023-eag249\LP_data\23-Liivi\WaveParam_LTE\2023_07"]

    kihnu2paths = [
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\Web\web.txt",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_04\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_05\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_06\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_07\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_08",
        r"D:\Project_data\2023-eag249\LP_data\Kihnu_2023.04.13\LP_16\WaveParam_LTE\2023_09"]

    pakrikaadpaths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri-kaadamisala\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri-kaadamisala\2023_10\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri-kaadamisala\2023_11\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri-kaadamisala\2023_12\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri-kaadamisala\2024_01\Sent"]

    pakri1paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.04.21\Pakri_2022.04.21\LP_1\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.04.21\Pakri_2022.04.21\LP_1\WaveParam_LTE\2022_04\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.04.21\Pakri_2022.04.21\LP_1\WaveParam_LTE\2022_05\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.04.21\Pakri_2022.04.21\LP_1\WaveParam_LTE\2022_06\Sent"]

    pakri2paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.06.21\Pakri_2022.06.21\LP_1\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.06.21\Pakri_2022.06.21\LP_1\WaveParam_LTE\2022_06\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.06.21\Pakri_2022.06.21\LP_1\WaveParam_LTE\2022_07\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.06.21\Pakri_2022.06.21\LP_1\WaveParam_LTE\2022_08\Sent"]

    pakri3paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.08.10\LP_1\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.08.10\LP_1\WaveParam_LTE\2022_08\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.08.10\LP_1\WaveParam_LTE\2022_09\Sent"]

    pakri4paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.09.28\LP_1\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.09.28\LP_1\WaveParam_LTE\2022_09\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.09.28\LP_1\WaveParam_LTE\2022_10\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.09.28\LP_1\WaveParam_LTE\2022_11\Sent"]

    pakri5paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.12.29\LP_15\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pakri_2022.04.21_2023.01.17\Pakri_2022.12.29\LP_15"]

    parnu1paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_15\WaveParam_LTE\Web\Sent\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_15\WaveParam_LTE\2022_09\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_15\WaveParam_LTE\2022_10\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_15\WaveParam_LTE\2022_11\Sent"]

    parnu2paths = [
        r'D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_16\WaveParam_LTE\Web\Sent\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_16\WaveParam_LTE\2022_09\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_16\WaveParam_LTE\2022_10\Sent",
        r"D:\Project_data\2023-eag249\LP_data\Pärnu_2022_09_13\LP_16\WaveParam_LTE\2022_11\Sent"]

    ruhnu2paths = [
        r'D:\Project_data\2023-eag249\LP_data\Ruhnu_04.08.2021\LP_2\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Ruhnu_04.08.2021\LP_2\WaveParam_LTE"]

    ruhnu3paths = [
        r'D:\Project_data\2023-eag249\LP_data\Ruhnu_2021.09.27\LP_3\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Ruhnu_2021.09.27\LP_3\WaveParam_LTE"]

    ruhnu4paths = [
        r'D:\Project_data\2023-eag249\LP_data\Ruhnu_2021.10.01\LP_2\WaveParam_LTE',
        r"D:\Project_data\2023-eag249\LP_data\Ruhnu_2021.10.01\LP_2\WaveParam_LTE"]

    ruhnu1paths = [
        r'D:\Project_data\2023-eag249\LP_data\Ruhnu_28.07.2021\LP_4\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Ruhnu_28.07.2021\LP_4\WaveParam_LTE"]

    gofpaths = [
        r'D:\Project_data\2023-eag249\LP_data\Soome_laht_2023.10.30\LP_16\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Soome_laht_2023.10.30\LP_16\WaveParam_LTE\2023_10",
        r"D:\Project_data\2023-eag249\LP_data\Soome_laht_2023.10.30\LP_16\WaveParam_LTE\2023_11"]

    sorve1paths = [
        r'D:\Project_data\2023-eag249\LP_data\Sõrve_2021.07.27\LP_5\WaveParam_LTE',
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2021.07.27\LP_5\WaveParam_LTE"]

    sorve2paths = [
        r'D:\Project_data\2023-eag249\LP_data\Sõrve_2021.11.04\LP_7\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2021.11.04\LP_7\WaveParam_LTE\2021_11",
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2021.11.04\LP_7\WaveParam_LTE\2021_12",
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2021.11.04\LP_7\WaveParam_LTE\2022_01",
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2021.11.04\LP_7\WaveParam_LTE\2022_02"]

    sorve3paths = [
        r'D:\Project_data\2023-eag249\LP_data\Sõrve_2022.02.23\LP_4\WaveParam_LTE\Web',
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2022.02.23\LP_4\WaveParam_LTE\2022_02",
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2022.02.23\LP_4\WaveParam_LTE\2022_03",
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2022.02.23\LP_4\WaveParam_LTE\2022_04"]

    sorve4paths = [
        r'D:\Project_data\2023-eag249\LP_data\Sõrve_2022.04.19 cleaned\Sõrve_2022.04.19\LP_2\WaveParam_LTE\Web\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Sõrve_2022.04.19 cleaned\Sõrve_2022.04.19\LP_2\WaveParam_LTE\2022_04"]

    vj1paths = [
        r'D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_1\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_1\WaveParam_LTE"]

    vj2paths = [
        r'D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_2\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_2\WaveParam_LTE"]

    vj3paths = [
        r'D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_3\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_3\WaveParam_LTE"]

    vj4paths = [
        r'D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_4\WaveParam_LTE\web.txt',
        r"D:\Project_data\2023-eag249\LP_data\Vaana-Joesuu_2020.12.11\Vääna-Jõesuu_2020.12.11\Poi_4\WaveParam_LTE"]

    allpaths = {
        'peipsi': peipsipaths,
        'kihnu1': kihnu1paths,
        'kihnu2': kihnu2paths,
        'bphiiu': bphiiupaths,
        'liivi': liivipaths,
        'pakrikaad': pakrikaadpaths,
        'pakri1': pakri1paths,
        'pakri2': pakri2paths,
        'pakri3': pakri3paths,
        'pakri4': pakri4paths,
        'pakri5': pakri5paths,
        'parnu1': parnu1paths,
        'parnu2': parnu2paths,
        'soomelaht': gofpaths,
        'sorve1': sorve1paths,
        'sorve2': sorve2paths,
        'sorve3': sorve3paths,
        'sorve4': sorve4paths,
        'ruhnu1': ruhnu1paths,
        'ruhnu2': ruhnu2paths,
        'ruhnu3': ruhnu3paths,
        'ruhnu4': ruhnu4paths,
        'vj1': vj1paths,
        'vj2': vj2paths,
        'vj3': vj3paths,
        'vj4': vj4paths
    }

    for key in allpaths:
        dfparam, dfspec = mat2df(allpaths[key])
        dfparam.to_csv(f'data/{key}_param.csv')
        dfspec.to_csv(f'data/{key}_spec.csv')
    print('The end!')

