import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import serial
import pandas as pd

class SerialWorker(QThread):
    data_received = pyqtSignal(list)  # Signal to send data to the GUI

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        ser = serial.Serial(self.port, self.baudrate)
        ser.setDTR(False)
        time.sleep(1)
        ser.flushInput()
        ser.setDTR(True)

        value_set = []
        avg_values = []

        try:
            ser.readline()
            while self.running:
                
                if ser.in_waiting > 0:

                    for i in range(3):
                        
                        data = ser.readline().decode('utf-8').strip()
                        
                        
                        values = [float(x) for x in data.split()]
                        value_set.append(values)
                        
                    for i in range(3):
                        avg = (value_set[0][i] + value_set[1][i] + value_set[2][i]) / 3.0
                        avg_values.append(round(avg, 2))
                    
                    print(avg_values)      
                    value_set.clear()
                    
                    self.data_received.emit(avg_values)  # Emit the signal with new data
                    avg_values.clear() 

                         
            ser.close()
        except serial.SerialException as e:
            print(f"Error: {e}")
            
        # finally:
        #     if hasattr(self, 'ser') and self.ser.is_open:
        #         self.ser.close() 

    def send_setup(self):
        self.ser = serial.Serial(self.port, self.baudrate)


    def send_data(self, data):
        data = data + "\n"
        self.ser.write(data.encode('utf-8'))  # Send data as bytes
            

    def stop(self):
        self.running = False
        self.wait()
