import datetime
from datetime import datetime
import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from scipy.ndimage import gaussian_filter
import numpy as np
import random

import serial
from db import get_db, readings_table, temp_arrays_table
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

class DistanceSerialWorker(QThread):
    data_received = pyqtSignal(pd.DataFrame)  # Signal to send data to the GUI

    def __init__(self):
        super().__init__()
        self.running = True
        self.port = "COM5"
        self.baudrate = 9600
    
    
    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        ser.setDTR(False)
        time.sleep(1)
        ser.flushInput()
        ser.setDTR(True)
        
        self.df = pd.DataFrame(columns= ["Time", "Distance"])
        # temp_data = self.generate_temp_frame()

        line = ''
        temp_array = []

        try:

            while line == '':
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            while self.running:
                
                data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), float(line)]
                self.df.loc[len(self.df)] = [data[0], data[1]]
                
                self.data_received.emit(self.df.iloc[-1:])

                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            ser.close()

        except serial.SerialException as e:
            print(f"Error: {e}")

    def stop(self):
        self.running = False
        self.wait()

