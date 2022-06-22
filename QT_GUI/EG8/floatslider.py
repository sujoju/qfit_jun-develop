from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, Signal, Slot

class FloatSlider(QtWidgets.QSlider):
    intToDouble = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.valueChanged.connect(self.intToDoubleMethod)

    def intToDoubleMethod(self):
        sliderValue = self.value()
        doubleValue = float(sliderValue/100)
        self.intToDouble.emit(doubleValue)

    @Slot(float)
    def doubleToInt(self, floatValue):
        sliderValue = int(100*floatValue)
        self.setValue(sliderValue)