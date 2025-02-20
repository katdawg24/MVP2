import datetime
from datetime import datetime
import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from scipy.ndimage import gaussian_filter
import numpy as np
import random
from db import get_db, readings_table, temp_arrays_table
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

class TestDataSerialWorker(QThread):
    data_received = pyqtSignal(pd.DataFrame)  # Signal to send data to the GUI

    def __init__(self):
        super().__init__()
        self.running = True

        
        self.db = next(get_db())
    
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
        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance", "Max Temp", "Avg Temp", "Temp 1", "Temp 2", "Temp 3", "Temp 4", "Temp 5", "Temp 6", "Temp 7"])
        temp_data = self.generate_temp_frame()

        data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), temp_data, random.randint(50, 100) / 10.0]
        self.update_data_frame(data)
        self.store_data(self.df)
        self.data_received.emit(self.df)
        time.sleep(1)

        while (self.running):
            temp_data = self.generate_temp_frame(temp_data)
            data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), temp_data, random.randint(50, 100) / 10.0]
            self.update_data_frame(data)
            self.store_data(self.df)
            self.data_received.emit(self.df.iloc[-1:])
            time.sleep(1)
            

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
