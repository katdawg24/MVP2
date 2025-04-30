import datetime
from datetime import datetime
import time
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

import serial
from db import get_db, readings_table, temp_arrays_table
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

class GetDataSerialWorker(QThread):
    data_received = pyqtSignal(pd.DataFrame)  # Signal to send data to the GUI

    def __init__(self, teensy_port):
        super().__init__()
        self.running = True
        self.port = teensy_port
        self.baudrate = 19200
        self.prev_time = time.perf_counter()
        
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

        self.df.loc[len(self.df)] = [data[0], data[1], float(data[2]), float(data[3]), max_temp, avg_temp, temp_1, temp_2, temp_3, temp_4, temp_5, temp_6, temp_7]

    def store_data(self, data: pd.DataFrame):
        # Convert DataFrame rows into dictionary format
        last_row = data.iloc[-1]

        time = datetime.strptime(last_row["Time"], "%Y-%m-%d %H:%M:%S")

        insert_data = {
            "time": time,
            "distance": float(last_row["Distance"]),
            "max_temp": float(last_row["Max Temp"]),
            "avg_temp": float(last_row["Avg Temp"]),
            "distance_roc": float(last_row["Distance ROC"])
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

    def calculate_distance_roc(self, distance, prev_distance):
        curr_time = time.perf_counter()

        if prev_distance == 0:
            return 0.0
        else:
            delta_distance = distance - prev_distance
            delta_time = curr_time - self.prev_time
            self.prev_time = curr_time
            return delta_distance / delta_time

    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        ser.setDTR(False)
        time.sleep(1)
        ser.flushInput()
        ser.setDTR(True)
        
        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance", "Distance ROC", "Max Temp", "Avg Temp", "Temp 1", "Temp 2", "Temp 3", "Temp 4", "Temp 5", "Temp 6", "Temp 7"])
        # temp_data = self.generate_temp_frame()

        line = ''
        temp_array = []
        is_distance_next = False
        distance_mm = 0

        try:
            # Wait for first reading
            while line != '' or not(is_distance_next):
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

                #If the line is lond, we know that we're in the middle of a temp reading
                if len(line) > 4:
                    is_distance_next = True

            #Exits first loop when it reaches the first empty line
            #Consumes any empty lines before the first full reading
            while line == '':
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

            while self.running:
                # Read distance
                distance_mm = float(line)

                while line != '':
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()

                # Consume empty line
                while line == '':
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()

                # Read temperature data until empty line
                while line != "":
                    values = [float(x) for x in line[:-1].split(",")]
                    temp_array.append(values)
                    
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()

                dist_roc = self.calculate_distance_roc(distance_mm / 10.0, self.df["Distance"].iloc[-1] if not self.df.empty else 0)
                data = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), np.array(temp_array), distance_mm / 10.0, dist_roc]
                self.update_data_frame(data)
                self.store_data(self.df)
                data_to_send = pd.DataFrame(self.df.iloc[-1:])
                self.data_received.emit(data_to_send)
                temp_array.clear()

                while line == "":
                    if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').strip()

            ser.close()

        except serial.SerialException as e:
            print(f"Error: {e}")

    def stop(self):
        self.running = False
        self.wait()

