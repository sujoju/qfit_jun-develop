from inspect import currentframe
import sys

from PySide2 import QtWidgets

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import numpy as np
import scqubits as scq
from parametersweep_eg import ParameterSweep_EG
from parametersweep_ui_elements import ParameterSweep_UI_Elements
from floatslider import FloatSlider
import random
from eg8_ui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.parametersweep_main = ParameterSweep_EG()
        self.parametersweep = self.parametersweep_main.parametersweep
        self.current_sweep = list(self.parametersweep.param_info.keys())[0]
        self.parametersweep_ui_elements = ParameterSweep_UI_Elements(self.parametersweep, self.centralwidget)

        self.disable_current_sweep()
        self.disable_parameters()

        self.create_param_layout()
        self.create_subsys_layout()

        self.connect_widgets()

        self.update_plot()

        self.show()

    def get_subsys_params(self):
        param_list = []
        for subsys in self.parametersweep.hilbertspace.subsystem_list:
            param_list.append(subsys.get_initdata())
        return param_list

    def get_rand_params(self):
        rand_params =()

        for param_dict in self.parametersweep.param_info.values():
            min = param_dict[0]
            max = param_dict[-1]
            rand_params += (round(random.uniform(min, max), 2), )
        return rand_params

    def get_changed_params(self, original_copy, new_copy):
        changed_params = {}
        for i in range(0, len(original_copy)):
            subsys = original_copy[i]["id_str"]
            changed_params[subsys] = []
            for param, param_val in original_copy[i].items():
                if new_copy[i][param] != param_val:
                    changed_params[subsys].append(param)
            if len(changed_params[subsys]) == 0:
                del changed_params[subsys]
        return changed_params

    #STILL NEED TO UPDATE THE GRAYED OUT VALUES AS YOU CHANGE PARAMS
    def disable_parameters(self):
        original_copy = self.get_subsys_params()
        self.parametersweep_main.update_hilbertspace(*self.get_rand_params())
        new_copy = self.get_subsys_params()

        changed_params = self.get_changed_params(original_copy, new_copy)
        for subsys, param_list in changed_params.items():
            for i in range(0, len(param_list)):
                param = param_list[i]
                spinBox_key = param + "_spinBox"
                slider_key = param + "_slider"
                self.parametersweep_ui_elements.subsys_widget_Dict[subsys][param][slider_key].setEnabled(False)
                self.parametersweep_ui_elements.subsys_widget_Dict[subsys][param][spinBox_key].setEnabled(False)

    def get_current_values(self, tab_index):
        current_values_Dict = {}
        tab_name = self.parametersweepTabWidget.tabText(tab_index)
        if tab_name == "Parameters":
            for sweep in self.parametersweep_ui_elements.parametersweep_widget_Dict.keys():
                spinBox_key = sweep + "_spinBox"
                spinBox = self.parametersweep_ui_elements.parametersweep_widget_Dict[sweep][spinBox_key]

                current_values_Dict[sweep] = spinBox.value(
                )
        else:
            for param in self.parametersweep_ui_elements.subsys_widget_Dict[tab_name].keys():
                spinBox_key = param + "_spinBox"
                spinBox = self.parametersweep_ui_elements.subsys_widget_Dict[tab_name][param][spinBox_key]

                current_values_Dict[param] = spinBox.value(
                )

        return current_values_Dict

    def create_param_layout(self):
        total_layout = QVBoxLayout()
        for sweep, layout in self.parametersweep_ui_elements.parametersweep_widget_layout_Dict.items():
            total_layout.addLayout(layout)
            self.sweep_comboBox.addItem(sweep)

        self.parameters_tab.setLayout(total_layout)

    def create_subsys_layout(self):
        for subsys, subsys_Dict in self.parametersweep_ui_elements.subsys_widget_layout_Dict.items():
            total_layout = QVBoxLayout()
            subsys_tab_name = subsys + "_tab"
            subsys_tab = QWidget()
            subsys_tab.setObjectName(subsys_tab_name)

            for param, layout in subsys_Dict.items():
                total_layout.addLayout(layout)

            subsys_tab.setLayout(total_layout)
            self.parametersweepTabWidget.addTab(subsys_tab, subsys)

    def connect_param_slider_spinBox(self, widget_Dict):
        for sweep in widget_Dict.keys():
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

            if widget_Dict == self.parametersweep_ui_elements.parametersweep_widget_Dict:
                slider.sliderReleased.connect(self.update_plot)
                spinBox.editingFinished.connect(self.update_plot)
            else:
                slider.sliderReleased.connect(self.update_subsys_params_Dict)
                spinBox.editingFinished.connect(self.update_subsys_params_Dict)

    def disable_current_sweep(self):
        slider_object_name = self.current_sweep + "_slider"
        spinBox_object_name = self.current_sweep + "_spinBox"
        self.parametersweep_ui_elements.parametersweep_widget_Dict[self.current_sweep][slider_object_name].setEnabled(False)
        self.parametersweep_ui_elements.parametersweep_widget_Dict[self.current_sweep][spinBox_object_name].setEnabled(False)

    def connect_widgets(self):
        self.sweep_comboBox.currentTextChanged.connect(
            self.adjust_enabled_sweep)
        self.sweep_comboBox.currentTextChanged.connect(self.update_plot)
        self.show_data_checkBox.stateChanged.connect(self.update_plot)
        self.updateParameterSweepButton.clicked.connect(
            self.update_parametersweep)
        self.fitButton.clicked.connect(self.fit_plot)
        self.parametersweepTabWidget.currentChanged.connect(self.adjust_disabled_params)

        self.connect_param_slider_spinBox(self.parametersweep_ui_elements.parametersweep_widget_Dict)
        for subsys, subsys_Dict in self.parametersweep_ui_elements.subsys_widget_Dict.items():
            self.connect_param_slider_spinBox(subsys_Dict)

    #This is not needed for single parameter parametersweeps
    def adjust_disabled_params(self):
        pass

    def adjust_enabled_sweep(self, new_sweep):
        for sweep in self.parametersweep_ui_elements.parametersweep_widget_Dict.keys():
            spinBox_key = sweep + "_spinBox"
            slider_key = sweep + "_slider"

            slider = self.parametersweep_ui_elements.parametersweep_widget_Dict[sweep][slider_key]
            spinBox = self.parametersweep_ui_elements.parametersweep_widget_Dict[sweep][spinBox_key]

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
            self.parametersweep, self.current_sweep, current_values, show_data_tf, self.parametersweep_main.noisy_data)

    def update_subsys_params_Dict(self):
        total_tabs = self.parametersweepTabWidget.count()
        for tab_index in range(1, total_tabs, 1):
            current_values = self.get_current_values(tab_index)
            tab_name = self.parametersweepTabWidget.tabText(tab_index)
            for param, param_val in current_values.items():
                self.parametersweep_ui_elements.subsys_params_Dict[tab_name][param] = param_val

    def update_parametersweep(self):
        evals = self.evals_count_spinBox.value()
        self.parametersweep_main.create_hilbertspace(self.parametersweep_ui_elements.subsys_params_Dict)
        self.parametersweep_main.create_parametersweep(evals)
        self.parametersweep = self.parametersweep_main.parametersweep
        self.update_plot()

    def fit_plot(self):
        current_values = self.get_current_values(0)
        current_sweep_Dict = {}
        for param, param_val in current_values.items():
            current_sweep_Dict[param] = {
                "min": self.parametersweep.param_info[param][0],
                "max": self.parametersweep.param_info[param][-1],
                "value": param_val
            }
        fit_report = self.mplFigureCanvas.fit_parametersweep(
            self.parametersweep, self.current_sweep, current_sweep_Dict, self.parametersweep_main.noisy_data)
        QMessageBox.information(self, "Fit Report", fit_report)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
