# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'eg8_ui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from mplfigurecanvas import MplFigureCanvas


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mplFigureCanvas = MplFigureCanvas(self.centralwidget)
        self.mplFigureCanvas.setObjectName(u"mplFigureCanvas")
        self.mplFigureCanvas.setGeometry(QRect(275, 40, 500, 500))
        self.sweep_comboBox = QComboBox(self.centralwidget)
        self.sweep_comboBox.setObjectName(u"sweep_comboBox")
        self.sweep_comboBox.setGeometry(QRect(170, 380, 50, 20))
        self.sweep_comboBox.setEditable(False)
        self.sweep_label = QLabel(self.centralwidget)
        self.sweep_label.setObjectName(u"sweep_label")
        self.sweep_label.setGeometry(QRect(20, 380, 100, 20))
        self.show_data_checkBox = QCheckBox(self.centralwidget)
        self.show_data_checkBox.setObjectName(u"show_data_checkBox")
        self.show_data_checkBox.setGeometry(QRect(20, 420, 150, 17))
        self.show_data_checkBox.setChecked(True)
        self.parametersweepTabWidget = QTabWidget(self.centralwidget)
        self.parametersweepTabWidget.setObjectName(u"parametersweepTabWidget")
        self.parametersweepTabWidget.setGeometry(QRect(20, 40, 231, 331))
        self.parameters_tab = QWidget()
        self.parameters_tab.setObjectName(u"parameters_tab")
        self.parametersweepTabWidget.addTab(self.parameters_tab, "")
        self.updateParameterSweepButton = QPushButton(self.centralwidget)
        self.updateParameterSweepButton.setObjectName(u"updateParameterSweepButton")
        self.updateParameterSweepButton.setGeometry(QRect(50, 520, 160, 20))
        self.fitButton = QPushButton(self.centralwidget)
        self.fitButton.setObjectName(u"fitButton")
        self.fitButton.setGeometry(QRect(170, 420, 50, 20))
        self.evals_count_label = QLabel(self.centralwidget)
        self.evals_count_label.setObjectName(u"evals_count_label")
        self.evals_count_label.setGeometry(QRect(20, 450, 100, 20))
        self.evals_count_slider = QSlider(self.centralwidget)
        self.evals_count_slider.setObjectName(u"evals_count_slider")
        self.evals_count_slider.setGeometry(QRect(20, 480, 200, 20))
        self.evals_count_slider.setMinimum(1)
        self.evals_count_slider.setMaximum(20)
        self.evals_count_slider.setSingleStep(1)
        self.evals_count_slider.setValue(5)
        self.evals_count_slider.setSliderPosition(5)
        self.evals_count_slider.setOrientation(Qt.Horizontal)
        self.evals_count_slider.setTickInterval(0)
        self.evals_count_spinBox = QSpinBox(self.centralwidget)
        self.evals_count_spinBox.setObjectName(u"evals_count_spinBox")
        self.evals_count_spinBox.setGeometry(QRect(170, 450, 50, 20))
        self.evals_count_spinBox.setMinimum(1)
        self.evals_count_spinBox.setMaximum(20)
        self.evals_count_spinBox.setValue(5)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.evals_count_slider.valueChanged.connect(self.evals_count_spinBox.setValue)
        self.evals_count_spinBox.valueChanged.connect(self.evals_count_slider.setValue)

        self.sweep_comboBox.setCurrentIndex(-1)
        self.parametersweepTabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MatPlotLib Example", None))
        self.sweep_label.setText(QCoreApplication.translate("MainWindow", u"Sweep Parameter:", None))
        self.show_data_checkBox.setText(QCoreApplication.translate("MainWindow", u"Show Noisy Data", None))
        self.parametersweepTabWidget.setTabText(self.parametersweepTabWidget.indexOf(self.parameters_tab), QCoreApplication.translate("MainWindow", u"Parameters", None))
        self.updateParameterSweepButton.setText(QCoreApplication.translate("MainWindow", u"Update ParameterSweep", None))
        self.fitButton.setText(QCoreApplication.translate("MainWindow", u"Fit", None))
        self.evals_count_label.setText(QCoreApplication.translate("MainWindow", u"Eigenvalues:", None))
    # retranslateUi

