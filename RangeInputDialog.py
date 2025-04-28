from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QApplication, QWidget
)
from PyQt5.QtGui import QDoubleValidator
import sys

class RangeInputDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Set Expected Ranges")
        self.setFixedSize(700, 190)
        self.init_ui(main_window)
        self.show()
        

    def init_ui(self, main_window):
        main_layout = QVBoxLayout()
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)
        self.main_window = main_window

        # Prompt
        prompt_label = QLabel("Please enter the expected ranges for sensor readings:")
        main_layout.addWidget(prompt_label)

        # Temperature range
        temp_label = QLabel("Temperature Range (C): ")
        self.temp_min_input = QLineEdit()
        self.temp_min_input.setText(str(self.main_window.exp_temp_min))
        self.temp_max_input = QLineEdit()
        self.temp_max_input.setText(str(self.main_window.exp_temp_max))
        self.temp_min_input.setValidator(QDoubleValidator())
        self.temp_max_input.setValidator(QDoubleValidator())

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_min_input)
        temp_layout.addWidget(QLabel("to"))
        temp_layout.addWidget(self.temp_max_input)
        main_layout.addLayout(temp_layout)

        # Distance range
        dist_label = QLabel("Distance Range (cm): ")
        self.dist_min_input = QLineEdit()
        self.dist_min_input.setText(str(self.main_window.exp_dist_min))
        self.dist_max_input = QLineEdit()
        self.dist_max_input.setText(str(self.main_window.exp_dist_max))
        self.dist_min_input.setValidator(QDoubleValidator())
        self.dist_max_input.setValidator(QDoubleValidator())

        dist_layout = QHBoxLayout()
        dist_layout.addWidget(dist_label)
        dist_layout.addWidget(self.dist_min_input)
        dist_layout.addWidget(QLabel("to"))
        dist_layout.addWidget(self.dist_max_input)
        main_layout.addLayout(dist_layout)

        # Buttons
        button_layout = QHBoxLayout()
        if self.main_window.maintenance_needed:
            exit_maintenance_mode_btn = QPushButton("Maintenance Complete")
            exit_maintenance_mode_btn.clicked.connect(self.main_window.setMaintenanceComplete)
            button_layout.addWidget(exit_maintenance_mode_btn)
        cancel_btn = QPushButton("Cancel")
        confirm_btn = QPushButton("Confirm")
        cancel_btn.clicked.connect(self.closeWindow)
        confirm_btn.clicked.connect(self.confirm_ranges)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(confirm_btn)

        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_ranges(self):
        return {
            "temp_min": float(self.temp_min_input.text()),
            "temp_max": float(self.temp_max_input.text()),
            "dist_min": float(self.dist_min_input.text()),
            "dist_max": float(self.dist_max_input.text()),
        }
    
    def closeWindow(self):
        self.close()

    def confirm_ranges(self):
        self.main_window.setExpectedRanges(self.get_ranges())
        self.close()
