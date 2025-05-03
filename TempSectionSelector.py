import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QGridLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRect


class GridBlock(QWidget):
    def __init__(self, row, col, block_rect, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.block_rect = block_rect
        self.selected = False
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def toggle(self):
        self.selected = not self.selected
        self.update()

    def paintEvent(self, event):
        if self.selected:
            painter = QPainter(self)
            painter.setBrush(QBrush(QColor(0, 0, 0, 100)))  # Semi-transparent black
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

class AlertOverlay(QWidget):
    def __init__(self, parent, size, cold_blocks):
        super().__init__(parent)
        self.setGeometry(0, 0, size.width(), size.height())
        self.cold_blocks = cold_blocks
        self.block_width = size.width() // 8
        self.block_height = size.height() // 8
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.SolidLine))
        visited = set()

        def neighbors(r, c):
            return [(r + dr, c + dc) for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)] if (r + dr, c + dc) in self.cold_blocks]

        def bfs(start, group):
            queue = [start]
            while queue:
                node = queue.pop()
                if node in visited:
                    continue
                visited.add(node)
                group.append(node)
                queue.extend(neighbors(*node))

        # Find and outline groups
        for block in self.cold_blocks:
            if block in visited:
                continue
            group = []
            bfs(block, group)

            rows = [r for r, _ in group]
            cols = [c for _, c in group]
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)

            rect = QRect(
                min_col * self.block_width,
                min_row * self.block_height,
                (max_col - min_col + 1) * self.block_width,
                (max_row - min_row + 1) * self.block_height
            )
            painter.drawRect(rect)

class TemperatureSectionSelector(QDialog):
    def __init__(self, image, main_window, alert = False):
        super().__init__()
        self.setWindowTitle("Select Temperature Zones")
        self.main_window = main_window
        self.alert = alert
        
        original_pixmap = image
        crop_rect = QRect(20, 70, original_pixmap.width() - 130 , original_pixmap.height() - 130)
        pixmap = original_pixmap.copy(crop_rect)

        # Central widget to hold image and grid
        self.image_container = QWidget()
        self.image_container.setFixedSize(crop_rect.size())

        # Background image label
        self.label = QLabel(self.image_container)
        self.label.setPixmap(pixmap)
        self.label.setFixedSize(crop_rect.size())

        if alert:
            self.overlay = AlertOverlay(self.image_container, pixmap.size(), self.main_window.get_cold_blocks())
        else:
            self.overlay = QWidget(self.image_container)
            self.overlay.setGeometry(0, 0, crop_rect.width(), crop_rect.height())
            self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.grid_blocks = []
            block_width = crop_rect.width() // 8
            block_height = crop_rect.height() // 8

            for row in range(8):
                for col in range(8):
                    block = GridBlock(row, col, QRect(
                        col * block_width, row * block_height,
                        block_width, block_height
                    ), self.overlay)
                    block.setGeometry(block.block_rect)
                    block.show()
                    self.grid_blocks.append(block)

            self.overlay.mousePressEvent = self.handle_mouse_click

        # Buttons
        self.confirm_btn = QPushButton("Confirm")
        self.cancel_btn = QPushButton("Cancel")
        self.confirm_btn.clicked.connect(self.confirm_selection)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()

        # Layout configuration
        outer_layout = QVBoxLayout()
        outer_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        outer_layout.addWidget(self.image_container, alignment=Qt.AlignCenter)

        if alert:
            message = QLabel("Colder regions detected. Would you like to clear this alert? (This will also clear your selected region)")
            message.setAlignment(Qt.AlignCenter)
            outer_layout.addWidget(message)

        outer_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        outer_layout.addLayout(btn_layout)
        outer_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        outer_layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(outer_layout)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def handle_mouse_click(self, event):
        if self.alert:
            return
        for block in self.grid_blocks:
            if block.block_rect.contains(event.pos()):
                block.toggle()
                break

    def get_selected_blocks(self):
        return [(b.row, b.col) for b in self.grid_blocks if b.selected]

    def confirm_selection(self):
        if self.alert:
            self.main_window.clearTempSectionsAlert()
            self.main_window.setTempSections([])
            self.main_window.set_cold_blocks([])
            self.close()
            return

        selected = self.get_selected_blocks()
        if len(selected) < 2:
            QMessageBox.warning(self, "No Selection", "Please select at least two blocks.")
            return
        self.main_window.setTempSections(selected)
        self.close()

    def crop_pixmap_to_block(self, row, col):
        block_width = self.pixmap.width() // 8
        block_height = self.pixmap.height() // 8
        x = col * block_width
        y = row * block_height
        return self.pixmap.copy(x, y, block_width, block_height)
    

# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dummy placeholder image (use your real temperature pixmap here)
    pixmap = QPixmap(400, 400)
    pixmap.fill(Qt.white)

    window = TemperatureSectionSelector(pixmap)
    if window.exec_() == QDialog.Accepted:
        selected_blocks = window.get_selected_blocks()
        cropped_example = window.crop_pixmap_to_block(*selected_blocks[0])
        cropped_example.save("cropped_block.png")  # Save for demonstration

    sys.exit(app.exec_())
