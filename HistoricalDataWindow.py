from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from db import get_db, readings_table, temp_arrays_table
import TempImageGenerator


class Ui_HistoricalData(object):
    
    def setupUi(self, HistoricalData, mainWindow):
        self.main_window = mainWindow
        HistoricalData.setObjectName("HistoricalData")
        HistoricalData.resize(1050, 800)

        self.historical_data_close_button = QtWidgets.QPushButton(HistoricalData)
        self.historical_data_close_button.setGeometry(QtCore.QRect(900, 700, 121, 31))
        self.historical_data_close_button.setObjectName("historical_data_close_button")
        self.historical_data_close_button.clicked.connect(self.closeWindow)

        self.tableView = QtWidgets.QTableWidget(HistoricalData)
        self.tableView.setGeometry(QtCore.QRect(80, 20, 940, 400))
        self.tableView.setObjectName("data_table")
        self.tableView.setColumnCount(7)
        self.tableView.setHorizontalHeaderLabels(["ID", "Date", "Time", "Distance(cm)", "Max Temp (C)", "Avg Temp (C)", "Details"])
        self.tableView.verticalHeader().setVisible(False)


        self.initialize_table()

        font = QtGui.QFont()
        font.setFamily("Cambria")
        font.setPointSize(16)

        self.temp_map_display = QtWidgets.QLabel(HistoricalData)
        self.temp_map_display.setGeometry(QtCore.QRect(120, 450, 400, 320))
        self.temp_map_display.setObjectName("temp_map_display")
        self.temp_map_display.setFont(font)
        self.temp_map_display.setStyleSheet("border: 1px solid black;")
        

        self.retranslateUi(HistoricalData)
        QtCore.QMetaObject.connectSlotsByName(HistoricalData)

    def retranslateUi(self, HistoricalData):
        _translate = QtCore.QCoreApplication.translate
        HistoricalData.setWindowTitle(_translate("HistoricalData", "Dialog"))
        self.historical_data_close_button.setText(_translate("HistoricalData", "Close"))


    def closeWindow(self):
        self.HistoricalData.hide()

    def __init__(self, main_window):
        super().__init__()
        self.HistoricalData = QtWidgets.QDialog()
        self.db = next(get_db())
        self.setupUi(self.HistoricalData, main_window)
        
        self.HistoricalData.show()

    def initialize_table(self):
        
        # Fetch all readings
        query = self.db.query(
            readings_table.c.id,
            readings_table.c.time, 
            readings_table.c.distance, 
            readings_table.c.max_temp, 
            readings_table.c.avg_temp
        ).all()

        # Convert the results into a DataFrame
        df = pd.DataFrame(query, columns=["id", "datetime", "distance", "max_temp", "avg_temp"])

        # Split "datetime" column into "date" and "time"
        df["date"] = df["datetime"].dt.date
        df["time"] = df["datetime"].dt.time

        # Reorder columns to match your request
        df = df[["id", "date", "time", "distance", "max_temp", "avg_temp"]]

        for index, row in df.iterrows():
            self.tableView.setRowCount(self.tableView.rowCount() + 1)
            self.tableView.setItem(self.tableView.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(row['id'])))
            self.tableView.setItem(self.tableView.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(row['date'])))
            self.tableView.setItem(self.tableView.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(str(row['time'])))
            self.tableView.setItem(self.tableView.rowCount() - 1, 3, QtWidgets.QTableWidgetItem(str(row['distance'])))
            self.tableView.setItem(self.tableView.rowCount() - 1, 4, QtWidgets.QTableWidgetItem(str(row['max_temp'])))
            self.tableView.setItem(self.tableView.rowCount() - 1, 5, QtWidgets.QTableWidgetItem(str(row['avg_temp'])))
            btn = QtWidgets.QPushButton("Temp Details")
            btn.clicked.connect(lambda _, r=row: self.on_button_click(r))  # Capture row index
            self.tableView.setCellWidget(self.tableView.rowCount() - 1, 6, btn)  # Add button to the last column

    def on_button_click(self, row):
        # Extract the id from the row
        id = row["id"]

        array_query = self.db.query(temp_arrays_table).filter(temp_arrays_table.c.reading_id == id).all()

        # Convert to DataFrame
        self.temp_df = pd.DataFrame(array_query, columns=["row_index"] + [f"column_{i}" for i in range(1, 33)] + ["array_id", "reading_id"])

        # Convert result into a 2D array
        array_2d = self.temp_df.iloc[:, 1:33].to_numpy()

        TempImageGenerator.generate_heatmap(array_2d, "ImageForHistoricalData.png")
        self.temp_image = QPixmap("ImageForHistoricalData.png")
        self.scaled_temp_image = self.temp_image.scaled(400, 450, QtCore.Qt.KeepAspectRatio)
        self.temp_map_display.setPixmap(self.scaled_temp_image)


    def update_table_data(self, time, max_temp, avg_temp):
        self.tableView.setRowCount(self.tableView.rowCount() + 1)
        self.tableView.setItem(self.tableView.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(str(time)))
        self.tableView.setItem(self.tableView.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(max_temp)))
        self.tableView.setItem(self.tableView.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(str(avg_temp)))

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    HistoricalData = QtWidgets.QDialog()
    emptydf = pd.DataFrame(columns= ["Time", "Temp", "Distance"])
    ui = Ui_HistoricalData(emptydf)

    sys.exit(app.exec_())