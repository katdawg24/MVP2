import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

class DistanceDialogWithRectangle(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def show_message(self):
        estop_msg = QMessageBox()
        estop_msg.setWindowTitle("Emergency Stop Details")

        estop_msg.setText(f"Emergency Stop Triggered!\n\nDistance: 2.90cm\nDistance Cutoff: 3.00cm")

        estop_msg.setStandardButtons(QMessageBox.Ok)
        estop_msg.resize(150,100)
        estop_msg.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DistanceDialogWithRectangle()
    window.show()
    window.show_message()
    sys.exit(app.exec_())
