
from random import randint
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap

import HistoricalDataWindow
import SendSerialWorker

import DistanceDialog
import CalibrationAlertWindow
import pandas as pd
import sys
from datetime import datetime

import TempDialog
import RangeInputDialog

from TempImageGenerator import generate_heatmap

class MainWindowWithRectangle(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.darkGray, 1)
        painter.setPen(pen)
        painter.drawRect(60, 670, 780, 195)  # Adjusted height so it doesn't exceed the dialog size


class Ui_MainWindow(object):

    def setupUi(self, MainWindow, receiveSerialThread, arduino_port):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 900)
        MainWindow.setWindowTitle("CFMS Prototype Controls")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.depth_display = QtWidgets.QLCDNumber(self.centralwidget)
        self.depth_display.setGeometry(QtCore.QRect(1020, 60, 201, 61))
        self.depth_display.setObjectName("depth_display")

        self.motor_speed_display = QtWidgets.QLabel(self.centralwidget)
        self.motor_speed_display.setGeometry(QtCore.QRect(730, 720, 70, 51))
        self.motor_speed_display.setObjectName("motor_speed_display")
        self.motor_speed_display.setStyleSheet("border: 2px solid black;")

        self.speed_font = QtGui.QFont()
        
        self.speed_font.setPointSize(16)
        self.motor_speed_display.setText("0%")
        self.motor_speed_display.setFont(self.speed_font)


        self.motor_speed_slider = QtWidgets.QSlider(self.centralwidget)
        self.motor_speed_slider.setGeometry(QtCore.QRect(85, 730, 611, 31))
        self.motor_speed_slider.setOrientation(QtCore.Qt.Horizontal)
        self.motor_speed_slider.setObjectName("motor_speed_slider")
        self.motor_speed_slider.setMinimum(0)
        self.motor_speed_slider.setMaximum(100)
        self.motor_speed_slider.setValue(0)
        self.motor_speed_slider.valueChanged.connect(self.update_motor_speed)
        
        
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 690, 151, 31))
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(270, 10, 151, 41))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1080, 10, 100, 41))
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.temp_menu_button = QtWidgets.QPushButton(self.centralwidget)
        self.temp_menu_button.setGeometry(QtCore.QRect(230, 565, 270, 51))
        self.temp_menu_button.setObjectName("temp_menu_button")
        self.temp_menu_button.setFont(font)
        self.temp_menu_button.clicked.connect(self.openTempMenu2)

        self.distance_menu_button = QtWidgets.QPushButton(self.centralwidget)
        self.distance_menu_button.setGeometry(QtCore.QRect(1020, 565, 270, 51))
        self.distance_menu_button.setObjectName("distance_menu_button")
        self.distance_menu_button.setFont(font)
        self.distance_menu_button.clicked.connect(self.openDistanceMenu2)

        self.historical_data_button = QtWidgets.QPushButton(self.centralwidget)
        self.historical_data_button.setGeometry(QtCore.QRect(580, 565, 350, 50))
        self.historical_data_button.setObjectName("historical_data_button")
        self.historical_data_button.setFont(font)
        self.historical_data_button.clicked.connect(self.openHistoricalDataMenu)

        self.set_range_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_range_button.setGeometry(QtCore.QRect(930, 650, 390, 50))
        self.set_range_button.setObjectName("set_range_button")
        self.set_range_button.setFont(font)
        self.set_range_button.clicked.connect(self.openRangeInputDialog)
        

        self.calibrate_button = QtWidgets.QPushButton(self.centralwidget)
        self.calibrate_button.setGeometry(QtCore.QRect(930, 710, 390, 50))
        self.calibrate_button.setObjectName("calibrate_button")
        self.calibrate_button.setFont(font)
        self.calibrate_button.clicked.connect(self.calibrate)

        self.calibration_details = QtWidgets.QLabel(self.centralwidget)
        self.calibration_details.setGeometry(QtCore.QRect(960, 760, 250, 31))
        self.calibration_details.setObjectName("calibration_details")

        font.setPointSize(10)

        self.calibrate_details_button = QtWidgets.QPushButton(self.centralwidget)
        self.calibrate_details_button.setGeometry(QtCore.QRect(980, 795, 300, 40))
        self.calibrate_details_button.setObjectName("calibrate_details_button")
        self.calibrate_details_button.setFont(font)
        self.calibrate_details_button.clicked.connect(self.see_calibration_details)

        self.temp_calibration_range = [-999999, 999999]
        self.distance_calibration_range = [-999999, 999999] 
        self.temp_range = [999999, -999999]
        self.distance_range = [999999, -999999]
        self.calibration_count = 0
        self.calibration_mode = False

        self.calibration_details.setFont(self.speed_font)

        font.setPointSize(20)
        font.setBold(True)

        self.motor_stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.motor_stop_button.setGeometry(QtCore.QRect(310, 780, 265, 71))
        self.motor_stop_button.setObjectName("motor_stop_button")
        self.motor_stop_button.setFont(font)
        self.motor_stop_button.clicked.connect(self.stopMotor)
        self.motor_stop_button.setStyleSheet("background-color: red; color: white;")

        font.setPointSize(10)
        self.close_button = QtWidgets.QPushButton(self.centralwidget)
        self.close_button.setGeometry(QtCore.QRect(1320, 830, 145, 45))
        self.close_button.setObjectName("close_button")
        self.close_button.setFont(font)
        self.close_button.clicked.connect(self.closeWindow)
        
        self.temp_map_display = QtWidgets.QLabel(self.centralwidget)
        self.temp_map_display.setGeometry(QtCore.QRect(70, 60, 600, 490))
        self.temp_map_display.setObjectName("temp_map_display")
        self.temp_map_display.setFont(font)
        self.temp_map_display.setStyleSheet("border: 2px solid black;")

        self.temp_image = QPixmap("heatmap.png")
        self.scaled_temp_image = self.temp_image.scaled(600, 560, QtCore.Qt.KeepAspectRatio)
        self.temp_map_display.setPixmap(self.scaled_temp_image)

        self.time = []

        self.small_depth_chart = pg.PlotWidget(self.centralwidget)
        self.small_depth_chart.setBackground("w")
        pen = pg.mkPen(color=(255,0,0))
        self.small_depth_chart.setTitle("Distance", color="k", size="15pt")
        styles = {"color": "black", "font-size": "15px"}
        self.small_depth_chart.setLabel("left", "Distance (cm)", **styles)
        #self.small_depth_chart.setLabel("bottom", "Time (min)", **styles)
        #self.small_depth_chart.addLegend()
        self.small_depth_chart.showGrid(x=True, y=True)
        self.small_depth_chart.setYRange(3, 12)
        self.small_depth_chart.setStyleSheet("border: 2px solid black;")
        
        #self.distance = [60 + ((randint(1, 19) - 10) * 0.1) for _ in range(10)]
        self.distance = []

        self.depth_line = self.small_depth_chart.plot(
            self.time,
            self.distance,
            name="Lidar Sensor",
            pen=pen
        )
        self.small_depth_chart.setGeometry(QtCore.QRect(780, 140, 660, 370))
        self.small_depth_chart.setObjectName("small_depth_chart")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1108, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance", "Distance ROC", "Max Temp", "Avg Temp", "Temp 1", "Temp 2", "Temp 3", "Temp 4", "Temp 5", "Temp 6", "Temp 7"])

        self.is_calibration_check_running = False
        self.temp_cutoff = 999999
        self.distance_cutoff = -1

        self.exp_temp_min = 0
        self.exp_temp_max = 100
        self.exp_dist_min = 0
        self.exp_dist_max = 80
        self.maintenance_needed = False

        self.temp_sections = []
        self.temp_section_alert = False
        self.cold_blocks = []
        self.temp_distribution_threshold = 3.0

        self.receive_serial_thread = receiveSerialThread
        self.receive_serial_thread.start()
        self.receive_serial_thread.data_received.connect(self.update_plot)
        
        self.speed_change_signal = pyqtSignal(float)
        self.send_serial_thread = SendSerialWorker.SendSerialWorker(arduino_port)
        self.send_serial_thread.send_setup()
        
        self.temp_window = None
        self.distance_window = None
        self.alert_window = None

        self.signal_times = []
        self.alert_open = False

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):  
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CFMS Prototype Controls"))
        self.label.setText(_translate("MainWindow", "Motor Speed"))
        self.label_2.setText(_translate("MainWindow", "Temperature"))
        self.label_3.setText(_translate("MainWindow", "Distance"))
        self.temp_menu_button.setText(_translate("MainWindow", "Temperature Details"))
        self.distance_menu_button.setText(_translate("MainWindow", "Distance Details"))
        self.motor_stop_button.setText(_translate("MainWindow", "STOP MOTOR"))
        self.close_button.setText(_translate("MainWindow", "Quit"))
        self.historical_data_button.setText(_translate("MainWindow", "Historical Data"))
        self.calibrate_button.setText(_translate("MainWindow", "Auto Calibrate"))
        self.calibrate_details_button.setText(_translate("MainWindow", "Calibration Details"))
        self.set_range_button.setText(_translate("MainWindow", "Set Normal Range"))
        

    def update_plot(self, data: pd.DataFrame):
        #Move least recent reading off graph
        if (len(self.time) > 19):

            if (len(self.time) > 20):
                self.time = self.time[-20:]
                self.temperature = self.temperature[-20:]

            self.time = self.time[1:]
            self.distance = self.distance[1:]

        #self.checkCutoffValue(data)
        generate_heatmap(data["Temp"].iloc[-1])

        self.time.append(data["Time"].iloc[-1])
        
        self.distance.append(data["Distance"].iloc[-1])


        #Redraw line
        self.depth_line.setData(list(range(1, len(self.time) + 1)), self.distance)
        min_range, max_range = self.calculate_distance_y_range()
        self.small_depth_chart.setYRange(min_range, max_range)
        self.depth_display.display(self.distance[-1])

        self.temp_image = QPixmap("heatmap.png")
        self.scaled_temp_image = self.temp_image.scaled(600, 560, QtCore.Qt.KeepAspectRatio)
        self.temp_map_display.setPixmap(self.scaled_temp_image)

        self.df = pd.concat([self.df, data], ignore_index=True)
        
        self.checkCalibrationRange()
 
        if (self.calibration_mode):
            self.calibration_count += 1
            
            if (self.calibration_count < 15):
            
                min_temp = float(np.min(self.df["Temp"].iloc[-1]))
                max_temp = float(np.max(self.df["Temp"].iloc[-1]))

                if (min_temp < self.temp_range[0]):
                    self.temp_range[0] = min_temp
                if (max_temp > self.temp_range[1]):
                    self.temp_range[1] = max_temp

                if (float(self.df["Distance"].iloc[-1]) < self.distance_range[0]):
                    self.distance_range[0] = float(self.df["Distance"].iloc[-1])
                if (float(self.df["Distance"].iloc[-1]) > self.distance_range[1]):
                    self.distance_range[1] = float(self.df["Distance"].iloc[-1])

            elif (self.calibration_count == 15):

                distance_buffer = (self.distance_range[1] - self.distance_range[0]) * 0.25
                temp_buffer = (self.temp_range[1] - self.temp_range[0]) * 0.25

                self.temp_calibration_range = [self.temp_range[0] - temp_buffer, self.temp_range[1] + temp_buffer]
                self.distance_calibration_range = [self.distance_range[0] - distance_buffer, self.distance_range[1] + distance_buffer]

                self.calibration_details.setText("Calibrated!")

            elif (self.calibration_count > 17):

                self.calibration_details.setText("")
                self.calibration_count = 0
                self.calibration_mode = False

                print(self.temp_calibration_range)
                print(self.distance_calibration_range)

        

        self.signal_times.append(time.time())

    def calculate_distance_y_range(self):
        recent_readings = []

        if len(self.distance) > 20:
            recent_readings = self.distance[-20:]
        else:
            recent_readings = self.distance

        min_distance = min(recent_readings)
        max_distance = max(recent_readings)
        range = max(max_distance - min_distance, 2)

        min_range = max(min_distance - (0.15 * range), 0)
        max_range = max_distance + (0.15 * range)

        return (min_range, max_range)
    
    def checkCalibrationRange(self):

        if (not(self.is_calibration_check_running)):
            self.is_calibration_check_running = True

            if (self.maintenance_needed):
                expected_ranges_alert = False
            else:
                expected_ranges_alert = self.checkExpectedRanges()
            cutoff_alert = self.checkCutoffValue()
            
            if (not(expected_ranges_alert or cutoff_alert)):
                
                if (self.alert_open == False):
                    min_temp = float(np.min(self.df["Temp"].iloc[-1]))
                    max_temp = float(np.max(self.df["Temp"].iloc[-1]))

                    if (min_temp < self.temp_calibration_range[0]):
                        self.alert_open = True
                        self.alert_window = CalibrationAlertWindow.Ui_AlertWindow(self, "temp", self.temp_calibration_range, min_temp)
                        
                    elif (max_temp > self.temp_calibration_range[1]):
                        self.alert_open = True
                        self.alert_window = CalibrationAlertWindow.Ui_AlertWindow(self, "temp", self.temp_calibration_range, max_temp)
                        
                    elif ((float(self.df["Distance"].iloc[-1]) < self.distance_calibration_range[0] or 
                        float(self.df["Distance"].iloc[-1]) > self.distance_calibration_range[1]) and self.temp_sections == []):
                        self.alert_open = True
                        self.alert_window = CalibrationAlertWindow.Ui_AlertWindow(self, "distance", self.distance_calibration_range, float(self.df["Distance"].iloc[-1]))

                    elif (self.temp_sections != [] and self.temp_section_alert == False):
                        self.cold_blocks = self.find_cold_spots_in_grid(self.df["Temp"].iloc[-1], self.temp_sections, self.temp_distribution_threshold)
                        
            self.is_calibration_check_running = False

    def checkExpectedRanges(self):
        if (float(np.max(self.df["Temp"].iloc[-1])) > float(self.exp_temp_max)):

            self.unexpected_temp_alert = QMessageBox()
            self.unexpected_temp_alert.setWindowTitle("Unexpected Temperature Details")
            
            self.unexpected_temp_alert.setText(f"System requires maintenance!\n\nThe temperature reading: {float(np.max(self.df['Temp'].iloc[-1])):.2f}°C is outside of the normal range.\nPlease visit the expected ranges menu when maintenance is complete.")
            
            self.unexpected_temp_alert.setStandardButtons(QMessageBox.Ok)
            self.unexpected_temp_alert.exec_()

            self.maintenance_needed = True
            self.set_range_button.setStyleSheet("background-color: red; color: white;")

        elif (float(np.min(self.df["Temp"].iloc[-1])) < float(self.exp_temp_min)):
            self.unexpected_temp_alert = QMessageBox()
            self.unexpected_temp_alert.setWindowTitle("Unexpected Temperature Details")
            
            self.unexpected_temp_alert.setText(f"System requires maintenance!\n\nThe temperature reading: {float(np.min(self.df['Temp'].iloc[-1])):.2f}°C is outside of the normal range.\nPlease visit the expected ranges menu when maintenance is complete.")
            
            self.unexpected_temp_alert.setStandardButtons(QMessageBox.Ok)
            self.unexpected_temp_alert.exec_()

            self.maintenance_needed = True
            self.set_range_button.setStyleSheet("background-color: red; color: white;")

        elif (float(self.df["Distance"].iloc[-1]) > float(self.exp_dist_max) or float(self.df["Distance"].iloc[-1]) < float(self.exp_dist_min)):

            self.unexpected_dist_alert = QMessageBox()
            self.unexpected_dist_alert.setWindowTitle("Unexpected Distance Details")

            self.unexpected_dist_alert.setText(f"System requires maintenance!\n\nThe distance reading: {float(self.df['Distance'].iloc[-1]):.2f}cm is outside of the normal range.\nPlease visit the expected ranges menu when maintenance is complete.")

            self.unexpected_dist_alert.setStandardButtons(QMessageBox.Ok)
            self.unexpected_dist_alert.exec_()

            self.maintenance_needed = True
            self.set_range_button.setStyleSheet("background-color: red; color: white;")

        return self.maintenance_needed

    def checkCutoffValue(self):
        alert = False
        if (float(np.max(self.df["Temp"].iloc[-1])) >= float(self.temp_cutoff)):

            self.stopMotor()

            self.estop_msg = QMessageBox()
            self.estop_msg.setWindowTitle("Emergency Stop Details")
            
            self.estop_msg.setText(f"Emergency Stop Triggered!\n\nMax Temperature: {float(np.max(self.df['Temp'].iloc[-1])):.2f}°C\nTemperature Cutoff: {self.temp_cutoff:.2f}°C")
            
            self.estop_msg.setStandardButtons(QMessageBox.Ok)
            self.estop_msg.exec_()
            alert = True  
            self.temp_cutoff = 999999

        elif (float(self.df["Distance"].iloc[-1]) < float(self.distance_cutoff)):
            self.stopMotor()

            self.estop_msg = QMessageBox()
            self.estop_msg.setWindowTitle("Emergency Stop Details")

            self.estop_msg.setText(f"Emergency Stop Triggered!\n\nDistance: {float(self.df['Distance'].iloc[-1]):.2f}cm\nDistance Cutoff: {self.distance_cutoff:.2f}cm")

            self.estop_msg.setStandardButtons(QMessageBox.Ok)
            self.estop_msg.exec_()
            alert = True
            self.distance_cutoff = -1

        return alert
    
    def find_cold_spots_in_grid(self, temp_array, selected_blocks, threshold = 3.0):
    
        # Finds significantly colder blocks in a selected subset of an 8x8 grid
        # over a 32x24 temperature array.

        # Parameters:
        #     temp_array (np.ndarray): A 2D NumPy array of shape (24, 32).
        #     selected_blocks (List[Tuple[int, int]]): List of (row, col) blocks selected from 8x8 grid.
        #     threshold (float): Minimum temperature difference to be considered significantly colder.

        # Returns:
        #     List[Tuple[int, int]]: List of blocks that are significantly colder (minority).
        
        assert temp_array.shape == (24, 32), "Temperature array must be 24 rows by 32 columns."

        grid_rows, grid_cols = 8, 8
        block_height = temp_array.shape[0] // grid_rows  # 24 // 8 = 3
        block_width = temp_array.shape[1] // grid_cols   # 32 // 8 = 4

        block_avgs = []

        for (row, col) in selected_blocks:
            y_start = row * block_height
            y_end = y_start + block_height
            x_start = col * block_width
            x_end = x_start + block_width

            block = temp_array[y_start:y_end, x_start:x_end]
            block_avg = np.mean(block)
            block_avgs.append(((row, col), block_avg))

        # Calculate overall average of selected blocks
        avg_temps = [b[1] for b in block_avgs]
        overall_avg = np.mean(avg_temps)

        # Identify significantly colder blocks
        cold_blocks = [
            b[0] for b in block_avgs
            if (overall_avg - b[1]) >= threshold
        ]

        # Only return them if they are a minority
        if (len(cold_blocks) < len(selected_blocks) / 2) and len(cold_blocks) > 0:
            self.temp_section_msg = QMessageBox()
            self.temp_section_msg.setWindowTitle("Temperature Drop Alert")

            self.temp_section_msg.setText(f"A part of your selected temperature section is colder than the rest.\n\nPlease see the temperature details menu for more information.")

            self.temp_section_msg.setStandardButtons(QMessageBox.Ok)
            self.temp_section_msg.exec_()

            self.temp_section_alert = True
            self.temp_menu_button.setStyleSheet("background-color: red; color: white;")
            self.temp_image.save("temp_section_alert.png")

            print("Cold blocks:", cold_blocks)
            return cold_blocks
        else:
            return []  # If they're the majority, don't consider it meaningful

    def setTempCutoffValue(self, value):
        self.temp_cutoff = float(value)

    def setDistanceCutoffValue(self, value):
        self.distance_cutoff = float(value)

    def update_motor_speed(self, value):
        # Send motor speed value to Arduino
        self.motor_speed_display.setText(str(value) + "%")
        if self.send_serial_thread:
            speed_data = float(value) / 100
            self.send_serial_thread.send_data(str(round(speed_data, 2)))

    def calibrate(self):
        self.calibration_details.setText("Calibrating...")

        self.calibration_mode = True

    def manually_calibrate(self, metric, range: list):
        if (metric == "temp"):
            self.temp_calibration_range = range
            self.alert_window = None

            print(self.temp_calibration_range) 
        elif (metric == "distance"):
            self.distance_calibration_range = range
            self.alert_window = None

            print(self.distance_calibration_range)

    def set_alert_state(self, state):
        self.alert_open = state
        
    def see_calibration_details(self):
        self.calibration_details_msg = QMessageBox()
        self.calibration_details_msg.setWindowTitle("Calibration Details")
        
        if (self.temp_calibration_range[0] == -999999):
            self.calibration_details_msg.setText("System is not calibrated.")
        else:
            self.calibration_details_msg.setText(f"Temperature Calibration Range: {self.temp_calibration_range[0]:.2f} - {self.temp_calibration_range[1]:.2f}\nDistance Calibration Range: {self.distance_calibration_range[0]} - {self.distance_calibration_range[1]}")
        
        self.calibration_details_msg.setStandardButtons(QMessageBox.Ok)
        self.calibration_details_msg.exec_()

    def openTempMenu2(self):
        
        self.temp_window = TempDialog.Ui_TempDetails(self, self.df)
        self.receive_serial_thread.data_received.connect(self.temp_window.update_data)
        
    def openHistoricalDataMenu(self):  
        self.historical_window = HistoricalDataWindow.Ui_HistoricalData(self)
    
    def openDistanceMenu2(self):
        
            self.distance_window = DistanceDialog.Ui_DistanceDetails(self, self.df)
            self.receive_serial_thread.data_received.connect(self.distance_window.update_data)

    def openRangeInputDialog(self):
        self.range_input = RangeInputDialog.RangeInputDialog(self)

    def setExpectedRanges(self, ranges):
        self.exp_temp_min = ranges["temp_min"]
        self.exp_temp_max = ranges["temp_max"]
        self.exp_dist_min = ranges["dist_min"]
        self.exp_dist_max = ranges["dist_max"]

    def setMaintenanceComplete(self):
        self.maintenance_needed = False
        self.set_range_button.setStyleSheet("background-color: white; color: black;")

    def closeEvent(self, event):
        self.serial_thread.stop()
        event.accept()
    
    def stopMotor(self):

        self.send_serial_thread.send_data("stop")
        self.motor_speed_slider.setValue(0)
        self.motor_speed_display.setText("0%")

    def setTempSections(self, sections: list):
        self.temp_sections = sections

    def get_cold_blocks(self):
        return self.cold_blocks
    
    def set_cold_blocks(self, cold_blocks: list):
        self.cold_blocks = cold_blocks

    def get_temp_section_alert(self):
        return self.temp_section_alert
    
    def clearTempSectionsAlert(self):
        self.temp_section_alert = False
        self.temp_menu_button.setStyleSheet("background-color: white; color: black;")

    def getTempDistributionThreshold(self):
        return self.temp_distribution_threshold
    
    def setTempDistributionThreshold(self, threshold):
        self.temp_distribution_threshold = threshold
        print(self.temp_distribution_threshold)

    def __init__(self, receiveSerialThread, arduino_port):
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)
        
        self.MainWindow = MainWindowWithRectangle()
        
        self.setupUi(self.MainWindow, receiveSerialThread, arduino_port)
        self.MainWindow.show()
        sys.exit(self.app.exec_())

    def closeWindow(self):
        self.send_serial_thread.send_data("stop")

        # Calculate the differences between consecutive time values
        time_differences = [t2 - t1 for t1, t2 in zip(self.signal_times[:-1], self.signal_times[1:])]

        # Compute the average of these differences
        average_difference = sum(time_differences) / len(time_differences) if time_differences else 0

        print("Average difference:", average_difference)
        print("Number of readings:", len(self.signal_times))

        sys.exit(self.app.exec_())

