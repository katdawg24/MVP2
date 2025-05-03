import datetime
from datetime import datetime
import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from scipy.ndimage import gaussian_filter
import numpy as np
import random
import TempImageGenerator
import serial
from db import get_db, readings_table, temp_arrays_table
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

class DistanceNoTempSerialWorker(QThread):
    data_received = pyqtSignal(pd.DataFrame)  # Signal to send data to the GUI

    def __init__(self):
        super().__init__()
        self.running = True
        self.port = "COM7"
        self.baudrate = 9600

    def generate_temp_frame(self, previous_frame=None, shape=(24, 32), base_temp=30, temp_variation=10, smoothness=2):
        """
        Generates a smooth temperature array for infrared visualization.
        If a previous frame is provided, generates a new frame with gradual transitions.
        """
        if previous_frame is None:
            temp_data = np.random.uniform(base_temp - temp_variation, base_temp + temp_variation, shape)
        else:
            temp_data = previous_frame + np.random.uniform(-1, 1, shape)  # Small variations from previous frame

        temp_data = gaussian_filter(temp_data, sigma=smoothness)  # Apply Gaussian smoothing
        
        return temp_data
    
    def update_data_frame(self, data):
        temp_array = np.array(data[1]) 

        avg_temp = np.mean(data[1])
        max_temp = np.max(data[1])

        temp_1 = float(np.mean(np.mean(temp_array[:, :4], axis=0)))
        temp_2 = float(np.mean(np.mean(temp_array[:, 4:8], axis=0)))
        temp_3 = float(np.mean(np.mean(temp_array[:, 8:13], axis=0)))
        temp_4 = float(np.mean(np.mean(temp_array[:, 13:19], axis=0)))
        temp_5 = float(np.mean(np.mean(temp_array[:, 19:24], axis=0)))
        temp_6 = float(np.mean(np.mean(temp_array[:, 24:28], axis=0)))
        temp_7 = float(np.mean(np.mean(temp_array[:, 28:32], axis=0)))

        self.df.loc[len(self.df)] = [data[0], data[1], float(data[2]), max_temp, avg_temp, temp_1, temp_2, temp_3, temp_4, temp_5, temp_6, temp_7]
    
    
    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        ser.setDTR(False)
        time.sleep(0.5)
        ser.flushInput()
        ser.setDTR(True)
        
        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance", "Max Temp", "Avg Temp", "Temp 1", "Temp 2", "Temp 3", "Temp 4", "Temp 5", "Temp 6", "Temp 7"])
        
        line = ''
        
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()

            while line == '':
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            while self.running:
                temp_array = self.generate_temp_frame()
                data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), temp_array,  float(line)]
                self.update_data_frame(data)
                # TempImageGenerator.generate_heatmap(temp_array)
                self.data_received.emit(self.df.iloc[-1:])
                time.sleep(0.3)

                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            ser.close()

        except serial.SerialException as e:
            print(f"Error: {e}")

    def stop(self):
        self.running = False
        self.wait()

