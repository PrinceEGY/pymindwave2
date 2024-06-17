import logging
import sys
import threading
from PySide6 import QtWidgets
from mindwave.headset import MindWaveMobile2
from ui.main_window import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow

from util.connection_state import ConnectionStatus
from util.event_manager import EventType
from util.logger import Logger


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self._logger = Logger._instance.get_logger(self.__class__.__name__)
        self.ui.setupUi(self)
        self.headset = MindWaveMobile2()

        self.headset.on_status_change(self.update_headset_status)
        self.headset.on_signal_quality_change(self.update_signal_quality)

        self.ui.label_headset_status.setText(self.headset.connection_status.name)

        self.ui.pushButton_savedir.clicked.connect(self.get_folder_path)
        self.ui.pushButton_headset_connect.clicked.connect(self.headset_connection)

    def get_folder_path(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        self.ui.lineEdit_savedir.setText(folder_path)

    def headset_connection(self):
        if self.headset.connection_status == ConnectionStatus.DISCONNECTED:
            thread = threading.Thread(target=self.headset.connect, daemon=True)
        else:
            thread = threading.Thread(target=self.headset.disconnect, daemon=True)
        thread.start()

    def update_headset_status(self, status):
        # TODO: change the button status logic to be consisted with the retrying connection logic
        self.ui.label_headset_status.setText(status.name)
        if status == ConnectionStatus.CONNECTED:
            self.ui.pushButton_headset_connect.setText("Disconnect")
            self.ui.pushButton_headset_connect.setEnabled(True)
        elif status == ConnectionStatus.DISCONNECTED:
            self.ui.pushButton_headset_connect.setText("Connect")
            self.ui.pushButton_headset_connect.setEnabled(True)
        else:
            self.ui.pushButton_headset_connect.setEnabled(False)
            self.ui.pushButton_headset_connect.setText("Connecting...")

    def update_signal_quality(self, signal_quality):
        self.ui.label_signalquality_percent.setText(f"{signal_quality}%")


if __name__ == "__main__":
    Logger(level=logging.DEBUG, filename="mindwave.log", filemode="w")

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.setWindowTitle("MindWave Mobile2 - EEG Data Acquisition")
    window.show()
    window.ui.spinBox_trials.setValue(5)

    window.show()
    sys.exit(app.exec())
