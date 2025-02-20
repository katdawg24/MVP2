import MainWindow
import SerialWorker
import pandas as pd

import TestDataSerialWorker
import GetDataSerialWorker

class Main(object):
    
    def __init__(self):
        self.temp_cutoff = 100000
        self.distance_cutoff = 100000

    ## for serial connection
    def setUp(self):
        self.df = pd.DataFrame(columns= ["Time", "Temp", "Distance"])

        self.receive_serial_thread = SerialWorker.SerialWorker('COM5', 9600)
        self.receive_serial_thread.start()
        self.receive_serial_thread.data_received.connect(self.processData)

        self.send_serial_thread = SerialWorker.SerialWorker('COM3', 9600)

        self.main_window = MainWindow.Ui_MainWindow(self.receive_serial_thread, self.send_serial_thread)

    ## for testing without serial connection
    def setUpTest(self):
        

        self.receive_serial_thread = TestDataSerialWorker.TestDataSerialWorker()
        #self.receive_serial_thread = GetDataSerialWorker.GetDataSerialWorker()

        self.main_window = MainWindow.Ui_MainWindow(self.receive_serial_thread)
        

if __name__ == "__main__":
    main = Main()
    # main.setUp()
    main.setUpTest()