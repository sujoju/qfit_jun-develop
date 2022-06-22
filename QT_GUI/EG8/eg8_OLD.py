from inspect import currentframe
import sys

from PySide2 import QtWidgets

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import numpy as np
import scqubits as scq
import random
from floatslider import FloatSlider
from eg8_ui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #Need to utilize the defaults in GUI class
        self.hilbertspace_defaults = {
            "resonator": {
                "E_osc": {"min": 0.0, "max": 10.0, "value": 4.5},
                "l_osc": {"min": 0.0, "max": 5.0, "value": 0.0},
                "truncated_dim": {"min": 0, "max": 10, "value": 4},
                "id_str": {"value": "resonator"}
            },
            "tmon1": {
                "EJmax": {"min": 1e-10, "max": 50.0, "value": 40.0},
                "EC": {"min": 1e-10, "max": 5.0, "value": 0.2},
                "d": {"min": 0.0, "max": 1.0, "value": 0.1},
                "flux": {"min": 0.0, "max": 1.0, "value": 0.23},
                "ng": {"min": 0.0, "max": 1.0, "value": 0.3},
                "ncut": {"min": 10, "max": 50, "value": 40},
                "truncated_dim": {"min": 0, "max": 10, "value": 3},
                "id_str": {"value": "tmon1"}
            },
            "tmon2": {
                "EJmax": {"min": 1e-10, "max": 50.0, "value": 15.0},
                "EC": {"min": 1e-10, "max": 5.0, "value": 0.15},
                "d": {"min": 0.0, "max": 1.0, "value": 0.2},
                "flux": {"min": 0.0, "max": 1.0, "value": 0.0},
                "ng": {"min": 0.0, "max": 1.0, "value": 0.0},
                "ncut": {"min": 10, "max": 50, "value": 30},
                "truncated_dim": {"min": 0, "max": 10, "value": 3},
                "id_str": {"value": "tmon2"}
            },
            "g1": 0.1,
            "g2": 0.2
        }
        self.parametersweep_defaults = {
            "flux": {"min": 0.0, "max": 2.0, "value": 1.0, "index": 0},
            "ng": {"min": -0.5, "max": 0.5, "value": 0.0, "index": 1},
            "num_sample": 21,
            "scan_param": "flux",
            "area_ratio": 1.2,
            "eval": 5
        }
        self.subsys_widget_Dict = {}
        self.parametersweep_widget_Dict = {}
        self.subsys_widget_layout_Dict = {}
        self.parametersweep_widget_layout_Dict = {}
        self.subsys_params_Dict = {}
        self.parametersweep_params_Dict = {}
        self.hilbertspace = None
        self.parametersweep = None
        self.current_sweep = self.parametersweep_defaults["scan_param"]

        init_subsys_params = {
            "tmon1": self.get_subsys_defaults("tmon1"),
            "tmon2": self.get_subsys_defaults("tmon2"),
            "resonator": self.get_subsys_defaults("resonator")
        }
        self.create_hilbertspace(init_subsys_params)
        self.create_parametersweep(self.parametersweep_defaults["eval"])
        self.create_parametersweep_params_Dict()
        self.create_parametersweep_widget_Dict()
        self.create_parametersweep_widget_layout_Dict()
        self.create_param_layout()
        self.create_subsys_params_Dict()
        self.create_subsys_widget_Dict()
        self.disable_parameters()
        self.create_subsys_widget_layout_Dict()
        self.create_subsys_layout()

        self.connect_widgets()

        test_values = {
            "flux": 0.4,
            "ng": 0.2
        }
        sweep = "ng"
        self.mplFigureCanvas.create_noisy_data(
            self.parametersweep, sweep, test_values)
        self.update_plot()

        self.show()

    # function that defines how Hilbert space components are updated
    def update_hilbertspace(self, flux, ng):
        self.tmon1.flux = flux
        self.tmon2.flux = self.parametersweep_defaults["area_ratio"] * flux
        self.tmon2.ng = ng

    # Need to REDO
    def disable_parameters(self):
        original_subsys_params_dict = self.subsys_params_Dict.copy()
        params_rand =()
        for param, param_Dict in self.parametersweep_defaults.items():
            if isinstance(param_Dict, dict):
                params_rand += (round(random.uniform(param_Dict["min"], param_Dict["max"]), 2), )
        
        # print(self.subsys_params_Dict)
        # self.update_hilbertspace(*params_rand)
        # print(self.tmon1.flux, self.tmon2.flux, self.tmon2.ng)

    def get_subsys_defaults(self, subsys):
        subsys_defaults = {}
        for param, param_dict in self.hilbertspace_defaults[subsys].items():
            subsys_defaults[param] = param_dict["value"]

        return subsys_defaults

    def create_hilbertspace(self, subsys_params):
        self.tmon1 = scq.TunableTransmon(**subsys_params["tmon1"])
        self.tmon2 = scq.TunableTransmon(**subsys_params["tmon2"])
        self.resonator = scq.Oscillator(
            **subsys_params["resonator"])

        self.hilbertspace = scq.HilbertSpace(
            [self.tmon1, self.tmon2, self.resonator])

        g1 = self.hilbertspace_defaults["g1"]
        g2 = self.hilbertspace_defaults["g2"]

        self.hilbertspace.add_interaction(
            g_strength=g1,
            op1=self.tmon1.n_operator,
            op2=self.resonator.creation_operator,
            add_hc=True,
            id_str="tmon1-resonator"
        )

        self.hilbertspace.add_interaction(
            g_strength=g2,
            op1=self.tmon2.n_operator,
            op2=self.resonator.creation_operator,
            add_hc=True,
            id_str="tmon2-resonator"
        )

    def create_parametersweep(self, evals):
        paramvals_by_name = {}
        for param in self.parametersweep_defaults.keys():
            if isinstance(self.parametersweep_defaults[param], dict):
                param_min = self.parametersweep_defaults[param]["min"]
                param_max = self.parametersweep_defaults[param]["max"]
                num_sample = self.parametersweep_defaults["num_sample"]
                param_vals = np.linspace(param_min, param_max, num_sample)
                paramvals_by_name[param] = param_vals

        self.parametersweep = scq.ParameterSweep(
            hilbertspace=self.hilbertspace,
            paramvals_by_name=paramvals_by_name,
            update_hilbertspace=self.update_hilbertspace,
            evals_count=evals
        )

    def get_current_values(self, tab_index):
        current_values_Dict = {}
        tab_name = self.parametersweepTabWidget.tabText(tab_index)
        if tab_name == "Parameters":
            for sweep, sweep_Dict in self.parametersweep_widget_Dict.items():
                spinBox_key = sweep + "_spinBox"
                spinBox = self.parametersweep_widget_Dict[sweep][spinBox_key]

                current_values_Dict[sweep] = spinBox.value(
                )
        else:
            for param, param_Dict in self.subsys_widget_Dict[tab_name].items():
                spinBox_key = param + "_spinBox"
                spinBox = self.subsys_widget_Dict[tab_name][param][spinBox_key]

                current_values_Dict[param] = spinBox.value(
                )

        return current_values_Dict

    def create_subsys_params_Dict(self):
        for i in range(self.parametersweep.subsystem_count):
            subsys = self.parametersweep.get_subsys(i).id_str
            self.subsys_params_Dict[subsys] = {}

            for param in self.parametersweep.get_subsys(i).default_params().keys():
                self.subsys_params_Dict[subsys][param] = self.hilbertspace_defaults[subsys][param]["value"]

    def create_parametersweep_params_Dict(self):
        for param, param_dict in self.parametersweep.param_info.items():
            self.parametersweep_params_Dict[param] = param_dict[0]

    def create_subsys_widget_Dict(self):
        for subsys, subsys_Dict in self.subsys_params_Dict.items():
            self.subsys_widget_Dict[subsys] = {}
            for param in subsys_Dict.keys():
                self.subsys_widget_Dict[subsys][param] = {}
            self.create_label_widgets(
                self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])
            self.create_slider_widgets(
                self.hilbertspace_defaults[subsys], self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])
            self.create_spinBox_widgets(
                self.hilbertspace_defaults[subsys], self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])

    def create_parametersweep_widget_Dict(self):
        for sweep in self.parametersweep_params_Dict.keys():
            self.parametersweep_widget_Dict[sweep] = {}

        
        self.create_label_widgets(
            self.parametersweep_params_Dict, self.parametersweep_widget_Dict)
        self.create_slider_widgets(
            self.parametersweep_defaults, self.parametersweep_params_Dict, self.parametersweep_widget_Dict)
        self.create_spinBox_widgets(
            self.parametersweep_defaults, self.parametersweep_params_Dict, self.parametersweep_widget_Dict)

    def create_label_widgets(self, params_Dict, widget_Dict):
        for sweep in params_Dict.keys():
            object_name = sweep + "_label"
            label_value = sweep + " Value:"
            widget_Dict[sweep][object_name] = QtWidgets.QLabel(
                self.centralwidget)
            widget_Dict[sweep][object_name].setObjectName(object_name)
            widget_Dict[sweep][object_name].setText(
                QCoreApplication.translate("MainWindow", label_value, None))

    def create_slider_widgets(self, defaults, params_Dict, widget_Dict):
        for sweep, value in params_Dict.items():
            object_name = sweep + "_slider"

            if isinstance(value, int):
                slider_min = defaults[sweep]["min"]
                slider_max = defaults[sweep]["max"]

                widget_Dict[sweep][object_name] = QtWidgets.QSlider(
                    self.centralwidget)
                widget_Dict[sweep][object_name].setObjectName(
                    object_name)
                widget_Dict[sweep][object_name].setMinimum(
                    slider_min)
                widget_Dict[sweep][object_name].setMaximum(
                    slider_max)
                widget_Dict[sweep][object_name].setSingleStep(
                    1)
                widget_Dict[sweep][object_name].setValue(
                    value)
                widget_Dict[sweep][object_name].setSliderPosition(
                    value)
                widget_Dict[sweep][object_name].setOrientation(
                    Qt.Horizontal)
                widget_Dict[sweep][object_name].setTickInterval(
                    0)
            else:
                slider_min = defaults[sweep]["min"]*100
                slider_max = defaults[sweep]["max"]*100
                slider_value = value*100

                widget_Dict[sweep][object_name] = FloatSlider(
                    self.centralwidget)
                widget_Dict[sweep][object_name].setObjectName(
                    object_name)
                widget_Dict[sweep][object_name].setMinimum(
                    slider_min)
                widget_Dict[sweep][object_name].setMaximum(
                    slider_max)
                widget_Dict[sweep][object_name].setSingleStep(
                    1)
                widget_Dict[sweep][object_name].setValue(
                    slider_value)
                widget_Dict[sweep][object_name].setSliderPosition(
                    slider_value)
                widget_Dict[sweep][object_name].setOrientation(
                    Qt.Horizontal)
                widget_Dict[sweep][object_name].setTickInterval(
                    0)

            if defaults == self.parametersweep_defaults:
                if sweep == self.current_sweep:
                    widget_Dict[sweep][object_name].setEnabled(
                        False)

    def create_spinBox_widgets(self, defaults, params_Dict, widget_Dict):
        for sweep, value in params_Dict.items():
            object_name = sweep + "_spinBox"

            if isinstance(value, int):
                slider_min = defaults[sweep]["min"]
                slider_max = defaults[sweep]["max"]

                widget_Dict[sweep][object_name] = QSpinBox(
                    self.centralwidget)
                widget_Dict[sweep][object_name].setObjectName(
                    object_name)
                widget_Dict[sweep][object_name].setMinimum(
                    slider_min)
                widget_Dict[sweep][object_name].setMaximum(
                    slider_max)
                widget_Dict[sweep][object_name].setValue(
                    value)

            else:
                slider_min = defaults[sweep]["min"]
                slider_max = defaults[sweep]["max"]

                widget_Dict[sweep][object_name] = QDoubleSpinBox(
                    self.centralwidget)
                widget_Dict[sweep][object_name].setObjectName(
                    object_name)
                widget_Dict[sweep][object_name].setDecimals(
                    2)
                widget_Dict[sweep][object_name].setMinimum(
                    slider_min)
                widget_Dict[sweep][object_name].setMaximum(
                    slider_max)
                widget_Dict[sweep][object_name].setSingleStep(
                    0.01)
                widget_Dict[sweep][object_name].setValue(
                    value)

            if defaults == self.parametersweep_defaults:
                if sweep == self.current_sweep:
                    widget_Dict[sweep][object_name].setEnabled(
                        False)

    def create_subsys_widget_layout_Dict(self):
        for subsys, subsys_Dict in self.subsys_widget_Dict.items():
            self.subsys_widget_layout_Dict[subsys] = {}
            for param in subsys_Dict.keys():
                self.subsys_widget_layout_Dict[subsys][param] = {}
            self.create_widget_layout(
                self.subsys_widget_Dict[subsys], self.subsys_widget_layout_Dict[subsys])

    def create_parametersweep_widget_layout_Dict(self):
        for sweep in self.parametersweep_widget_Dict.keys():
            self.parametersweep_widget_layout_Dict[sweep] = {}

        self.create_widget_layout(
            self.parametersweep_widget_Dict, self.parametersweep_widget_layout_Dict)

    def create_widget_layout(self, widget_Dict, widget_layout_Dict):
        for sweep, sweep_Dict in widget_Dict.items():
            label_key = sweep + "_label"
            spinBox_key = sweep + "_spinBox"
            slider_key = sweep + "_slider"
            layout_object_name = sweep + "_layout"

            label_spinBox_layout = QHBoxLayout()
            label_spinBox_layout.addWidget(sweep_Dict[label_key])
            label_spinBox_layout.addWidget(sweep_Dict[spinBox_key])

            total_layout = QVBoxLayout()
            total_layout.addLayout(label_spinBox_layout)
            total_layout.addWidget(sweep_Dict[slider_key])
            widget_layout_Dict[sweep] = total_layout
            widget_layout_Dict[sweep].setObjectName(
                layout_object_name)

    def create_param_layout(self):
        total_layout = QVBoxLayout()
        for sweep, layout in self.parametersweep_widget_layout_Dict.items():
            total_layout.addLayout(layout)
            self.sweep_comboBox.addItem(sweep)

            if sweep == self.parametersweep_defaults["scan_param"]:
                self.sweep_comboBox.setCurrentText(sweep)

        self.parameters_tab.setLayout(total_layout)

    def create_subsys_layout(self):
        for subsys, subsys_Dict in self.subsys_widget_layout_Dict.items():
            total_layout = QVBoxLayout()
            subsys_tab_name = subsys + "_tab"
            subsys_tab = QWidget()
            subsys_tab.setObjectName(subsys_tab_name)

            for param, layout in subsys_Dict.items():
                total_layout.addLayout(layout)

            subsys_tab.setLayout(total_layout)
            self.parametersweepTabWidget.addTab(subsys_tab, subsys)

    def connect_param_slider_spinBox(self, widget_Dict):
        for sweep, sweep_Dict in widget_Dict.items():
            spinBox_key = sweep + "_spinBox"
            slider_key = sweep + "_slider"

            slider = widget_Dict[sweep][slider_key]
            spinBox = widget_Dict[sweep][spinBox_key]

            if isinstance(slider, FloatSlider):
                slider.intToDouble.connect(spinBox.setValue)
                spinBox.valueChanged.connect(slider.doubleToInt)
            else:
                slider.valueChanged.connect(spinBox.setValue)
                spinBox.valueChanged.connect(slider.setValue)

            if widget_Dict == self.parametersweep_widget_Dict:
                slider.sliderReleased.connect(self.update_plot)
                spinBox.editingFinished.connect(self.update_plot)
            else:
                slider.sliderReleased.connect(self.update_subsys_params_Dict)
                spinBox.editingFinished.connect(self.update_subsys_params_Dict)

    def connect_widgets(self):
        self.sweep_comboBox.currentTextChanged.connect(
            self.adjust_enabled_sweep)
        self.sweep_comboBox.currentTextChanged.connect(self.update_plot)
        self.show_data_checkBox.stateChanged.connect(self.update_plot)
        self.updateParameterSweepButton.clicked.connect(
            self.update_parametersweep)
        self.fitButton.clicked.connect(self.fit_plot)

        self.connect_param_slider_spinBox(self.parametersweep_widget_Dict)
        for subsys, subsys_Dict in self.subsys_widget_Dict.items():
            self.connect_param_slider_spinBox(subsys_Dict)

    def adjust_enabled_sweep(self, new_sweep):
        for sweep, sweep_Dict in self.parametersweep_widget_Dict.items():
            spinBox_key = sweep + "_spinBox"
            slider_key = sweep + "_slider"

            slider = self.parametersweep_widget_Dict[sweep][slider_key]
            spinBox = self.parametersweep_widget_Dict[sweep][spinBox_key]

            if sweep == new_sweep:
                slider.setEnabled(False)
                spinBox.setEnabled(False)
            elif sweep == self.current_sweep:
                slider.setEnabled(True)
                spinBox.setEnabled(True)
            else:
                pass
        self.current_sweep = new_sweep

    def update_plot(self):
        tab_index = 0
        current_values = self.get_current_values(tab_index)
        show_data_tf = self.show_data_checkBox.isChecked()

        self.mplFigureCanvas.plot_parametersweep(
            self.parametersweep, self.current_sweep, current_values, show_data_tf)

    def update_subsys_params_Dict(self):
        total_tabs = self.parametersweepTabWidget.count()
        for tab_index in range(1, total_tabs, 1):
            current_values = self.get_current_values(tab_index)
            tab_name = self.parametersweepTabWidget.tabText(tab_index)
            for param, param_val in current_values.items():
                self.subsys_params_Dict[tab_name][param] = param_val

    def update_parametersweep(self):
        evals = self.evals_count_spinBox.value()
        self.create_hilbertspace(self.subsys_params_Dict)
        self.create_parametersweep(evals)
        self.update_plot()

    def fit_plot(self):
        current_values = self.get_current_values(0)
        current_sweep_Dict = {}
        for param, param_val in current_values.items():
            current_sweep_Dict[param] = {
                "min": self.parametersweep_defaults[param]["min"],
                "max": self.parametersweep_defaults[param]["max"],
                "value": param_val
            }
        fit_report = self.mplFigureCanvas.fit_parametersweep(
            self.parametersweep, self.current_sweep, current_sweep_Dict)
        QMessageBox.information(self, "Fit Report", fit_report)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
