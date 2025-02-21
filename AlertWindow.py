import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import MainWindow

class Ui_AlertWindow(object):

    def __init__(self, main_window, metric, range, value):
        super().__init__()
        self.AlertWindow = QtWidgets.QDialog()
        self.setupUi(self.AlertWindow, main_window, metric, range, value)
        self.AlertWindow.setModal(True)
        self.AlertWindow.exec_()
    
    def setupUi(self, AlertWindow, mainWindow, metric, range, value):
        self.main_window = mainWindow
        AlertWindow.setObjectName("AlertWindow")
        AlertWindow.resize(600, 300)
        self.alert_window = AlertWindow

        self.metric = metric
        self.range = range
        self.value = value

        self.stop_button = QtWidgets.QPushButton(AlertWindow)
        self.stop_button.setGeometry(QtCore.QRect(40, 260, 121, 31))
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.stopSystem)

        self.adjust_range_button = QtWidgets.QPushButton(AlertWindow)
        self.adjust_range_button.setGeometry(QtCore.QRect(200, 260, 121, 31))
        self.adjust_range_button.setObjectName("adjust_range_button")
        self.adjust_range_button.clicked.connect(self.adjustRange)

        self.calibration_off_button = QtWidgets.QPushButton(AlertWindow)
        self.calibration_off_button.setGeometry(QtCore.QRect(350, 260, 121, 31))
        self.calibration_off_button.setObjectName("calibration_off_button")
        self.calibration_off_button.clicked.connect(self.turnCalibrationOff)

        font = QtGui.QFont()
        font.setFamily("Cambria")
        font.setPointSize(14)

        self.details_text = QtWidgets.QLabel(AlertWindow)
        self.details_text.setGeometry(QtCore.QRect(20, 20, 450, 200))
        self.details_text.setObjectName("details_text")

        if (self.value < self.range[0]):
            difference = self.range[0] - self.value
        else:
            difference = self.value - self.range[1]

        if (self.metric == "Temperature"):
            unit = "°C"
        else:
            unit = "cm"

        text = f"ALERT: {self.metric} readings are abnormal!\n\n{self.metric} was read as {self.value}, {difference:.2f} {unit} outside the range of {self.range[0]} to {self.range[1]}.\n\nHow would you like to resolve this issue?"

        self.details_text.setText(text)
        self.details_text.setFont(font)
        self.details_text.setWordWrap(True)

        self.retranslateUi(AlertWindow)
        QtCore.QMetaObject.connectSlotsByName(AlertWindow)

    def retranslateUi(self, AlertWindow):
        _translate = QtCore.QCoreApplication.translate
        AlertWindow.setWindowTitle(_translate("AlertWindow", "Dialog"))
        self.stop_button.setText(_translate("AlertWindow", "Stop System"))
        self.adjust_range_button.setText(_translate("AlertWindow", "Expand Calibration Range"))
        self.calibration_off_button.setText(_translate("AlertWindow", "Turn Calibration Off"))

    def stopSystem(self):
        self.alert_window.close()
        return
    
    def adjustRange(self):
        min_value = self.range[0]
        max_value = self.range[1]

        if (self.value < self.range[0]):
            min_value = self.value - (self.range[0] - self.value) * 0.5
        else:
            max_value = self.value + (self.value - self.range[1]) * 0.5
        
        MainWindow.Ui_MainWindow.manually_calibrate(self.main_window, self.metric, [min_value, max_value])
        self.alert_window.close()

    def turnCalibrationOff(self):
        MainWindow.Ui_MainWindow.manually_calibrate(self.main_window, self.metric, [-999999, 999999])
        self.alert_window.close()

    def closeWindow(self):
        self.alert_window.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    AlertWindow = QtWidgets.QDialog()
    emptydf = pd.DataFrame(columns= ["Time", "Temp", "Distance"])
    ui = Ui_AlertWindow(emptydf)

    sys.exit(app.exec_())
