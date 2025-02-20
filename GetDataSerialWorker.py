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

class GetDataSerialWorker(QThread):
    data_received = pyqtSignal(pd.DataFrame)  # Signal to send data to the GUI

    def __init__(self):
        super().__init__()
        self.running = True
        self.port = "COM4"
        self.baudrate = 115200
        
        self.db = next(get_db())
    
    
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

    def store_data(self, data: pd.DataFrame):
        # Convert DataFrame rows into dictionary format
        last_row = data.iloc[-1]

        time = datetime.strptime(last_row["Time"], "%Y-%m-%d %H:%M:%S")

        insert_data = {
            "time": time,
            "distance": float(last_row["Distance"]),
            "max_temp": float(last_row["Max Temp"]),
            "avg_temp": float(last_row["Avg Temp"])
        }
    
        # Insert into table
        insert_query = readings_table.insert().values(insert_data).returning(readings_table.c.id)
        reading_id = self.db.execute(insert_query).scalar()
        
        insert_data.clear()

        for row_index, row in enumerate(last_row["Temp"], start=1):
            insert_data = {"row_index": row_index,
                           "reading_id": reading_id}  # Start with row_index
            for col_index, value in enumerate(row):
                insert_data[f"column_{col_index + 1}"] = float(value)  # column_1 to column_32

            self.db.execute(temp_arrays_table.insert().values(insert_data))

        self.db.commit()

    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        ser.setDTR(False)
        time.sleep(1)
        ser.flushInput()
        ser.setDTR(True)
        
        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance", "Max Temp", "Avg Temp", "Temp 1", "Temp 2", "Temp 3", "Temp 4", "Temp 5", "Temp 6", "Temp 7"])
        # temp_data = self.generate_temp_frame()

        line = ''
        temp_array = []

        try:
        
            while line != 'done':
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()

            while self.running:
                while line != "done":
                    values = [float(x) for x in line[:-1].split(",")]
                    temp_array.append(values)
                    
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()

                
                data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), np.array(temp_array), random.randint(50, 100) / 10.0]
                self.update_data_frame(data)
                self.store_data(self.df)
                self.data_received.emit(self.df.iloc[-1:])
                temp_array.clear()

                if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()

            ser.close()

        except serial.SerialException as e:
            print(f"Error: {e}")

    def stop(self):
        self.running = False
        self.wait()

# generator = TestDataSerialWorker()
# temp_data = generator.generate_temp_frame()
# print(temp_data)  # For demonstration, replace with appropriate visualization or storage logic
# time.sleep(1)
# for _ in range(5):  # Generate 5 frames
#     temp_data = generator.generate_temp_frame(temp_data)
#     print(temp_data)  # For demonstration, replace with appropriate visualization or storage logic
#     time.sleep(1)
