import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import serial
import pandas as pd

class SendSerialWorker(QThread):

    def __init__(self, arduino_port):
        super().__init__()
        self.port = arduino_port
        self.baudrate = 9600
        self.running = True

    def send_setup(self):
        self.ser = serial.Serial(self.port, self.baudrate)


    def send_data(self, data):
        data = data + "\n"
        self.ser.write(data.encode('utf-8'))  # Send data as bytes
            

    def stop(self):
        self.running = False
        self.wait()
