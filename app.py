import logging
import sys
from PySide6 import QtWidgets
from ui.main_window import MainWindow
from util.logger import Logger

if __name__ == "__main__":
    Logger(level=logging.INFO, filename="mindwave.log", filemode="w")

    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.setWindowTitle("MindWave Mobile2 - EEG Data Acquisition")
    window.ui.spinBox_trials.setValue(5)
    window.show()

    sys.exit(app.exec())
