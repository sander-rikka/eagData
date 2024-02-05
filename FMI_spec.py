"""just for fun challenge to do this in OOP"""
import os
import sys

import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import pandas as pd

from wave_parameters import WaveParameters as WP


class FmiDataLoad(object):
    #datapath = r'D:\Project_data\2023-eag249\FMI_data'
    datapath = r'C:\Temp'  # for laptop
    start_f_ind = 0  # 0.025 Hz
    end_f_ind = 80  # 0.6 Hz

    def __init__(self, station: str, ds_params: list):
        if self.validate_station_name(station):
            self.stationname = station
        if self.validate_param_names(ds_params):
            self.ds_params = ds_params

        self.available_files = self.get_available_files()
        self.F = None
        self.time = None
        self.S = None
        self.bulk_params = None
        self.SPR = None
        self.D = None

    def load_vars_into_df(self):
        for param in self.ds_params:
            if param == 'S':
                self.S = self.load_param(param)
                self.bulk_params = self.calculate_bulk_params()
            if param == 'spr':
                self.SPR = self.load_param(param)
            if param == 'D':
                self.D = self.load_param(param)

    def load_param(self, param) -> pd.DataFrame:
        df = pd.DataFrame()
        for file in self.available_files:
            dset = nc.Dataset(os.path.join(FmiDataLoad.datapath, file))
            time = dset['time']

            data = ma.getdata(dset[param][:])
            df_i = pd.DataFrame(data[FmiDataLoad.start_f_ind: FmiDataLoad.end_f_ind, :].T,
                                index=pd.to_datetime(time[:], unit='s'))
            df = pd.concat([df, df_i], axis=0)

        df = df.replace(to_replace=-9., value=sys.float_info.epsilon)
        # assumption that all the Frequency values between files are the same.. should check
        f = dset['F']  # takes F from last file
        self.F = ma.getdata(f[:][FmiDataLoad.start_f_ind:FmiDataLoad.end_f_ind, 0])
        self.time = df.index.values
        f_str = [str(x) for x in f[:][FmiDataLoad.start_f_ind:FmiDataLoad.end_f_ind, 0]]
        df.columns = f_str
        return df

    def calculate_bulk_params(self) -> pd.DataFrame:
        params = np.vstack([WP(np.array(self.S), self.F).hs(),
                            WP(np.array(self.S), self.F).tp(),
                            WP(np.array(self.S), self.F).tm01(),
                            WP(np.array(self.S), self.F).tm_10(),
                            WP(np.array(self.S), self.F).tm02(),
                            WP(np.array(self.S), self.F).fm(),
                            WP(np.array(self.S), self.F).wm()
                            ])
        return pd.DataFrame(params.T, columns=['hs', 'tp', 'tm01', 'tm_10', 'tm02', 'fm', 'wm'], index=self.time)

    def save_vars_csv(self):
        self.S.to_csv(f'spec1D_{self.stationname}')
        self.bulk_params.to_csv(f'bulkparams_{self.stationname}')
        if not self.D:
            self.D.to_csv(f'specdir_{self.stationname}')
        if not self.SPR:
            self.SPR.to_csv(f'specspr_{self.stationname}')

    def get_available_files(self) -> list:
        files = os.listdir(FmiDataLoad.datapath)
        available_files = []
        for file in files:
            if file.startswith(self.stationname):
                available_files.append(file)
        return available_files

    @staticmethod
    def validate_param_names(params):
        valid = []
        for param in params:
            valid.append(FmiDataLoad.valid_params(param))
            if np.all(valid):
                return True
            else:
                raise ValueError(f'Not valid parameter names. Expected S, spr; got {param}')

    @staticmethod
    def validate_station_name(station):
        if station in ['BS', 'NBP', 'GOF']:
            return True
        else:
            raise ValueError(f'Not valid stationname, expected BS, NBP, GOF. Got {station}')

    @staticmethod
    def valid_params(param):
        if param in ['S', 'spr', 'D']:
            return True
        else:
            raise ValueError(f'Not valid parameter name! Expected S, or spr; got {param}.')


if __name__ == '__main__':
    BS = FmiDataLoad('BS', ['S'])
    BS.load_vars_into_df()

    dset = nc.Dataset(r'C:\Temp\BS_2016.nc')
    hs = ma.getdata(dset['Hs'][:])
    print(np.corrcoef(BS.bulk_params['hs'].values[0:14636], hs))
    print(np.mean(BS.bulk_params['hs'].values[0:14636]) - np.mean(hs))

    print('a')