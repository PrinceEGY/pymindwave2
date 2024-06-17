import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont


class ErrorDialog(QDialog):
    def __init__(self, error_message):
        super().__init__()

        self.setWindowTitle("Error")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.error_label = QLabel(error_message)
        self.error_label.setFont(QFont("Arial", 10))
        self.error_label.setContentsMargins(5, 5, 5, 10)
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)
