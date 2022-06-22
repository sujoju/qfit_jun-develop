from sys import prefix
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import numpy as np
import scqubits as scq
from scipy import interpolate
from lmfit import Parameters, Minimizer, minimize, fit_report

matplotlib.use("Qt5Agg")


class MplFigureCanvas(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()

        px = 1/plt.rcParams['figure.dpi']
        width = 500*px
        height = 500*px
        dpi = 200
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)

        self.canvas = FigureCanvasQTAgg(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes = fig.add_subplot(111)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def create_point(self, sweep, current_values, sweep_value, evals_value):
        point = []
        for param, value in current_values.items():
            if param == sweep:
                point.append(sweep_value)
            else:
                point.append(value)
        point.append(evals_value)

        return point

    def create_points(self, parametersweep, evals):
        points = ()
        for param_x in parametersweep.param_info.values():
            points = points + (param_x,)

        evals_x = np.linspace(0, evals-1, evals)
        points = points + (evals_x,)

        return points

    def get_interpolated_data_size(self, parametersweep, sweep, evals):
        interpolated_size = ()
        if len(parametersweep.param_info.keys()) == 1:
            interpolated_size = interpolated_size + (list(parametersweep.param_info.values())[0].size,)
        else:
            for param, param_x in parametersweep.param_info.items():
                if param != sweep:
                    interpolated_size = interpolated_size + (param_x.size,)

        interpolated_size = interpolated_size + (evals,)

        return interpolated_size

    def create_interpolated_data(self, parametersweep, sweep, current_values):
        evals = parametersweep.eigenvals().shape[-1]
        sweep_x = parametersweep.param_info[sweep]
        points = self.create_points(parametersweep, evals)
        values = parametersweep["evals"]

        matrix_size = self.get_interpolated_data_size(
            parametersweep, sweep, evals)
        matrix = np.zeros(matrix_size)
        row_index = 0
        for sweep_value in sweep_x:
            column_index = 0
            for evals_value in points[-1]:
                point = self.create_point(
                    sweep, current_values, sweep_value, evals_value)
                matrix[row_index, column_index] = interpolate.interpn(
                    points, values, np.array(point))[0]
                column_index += 1
            row_index += 1
        return matrix

    def plot_parametersweep_noisy_data(self, data_x, noisy_data):
        self.axes.plot(data_x, noisy_data, 'r')

    def plot_parametersweep(self, parametersweep, sweep, current_values, show_data_tf, noisy_data):
        self.axes.clear()

        data = self.create_interpolated_data(
            parametersweep, sweep, current_values)
        data_x = parametersweep.param_info[sweep]

        self.axes.plot(data_x, data)
        self.axes.set_xlabel(sweep)

        if show_data_tf:
            self.plot_parametersweep_noisy_data(data_x, noisy_data)

        self.canvas.draw()

    def parametersweep_resid(self, pars, parametersweep, sweep, current_values, data=None):
        if len(current_values.keys()) == 1:
            current_values[sweep] = pars[sweep]
        else:
            for param in current_values.keys():
                if param != sweep:
                    current_values[param] = pars[param]

        model = self.create_interpolated_data(
            parametersweep, sweep, current_values)
        if data is None:
            return model
        resid = model - data
        return resid.flatten()

    def fit_parametersweep(self, parametersweep, sweep, current_sweep_Dict, noisy_data):
        current_values = {}
        pars = Parameters()
        if len(current_sweep_Dict.keys()) == 1:
            param_val = current_sweep_Dict[sweep]["value"]
            param_min = current_sweep_Dict[sweep]["min"]
            param_max = current_sweep_Dict[sweep]["max"]
            pars.add(sweep, value=param_val, min=param_min, max=param_max)
            current_values[sweep] = current_sweep_Dict[sweep]["value"]
        else:
            for param, param_Dict in current_sweep_Dict.items():
                if param != sweep:
                    param_val = param_Dict["value"]
                    param_min = param_Dict["min"]
                    param_max = param_Dict["max"]
                    pars.add(param, value=param_val, min=param_min, max=param_max)
                current_values[param] = param_Dict["value"]

        min1 = Minimizer(self.parametersweep_resid, pars, fcn_args=(
            parametersweep, sweep, current_values), fcn_kws={'data': noisy_data})
        out1 = min1.minimize()
        # fit1 = self.parametersweep_resid(
        #     out1.params, parametersweep, sweep, current_values)

        return fit_report(out1)
