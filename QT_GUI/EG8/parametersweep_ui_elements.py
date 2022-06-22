from PySide2 import QtWidgets

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import numpy as np
from floatslider import FloatSlider

class ParameterSweep_UI_Elements():
    def __init__(self, parametersweep, centralwidget) -> None:
        # NEED TO CHANGE gui.py such that I make these defaults accessible
        self.hilbertspace_defaults = {
            "resonator": {
                "E_osc": {"min": 0.0, "max": 10.0},
                "l_osc": {"min": 0.0, "max": 5.0},
                "truncated_dim": {"min": 0, "max": 10}
            },
            "tmon1": {
                "EJmax": {"min": 1e-10, "max": 50.0},
                "EC": {"min": 1e-10, "max": 5.0},
                "d": {"min": 0.0, "max": 1.0},
                "flux": {"min": 0.0, "max": 1.0},
                "ng": {"min": 0.0, "max": 1.0},
                "ncut": {"min": 10, "max": 50},
                "truncated_dim": {"min": 0, "max": 10}
            },
            "tmon2": {
                "EJmax": {"min": 1e-10, "max": 50.0},
                "EC": {"min": 1e-10, "max": 5.0},
                "d": {"min": 0.0, "max": 1.0},
                "flux": {"min": 0.0, "max": 1.0},
                "ng": {"min": 0.0, "max": 1.0},
                "ncut": {"min": 10, "max": 50},
                "truncated_dim": {"min": 0, "max": 10}
            }
        }

        self.subsys_widget_Dict = {}
        self.parametersweep_widget_Dict = {}
        self.subsys_widget_layout_Dict = {}
        self.parametersweep_widget_layout_Dict = {}
        self.subsys_params_Dict = {}
        self.parametersweep_params_Dict = {}
        
        self.create_parametersweep_params_Dict(parametersweep)
        self.create_subsys_params_Dict(parametersweep)
        self.create_subsys_widget_Dict(centralwidget)
        self.create_parametersweep_widget_Dict(parametersweep, centralwidget)
        self.create_parametersweep_widget_layout_Dict()
        self.create_subsys_widget_layout_Dict()

    def get_parametersweep_defaults(self, parametersweep):
        defaults = {}
        for param, param_dict in parametersweep.param_info.items():
            defaults[param] = {}
            defaults[param]["min"] = param_dict[0]
            defaults[param]["max"] = param_dict[-1]
        return defaults

    def create_subsys_params_Dict(self, parametersweep):
        for i in range(parametersweep.subsystem_count):
            subsys = parametersweep.get_subsys(i).id_str
            self.subsys_params_Dict[subsys] = parametersweep.hilbertspace.subsystem_list[i].get_initdata()
            del self.subsys_params_Dict[subsys]["id_str"]

    def create_parametersweep_params_Dict(self, parametersweep):
        for param, param_dict in parametersweep.param_info.items():
            self.parametersweep_params_Dict[param] = np.median(param_dict)

    def create_subsys_widget_Dict(self, centralwidget):
        for subsys, subsys_Dict in self.subsys_params_Dict.items():
            self.subsys_widget_Dict[subsys] = {}
            for param in subsys_Dict.keys():
                self.subsys_widget_Dict[subsys][param] = {}
            self.create_label_widgets(centralwidget,
                self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])
            self.create_slider_widgets(centralwidget,
                self.hilbertspace_defaults[subsys], self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])
            self.create_spinBox_widgets(centralwidget,
                self.hilbertspace_defaults[subsys], self.subsys_params_Dict[subsys], self.subsys_widget_Dict[subsys])

    def create_parametersweep_widget_Dict(self, parametersweep, centralwidget):
        for sweep in self.parametersweep_params_Dict.keys():
            self.parametersweep_widget_Dict[sweep] = {}
        parametersweep_defaults  = self.get_parametersweep_defaults(parametersweep)
        
        self.create_label_widgets(centralwidget,
            self.parametersweep_params_Dict, self.parametersweep_widget_Dict)
        self.create_slider_widgets(centralwidget,
            parametersweep_defaults, self.parametersweep_params_Dict, self.parametersweep_widget_Dict)
        self.create_spinBox_widgets(centralwidget,
            parametersweep_defaults, self.parametersweep_params_Dict, self.parametersweep_widget_Dict)

    def create_label_widgets(self, centralwidget, params_Dict, widget_Dict):
        for sweep in params_Dict.keys():
            object_name = sweep + "_label"
            label_value = sweep + " Value:"
            widget_Dict[sweep][object_name] = QtWidgets.QLabel(centralwidget)
            widget_Dict[sweep][object_name].setObjectName(object_name)
            widget_Dict[sweep][object_name].setText(
                QCoreApplication.translate("MainWindow", label_value, None))

    def create_slider_widgets(self, centralwidget, defaults, params_Dict, widget_Dict):
        for sweep, value in params_Dict.items():
            object_name = sweep + "_slider"

            if isinstance(value, int):
                slider_min = defaults[sweep]["min"]
                slider_max = defaults[sweep]["max"]

                widget_Dict[sweep][object_name] = QtWidgets.QSlider(centralwidget)
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

                widget_Dict[sweep][object_name] = FloatSlider(centralwidget)
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

    def create_spinBox_widgets(self, centralwidget, defaults, params_Dict, widget_Dict):
        for sweep, value in params_Dict.items():
            object_name = sweep + "_spinBox"

            if isinstance(value, int):
                slider_min = defaults[sweep]["min"]
                slider_max = defaults[sweep]["max"]

                widget_Dict[sweep][object_name] = QtWidgets.QSpinBox(centralwidget)
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

                widget_Dict[sweep][object_name] = QtWidgets.QDoubleSpinBox(centralwidget)
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

            label_spinBox_layout = QtWidgets.QHBoxLayout()
            label_spinBox_layout.addWidget(sweep_Dict[label_key])
            label_spinBox_layout.addWidget(sweep_Dict[spinBox_key])

            total_layout = QtWidgets.QVBoxLayout()
            total_layout.addLayout(label_spinBox_layout)
            total_layout.addWidget(sweep_Dict[slider_key])
            widget_layout_Dict[sweep] = total_layout
            widget_layout_Dict[sweep].setObjectName(
                layout_object_name)