import numpy as np
import xarray as xr


class Moment:
    """Spectral moment from spectra"""
    def __init__(self, moment: float) -> None:
        self._moment = moment
        pass

    def __call__(self, spec):
        moment = spec

        moment = (moment*(moment.freq**self._moment)).integrate(coord='freq')

        return moment


class WaveParameters(object):
    """
    Collection of wave parameters calculated from 1D wave spectra.
    Deals with 1D energy spectra only. No spread or direction parameters possible!
    """

    def __init__(self, spec, freq=None):
        """

        :param spec: array of spectra
        :param freq: frequency axis of spectra
        :return: ndarray of parameter.
        """
        if not freq.all():
            print(f'No frequency axis is provided. Exiting the process.')
            exit()

        self.spec = spec
        self.freq = freq
        self.xr_spec = self.compile_to_xr()

    def hs(self):
        return (4 * Moment(0)(self.xr_spec) ** 0.5).spec.values

    def tm01(self):
        return (Moment(0)(self.xr_spec)/Moment(1)(self.xr_spec)).spec.values

    def tm_10(self):
        return (Moment(-1)(self.xr_spec)/Moment(0)(self.xr_spec)).spec.values

    def tm02(self):
        return ((Moment(0)(self.xr_spec)/Moment(2)(self.xr_spec)) ** 0.5).spec.values

    def fm(self):
        return (Moment(1)(self.xr_spec)/Moment(0)(self.xr_spec)).spec.values

    def wm(self):
        return ((Moment(1)(self.xr_spec)/Moment(0)(self.xr_spec)) * 2 * np.pi).spec.values

    def tp(self):
        max_ind = self.xr_spec.argmax(dim='freq').to_dataframe()
        freq = self.xr_spec.freq.values
        return 1 / freq[max_ind['spec']]

    def compile_to_xr(self):
        """

        :param freq:
        :param spec:
        :return: xrarray type dataset
        """
        data = xr.Dataset(
            data_vars=dict(
                spec=(["x", "freq"], self.spec),
            ),
            coords=dict(
                freq=self.freq
            ),
        )
        return data


if __name__ == '__main__':
    # for testing purposes!
    from model_dev.datamanager import load_inputs_outputs, DataManager

    sar_to_load = []
    mdl_to_load = ['model_spec', 'model_param']
    data_inst_clean = load_inputs_outputs(sar_to_load, mdl_to_load, min_hs=0.3, min_depth=-10, max_tp=10)

    new_freq = np.arange(0.1, 0.51, 0.01)  # 0.01 step on sama, mis lainepoisil, aga seda võib muuta, kuidas vaja/soov
    model_spec = DataManager(data_inst_clean[mdl_to_load[0]].data,
                             data_inst_clean[mdl_to_load[0]].name).data_interpolate(new_freq, kind='MDL')

    hs = WaveParameters(np.array(model_spec), new_freq).tm_10()

    og_wm = data_inst_clean[mdl_to_load[1]].data['tm_10'].to_numpy()
    print(np.corrcoef(og_wm, hs))
