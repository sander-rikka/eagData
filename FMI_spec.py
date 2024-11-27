"""just for fun challenge to do this in OOP"""
import os
import sys

import netCDF4 as nc
import numpy as np
import numpy.ma as ma
import pandas as pd

from wave_parameters import WaveParameters as WP


class FmiDataLoad(object):
    datapath = r'D:\Project_data\2023-eag249\FMI_data'
    # datapath = r'C:\Temp'  # for laptop
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
        print(f'Loading parameter {param} for {self.stationname}')
        df = pd.DataFrame()
        for file in self.available_files:
            dset = nc.Dataset(os.path.join(FmiDataLoad.datapath, file))
            time = dset['time']

            data = ma.getdata(dset[param][:])
            df_i = pd.DataFrame(data[FmiDataLoad.start_f_ind: FmiDataLoad.end_f_ind, :].T,
                                index=pd.to_datetime(time[:], unit='s'))
            df = pd.concat([df, df_i], axis=0)

        df = df.replace(to_replace=-9., value=sys.float_info.epsilon)
        df["Datetime"] = pd.to_datetime(df.index.tolist())
        df.set_index("Datetime", inplace=True)

        # filter for half hour data
        df = df[(df.index.minute < 25) | (df.index.minute > 30)]
        df.reset_index(inplace=True)

        df['Datetime'] = df['Datetime'].dt.round("h")
        # assumption that all the Frequency values between files are the same.. should check
        f = dset['F']  # takes F from last file
        self.F = ma.getdata(f[:][FmiDataLoad.start_f_ind:FmiDataLoad.end_f_ind, 0])

        f_str = [str(x) for x in f[:][FmiDataLoad.start_f_ind:FmiDataLoad.end_f_ind, 0]]
        # append frequency values as heading for dataframe
        df.columns = [col if i < 1 else f_str[i - 1] for i, col in enumerate(df.columns)]
        # df.columns = f_str

        # Drop duplicates based on the rounded 'Datetime'
        df = df.drop_duplicates(subset="Datetime", keep="first")

        df.set_index("Datetime", inplace=True)
        self.time = df.index.values
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
        if self.stationname == 'BS':
            self.stationname = 'BOT'

        print(f'Saving data for {self.stationname}')
        self.S.to_csv(f'FMI_{self.stationname.lower()}_spec.csv')
        # self.bulk_params.to_csv(f'FMI_{self.stationname.lower()}_bulkparams.csv')
        if self.D is not None:
            self.D.to_csv(f'FMI_{self.stationname.lower()}_mdir.csv')
        if self.SPR is not None:
            self.SPR.to_csv(f'FMI_{self.stationname.lower()}_spr.csv')

    def get_available_files(self) -> list:
        files = os.listdir(FmiDataLoad.datapath)
        available_files = []
        for file in files:
            if file.startswith(self.stationname):
                available_files.append(file)
        if not available_files:
            raise ValueError(f'empty list for available files. check the input path. current value {self.datapath}.')
        else:
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
        if station in ['BS', 'NBP', 'GoF']:
            return True
        else:
            raise ValueError(f'Not valid stationname, expected BS, NBP, GoF. Got {station}')

    @staticmethod
    def valid_params(param):
        if param in ['S', 'spr', 'D']:
            return True
        else:
            raise ValueError(f'Not valid parameter name! Expected S, or spr; got {param}.')


if __name__ == '__main__':
    BS = FmiDataLoad('BS', ['S', 'spr', 'D'])
    BS.load_vars_into_df()
    BS.save_vars_csv()

    NBP = FmiDataLoad('NBP', ['S', 'spr', 'D'])
    NBP.load_vars_into_df()
    NBP.save_vars_csv()

    GOF = FmiDataLoad('GoF', ['S', 'spr', 'D'])
    GOF.load_vars_into_df()
    GOF.save_vars_csv()

    print('The end!')
