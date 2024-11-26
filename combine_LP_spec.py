"""Combine LainePoiss spectra and parameter dataframes by stations."""
import pandas as pd
import glob


stations2combine = ['pakri','ruhnu','sorve','vj']

for station in stations2combine:
    df_spec_comb = pd.DataFrame()
    df_prms_comb = pd.DataFrame()

    spec_files = glob.glob('data/*'+station+'[0-9]_spec.csv')
    prms_files = glob.glob('data/*'+station+'[0-9]_param.csv')
    for filename in spec_files:
        dfi_s = pd.read_csv(filename)
        df_spec_comb = pd.concat([df_spec_comb, dfi_s], axis=0, ignore_index=True)

    for filename in prms_files:
        dfi_p = pd.read_csv(filename)
        df_prms_comb = pd.concat([df_prms_comb, dfi_p], axis=0, ignore_index=True)

    df_spec_comb.to_csv(f'data/{station}_spec_cmb.csv', index=False)
    df_prms_comb.to_csv(f'data/{station}_param_cmb.csv', index=False)