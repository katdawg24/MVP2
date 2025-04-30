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


from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
import pandas as pd
from PyQt5.QtGui import QPixmap
from db import get_db, readings_table, temp_arrays_table
import TempImageGenerator
import datetime

class Ui_HistoricalData(object):
    def __init__(self, main_window):
        super().__init__()
        self.HistoricalData = QtWidgets.QDialog()
        self.db = next(get_db())
        self.main_window = main_window
        self.full_data = []
        self.loaded_rows = 0
        self.batch_size = 20
        self.current_filter = "Last Hour"
        self.setupUi(self.HistoricalData)
        self.HistoricalData.show()

    def setupUi(self, HistoricalData):
        HistoricalData.setObjectName("HistoricalData")
        HistoricalData.resize(1150, 900)

        # Filter dropdown
        self.filter_combo = QtWidgets.QComboBox(HistoricalData)
        self.filter_combo.setGeometry(QtCore.QRect(50, 20, 200, 30))
        self.filter_combo.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "All"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)

        self.refresh_button = QtWidgets.QPushButton(HistoricalData)
        self.refresh_button.setGeometry(QtCore.QRect(280, 20, 120, 30))
        self.refresh_button.setText("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)

        self.tableView = QtWidgets.QTableWidget(HistoricalData)
        self.tableView.setGeometry(QtCore.QRect(50, 60, 1040, 450))
        self.tableView.setObjectName("data_table")
        self.tableView.setColumnCount(8)
        self.tableView.setHorizontalHeaderLabels(
            ["ID", "Date", "Time", "Distance(cm)", "Distance ROC(cm/s)", "Max Temp (C)", "Avg Temp (C)", "Details"]
        )
        self.tableView.verticalHeader().setVisible(False)

        self.tableView.verticalScrollBar().valueChanged.connect(self.check_scroll_position)

        font = QtGui.QFont()
        font.setFamily("Cambria")
        font.setPointSize(16)

        self.temp_map_display = QtWidgets.QLabel(HistoricalData)
        self.temp_map_display.setGeometry(QtCore.QRect(200, 530, 400, 320))
        self.temp_map_display.setFont(font)
        self.temp_map_display.setStyleSheet("border: 1px solid black;")

        self.historical_data_close_button = QtWidgets.QPushButton(HistoricalData)
        self.historical_data_close_button.setGeometry(QtCore.QRect(900, 820, 121, 31))
        self.historical_data_close_button.setObjectName("historical_data_close_button")
        self.historical_data_close_button.setText("Close")
        self.historical_data_close_button.clicked.connect(self.HistoricalData.hide)

        self.retranslateUi(HistoricalData)
        QtCore.QMetaObject.connectSlotsByName(HistoricalData)

        self.fetch_data()
        self.load_next_batch()

    def retranslateUi(self, HistoricalData):
        _translate = QtCore.QCoreApplication.translate
        HistoricalData.setWindowTitle(_translate("HistoricalData", "Historical Readings"))

    def fetch_data(self):
        now = datetime.datetime.now()
        query = self.db.query(
            readings_table.c.id,
            readings_table.c.time,
            readings_table.c.distance,
            readings_table.c.distance_roc,
            readings_table.c.max_temp,
            readings_table.c.avg_temp
        )

        if self.current_filter == "Last Hour":
            query = query.filter(readings_table.c.time >= now - datetime.timedelta(hours=1))
        elif self.current_filter == "Last 6 Hours":
            query = query.filter(readings_table.c.time >= now - datetime.timedelta(hours=6))
        elif self.current_filter == "Last 24 Hours":
            query = query.filter(readings_table.c.time >= now - datetime.timedelta(days=1))

        self.full_data = query.order_by(readings_table.c.time.desc()).all()
        self.loaded_rows = 0
        self.tableView.setRowCount(0)

    def apply_filter(self, value):
        self.current_filter = value
        self.fetch_data()
        self.load_next_batch()

    def refresh_data(self):
        self.fetch_data()
        self.load_next_batch()

    def load_next_batch(self):
        batch = self.full_data[self.loaded_rows:self.loaded_rows + self.batch_size]
        for row in batch:
            row_position = self.tableView.rowCount()
            self.tableView.insertRow(row_position)

            date = row.time.date()
            time = row.time.time()

            self.tableView.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            self.tableView.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(date)))
            self.tableView.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(time)))
            self.tableView.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(row.distance)))
            self.tableView.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(row.distance_roc)))
            self.tableView.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(row.max_temp)))
            self.tableView.setItem(row_position, 6, QtWidgets.QTableWidgetItem(str(row.avg_temp)))

            btn = QtWidgets.QPushButton("Temp Details")
            btn.clicked.connect(lambda _, r=row: self.on_button_click(r))
            self.tableView.setCellWidget(row_position, 7, btn)

        self.loaded_rows += len(batch)

    def check_scroll_position(self):
        scrollbar = self.tableView.verticalScrollBar()
        if scrollbar.value() > scrollbar.maximum() - 10:
            if self.loaded_rows < len(self.full_data):
                self.load_next_batch()

    def on_button_click(self, row):
        id = row.id
        array_query = self.db.query(temp_arrays_table).filter(temp_arrays_table.c.reading_id == id).all()
        self.temp_df = pd.DataFrame(array_query, columns=["row_index"] + [f"column_{i}" for i in range(1, 33)] + ["array_id", "reading_id"])

        array_2d = self.temp_df.iloc[:, 1:33].to_numpy()
        TempImageGenerator.generate_heatmap(array_2d, "ImageForHistoricalData.png")
        self.temp_image = QPixmap("ImageForHistoricalData.png")
        self.scaled_temp_image = self.temp_image.scaled(400, 450, QtCore.Qt.KeepAspectRatio)
        self.temp_map_display.setPixmap(self.scaled_temp_image)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    HistoricalData = QtWidgets.QDialog()
    emptydf = pd.DataFrame(columns= ["Time", "Temp", "Distance"])
    ui = Ui_HistoricalData(emptydf)

    sys.exit(app.exec_())