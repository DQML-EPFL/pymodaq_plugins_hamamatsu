import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from scipy.optimize import curve_fit

from pymodaq_plugins_hamamatsu.hardware.minispectro import MiniSpectro

from pymodaq_plugins_hamamatsu.daq_viewer_plugins.plugins_1D.daq_1Dviewer_MiniSpectro import DAQ_1DViewer_MiniSpectro

class DAQ_1DViewer_MiniSpectro_Fit(DAQ_1DViewer_MiniSpectro):
    """ Instrument plugin class for Hamamatsu USB Mini-spectrometers.
    
    This object inherits all functionalities to communicate with PyMoDAQ's DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    This plugin should work with Hamamatsu mini-spectrometers connected with USB on Windows machines only (Python wrapper uses
    .NET libraries to communicate with the device). It has been tested with C10083CA (TM-CCD) and C9913GC (TG-cooled NIR-I)
    mini-spectrometers.

    Tested with PyMoDAQ 4.4.7 on Windows 11.

    The "specu1b.dll" driver is required and is obtained through the installation of Hamamatsu Tokuspec software. This plugin
    should work with the .dll file in its default location (C:\Program Files\Hamamatsu\TokuSpec) but make sure to change its
    path in the python wrapper "minispectro.py" in the case you place it somewhere else. This .dll file can also be found in
    the installation files of the Hamamatsu Evaluation Software originally provided with the device CD.
    """
    params = DAQ_1DViewer_MiniSpectro.params + [

    ]

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        # Synchrone version (blocking function)
        pixel_array, wl_array, data_tot = self.controller.get_sensor_data()

        

        try:
            x_data = wl_array
            y_data = data_tot
            initial_guess = [np.max(y_data) - np.min(y_data), x_data[np.argmax(y_data)], (x_data[-1]-x_data[0])/6 , np.min(y_data)]
            popt, pcov = curve_fit(gaussian, x_data, y_data, p0=initial_guess)

            dfp = []
            dfp.append(DataFromPlugins(name='Mini-spectrometer_Fit',
                                        data=data_tot,
                                        dim='Data1D',
                                        labels=['Data'],
                                        axes=[self.x_axis]))

            dfp.append(DataFromPlugins(name='Mini-spectrometer_Fit',
                                        data=gaussian(x_data, *popt),
                                        dim='Data1D',
                                        labels=['Fit'],
                                        axes=[self.x_axis]))

            self.dte_signal.emit(DataToExport(name='MiniSpectro', data=dfp))

            print(popt[1])

        except Exception as e:
            self.dte_signal.emit(DataToExport(name='MiniSpectro',
                                          data=[DataFromPlugins(name='Mini-spectrometer',
                                                                data=data_tot,
                                                                dim='Data1D',
                                                                labels=['Spectrometer'],
                                                                axes=[self.x_axis])]))        




def gaussian(x, a, x0, sigma, offset):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + offset

if __name__ == '__main__':
    main(__file__)