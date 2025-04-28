import serial.tools.list_ports
import MainWindow
import pandas as pd

import GetDataSerialWorker


class Main(object):
    
    def __init__(self):
        self.temp_cutoff = 100000
        self.distance_cutoff = 100000

    ## for testing without serial connection
    def setUp(self):

        try:
            ports = list(serial.tools.list_ports.comports())

            for port in ports:
                if port.description.startswith("Arduino"):
                    arduino_port = port.device
                else:
                    teensy_port = port.device

        except Exception as e:
            print(f"Could not start application: {e}")

        print("Arduino port:" + arduino_port)
        print("Teensy port:" + teensy_port)
        
        self.receive_serial_thread = GetDataSerialWorker.GetDataSerialWorker(teensy_port)

        self.main_window = MainWindow.Ui_MainWindow(self.receive_serial_thread, arduino_port)


if __name__ == "__main__":
    main = Main()
    main.setUp()