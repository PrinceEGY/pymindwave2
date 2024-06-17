import threading
from PySide6 import QtWidgets
from mindwave.session import SessionConfig
from ui.acquisitioner import AcquisitionWindow
from ui.error_dialog import ErrorDialog
from util.connection_state import ConnectionStatus
from mindwave.headset import MindWaveMobile2
from util.logger import Logger

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
    QMainWindow,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QMainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(596, 670)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_20 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 15, 20, 15)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_username = QLabel(self.groupBox_2)
        self.label_username.setObjectName("label_username")

        self.verticalLayout.addWidget(self.label_username)

        self.lineEdit_username = QLineEdit(self.groupBox_2)
        self.lineEdit_username.setObjectName("lineEdit_username")

        self.verticalLayout.addWidget(self.lineEdit_username)

        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_age = QLabel(self.groupBox_2)
        self.label_age.setObjectName("label_age")

        self.verticalLayout_3.addWidget(self.label_age)

        self.spinBox_Age = QSpinBox(self.groupBox_2)
        self.spinBox_Age.setObjectName("spinBox_Age")

        self.verticalLayout_3.addWidget(self.spinBox_Age)

        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(5)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_gender = QLabel(self.groupBox_2)
        self.label_gender.setObjectName("label_gender")

        self.verticalLayout_5.addWidget(self.label_gender)

        self.comboBox_gender = QComboBox(self.groupBox_2)
        self.comboBox_gender.addItem("")
        self.comboBox_gender.addItem("")
        self.comboBox_gender.addItem("")
        self.comboBox_gender.setObjectName("comboBox_gender")

        self.verticalLayout_5.addWidget(self.comboBox_gender)

        self.verticalLayout_2.addLayout(self.verticalLayout_5)

        self.verticalLayout_20.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(5)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_trials = QLabel(self.groupBox_3)
        self.label_trials.setObjectName("label_trials")

        self.verticalLayout_6.addWidget(self.label_trials)

        self.spinBox_trials = QSpinBox(self.groupBox_3)
        self.spinBox_trials.setObjectName("spinBox_trials")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.spinBox_trials.sizePolicy().hasHeightForWidth()
        )
        self.spinBox_trials.setSizePolicy(sizePolicy)

        self.verticalLayout_6.addWidget(self.spinBox_trials)

        self.gridLayout.addLayout(self.verticalLayout_6, 0, 0, 1, 1)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setSpacing(5)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_ready = QLabel(self.groupBox_3)
        self.label_ready.setObjectName("label_ready")

        self.verticalLayout_11.addWidget(self.label_ready)

        self.lineEdit_ready = QLineEdit(self.groupBox_3)
        self.lineEdit_ready.setObjectName("lineEdit_ready")

        self.verticalLayout_11.addWidget(self.lineEdit_ready)

        self.gridLayout.addLayout(self.verticalLayout_11, 1, 3, 1, 1)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setSpacing(5)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_baseline = QLabel(self.groupBox_3)
        self.label_baseline.setObjectName("label_baseline")

        self.verticalLayout_9.addWidget(self.label_baseline)

        self.lineEdit_baseline = QLineEdit(self.groupBox_3)
        self.lineEdit_baseline.setObjectName("lineEdit_baseline")

        self.verticalLayout_9.addWidget(self.lineEdit_baseline)

        self.gridLayout.addLayout(self.verticalLayout_9, 1, 0, 1, 1)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setSpacing(5)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.checkBox_blinks = QCheckBox(self.groupBox_3)
        self.checkBox_blinks.setObjectName("checkBox_blinks")
        sizePolicy.setHeightForWidth(
            self.checkBox_blinks.sizePolicy().hasHeightForWidth()
        )
        self.checkBox_blinks.setSizePolicy(sizePolicy)

        self.verticalLayout_15.addWidget(self.checkBox_blinks)

        self.gridLayout.addLayout(self.verticalLayout_15, 0, 3, 1, 1)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setSpacing(5)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_rest = QLabel(self.groupBox_3)
        self.label_rest.setObjectName("label_rest")

        self.verticalLayout_10.addWidget(self.label_rest)

        self.lineEdit_rest = QLineEdit(self.groupBox_3)
        self.lineEdit_rest.setObjectName("lineEdit_rest")

        self.verticalLayout_10.addWidget(self.lineEdit_rest)

        self.gridLayout.addLayout(self.verticalLayout_10, 1, 1, 1, 2)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setSpacing(5)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_motor = QLabel(self.groupBox_3)
        self.label_motor.setObjectName("label_motor")

        self.verticalLayout_13.addWidget(self.label_motor)

        self.lineEdit_motor = QLineEdit(self.groupBox_3)
        self.lineEdit_motor.setObjectName("lineEdit_motor")

        self.verticalLayout_13.addWidget(self.lineEdit_motor)

        self.gridLayout.addLayout(self.verticalLayout_13, 2, 1, 1, 2)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setSpacing(5)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_cue = QLabel(self.groupBox_3)
        self.label_cue.setObjectName("label_cue")

        self.verticalLayout_12.addWidget(self.label_cue)

        self.lineEdit_cue = QLineEdit(self.groupBox_3)
        self.lineEdit_cue.setObjectName("lineEdit_cue")

        self.verticalLayout_12.addWidget(self.lineEdit_cue)

        self.gridLayout.addLayout(self.verticalLayout_12, 2, 0, 1, 1)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setSpacing(5)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_extra = QLabel(self.groupBox_3)
        self.label_extra.setObjectName("label_extra")

        self.verticalLayout_14.addWidget(self.label_extra)

        self.lineEdit_extra = QLineEdit(self.groupBox_3)
        self.lineEdit_extra.setObjectName("lineEdit_extra")

        self.verticalLayout_14.addWidget(self.lineEdit_extra)

        self.gridLayout.addLayout(self.verticalLayout_14, 2, 3, 1, 1)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(5)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_classes = QLabel(self.groupBox_3)
        self.label_classes.setObjectName("label_classes")

        self.verticalLayout_7.addWidget(self.label_classes)

        self.lineEdit_classes = QLineEdit(self.groupBox_3)
        self.lineEdit_classes.setObjectName("lineEdit_classes")

        self.verticalLayout_7.addWidget(self.lineEdit_classes)

        self.gridLayout.addLayout(self.verticalLayout_7, 0, 1, 1, 2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.label_savedir = QLabel(self.groupBox_3)
        self.label_savedir.setObjectName("label_savedir")

        self.verticalLayout_4.addWidget(self.label_savedir)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_savedir = QLineEdit(self.groupBox_3)
        self.lineEdit_savedir.setObjectName("lineEdit_savedir")
        sizePolicy.setHeightForWidth(
            self.lineEdit_savedir.sizePolicy().hasHeightForWidth()
        )
        self.lineEdit_savedir.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.lineEdit_savedir)

        self.pushButton_savedir = QPushButton(self.groupBox_3)
        self.pushButton_savedir.setObjectName("pushButton_savedir")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.pushButton_savedir.sizePolicy().hasHeightForWidth()
        )
        self.pushButton_savedir.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pushButton_savedir)

        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.gridLayout.addLayout(self.verticalLayout_4, 3, 0, 1, 4)

        self.verticalLayout_20.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_headset_connection = QLabel(self.groupBox_4)
        self.label_headset_connection.setObjectName("label_headset_connection")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.label_headset_connection.sizePolicy().hasHeightForWidth()
        )
        self.label_headset_connection.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.label_headset_connection, 0, 0, 1, 1)

        self.label_headset_status = QLabel(self.groupBox_4)
        self.label_headset_status.setObjectName("label_headset_status")

        self.gridLayout_2.addWidget(self.label_headset_status, 0, 1, 1, 1)

        self.pushButton_headset_connect = QPushButton(self.groupBox_4)
        self.pushButton_headset_connect.setObjectName("pushButton_headset_connect")

        self.gridLayout_2.addWidget(self.pushButton_headset_connect, 1, 0, 1, 2)

        self.verticalLayout_20.addWidget(self.groupBox_4)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushButton_start_session = QPushButton(self.frame_2)
        self.pushButton_start_session.setObjectName("pushButton_start_session")

        self.gridLayout_3.addWidget(self.pushButton_start_session, 1, 1, 1, 2)

        self.label_signalquality = QLabel(self.frame_2)
        self.label_signalquality.setObjectName("label_signalquality")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.label_signalquality.sizePolicy().hasHeightForWidth()
        )
        self.label_signalquality.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.label_signalquality, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.label_signalquality_percent = QLabel(self.frame_2)
        self.label_signalquality_percent.setObjectName("label_signalquality_percent")

        self.gridLayout_3.addWidget(self.label_signalquality_percent, 0, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 3, 1, 1)

        self.verticalLayout_20.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 596, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.groupBox_2.setTitle(
            QCoreApplication.translate("MainWindow", "User Information", None)
        )
        self.label_username.setText(
            QCoreApplication.translate("MainWindow", "Name", None)
        )
        self.label_age.setText(QCoreApplication.translate("MainWindow", "Age", None))
        self.label_gender.setText(
            QCoreApplication.translate("MainWindow", "Gender", None)
        )
        self.comboBox_gender.setItemText(
            0, QCoreApplication.translate("MainWindow", "Male", None)
        )
        self.comboBox_gender.setItemText(
            1, QCoreApplication.translate("MainWindow", "Female", None)
        )
        self.comboBox_gender.setItemText(
            2, QCoreApplication.translate("MainWindow", "Perfer not to say", None)
        )

        self.groupBox_3.setTitle(
            QCoreApplication.translate("MainWindow", "Session Config", None)
        )
        self.label_trials.setText(
            QCoreApplication.translate("MainWindow", "Number of Trials", None)
        )
        self.label_ready.setText(
            QCoreApplication.translate("MainWindow", "Ready duration", None)
        )
        self.lineEdit_ready.setText(
            QCoreApplication.translate("MainWindow", "1.0", None)
        )
        self.label_baseline.setText(
            QCoreApplication.translate("MainWindow", "Baseline duration", None)
        )
        self.lineEdit_baseline.setText(
            QCoreApplication.translate("MainWindow", "15.0", None)
        )
        self.checkBox_blinks.setText(
            QCoreApplication.translate("MainWindow", "Capture Blinks", None)
        )
        self.label_rest.setText(
            QCoreApplication.translate("MainWindow", "Rest duration", None)
        )
        self.lineEdit_rest.setText(
            QCoreApplication.translate("MainWindow", "2.0", None)
        )
        self.label_motor.setText(
            QCoreApplication.translate("MainWindow", "Motor duration", None)
        )
        self.lineEdit_motor.setText(
            QCoreApplication.translate("MainWindow", "4.0", None)
        )
        self.label_cue.setText(
            QCoreApplication.translate("MainWindow", "Cue duration", None)
        )
        self.lineEdit_cue.setText(QCoreApplication.translate("MainWindow", "1.5", None))
        self.label_extra.setText(
            QCoreApplication.translate("MainWindow", "Extra Motor duration", None)
        )
        self.lineEdit_extra.setText(
            QCoreApplication.translate("MainWindow", "3.0", None)
        )
        self.label_classes.setText(
            QCoreApplication.translate(
                "MainWindow", "Classes (Seperated with comma)", None
            )
        )
        self.lineEdit_classes.setText(
            QCoreApplication.translate("MainWindow", "Left, Right", None)
        )
        self.label_savedir.setText(
            QCoreApplication.translate("MainWindow", "Save Directory", None)
        )
        self.pushButton_savedir.setText(
            QCoreApplication.translate("MainWindow", "Select Folder", None)
        )
        self.groupBox_4.setTitle(
            QCoreApplication.translate("MainWindow", "Headset", None)
        )
        self.label_headset_connection.setText(
            QCoreApplication.translate("MainWindow", "Connection State:", None)
        )
        self.label_headset_status.setText(
            QCoreApplication.translate("MainWindow", "Disconnected", None)
        )
        self.pushButton_headset_connect.setText(
            QCoreApplication.translate("MainWindow", "Connect", None)
        )
        self.pushButton_start_session.setText(
            QCoreApplication.translate("MainWindow", "Start Session", None)
        )
        self.label_signalquality.setText(
            QCoreApplication.translate("MainWindow", "Signal Quality:", None)
        )
        self.label_signalquality_percent.setText(
            QCoreApplication.translate("MainWindow", "0%", None)
        )

    # retranslateUi


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
        self.ui.pushButton_start_session.clicked.connect(self.start_acquisition)

    def get_folder_path(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory()
        self.ui.lineEdit_savedir.setText(folder_path)

    def headset_connection(self):
        if self.headset.connection_status == ConnectionStatus.DISCONNECTED:
            thread = threading.Thread(
                target=self.headset.connect, daemon=True, kwargs={"timeout": 30}
            )
        else:
            thread = threading.Thread(target=self.headset.disconnect, daemon=True)
        thread.start()

    def start_acquisition(self):
        if self.headset.connection_status != ConnectionStatus.CONNECTED:
            self._logger.error("Headset is not connected")
            error_dialog = ErrorDialog("Headset is not connected!")
            error_dialog.exec()
        elif self.headset.signal_quality < 100:
            self._logger.error(
                "Signal quality is low, Current Signal Quality: %s",
                self.headset.signal_quality,
            )
            error_dialog = ErrorDialog(
                "Signal quality is low!, Please wear the headset properly and make sure the signal quality is 100% before starting the session"
            )
            error_dialog.exec()
        # else:
        self.acq_window = AcquisitionWindow(self.headset)
        self.acq_window.show()

        sess_config = SessionConfig(
            user_name=self.ui.lineEdit_username.text(),
            user_age=self.ui.spinBox_Age.value(),
            user_gender=self.ui.comboBox_gender.currentText(),
            classes=self.ui.lineEdit_classes.text().split(","),
            trials=self.ui.spinBox_trials.value(),
            baseline_duration=float(self.ui.lineEdit_baseline.text()),
            rest_duration=float(self.ui.lineEdit_rest.text()),
            ready_duration=float(self.ui.lineEdit_ready.text()),
            cue_duration=float(self.ui.lineEdit_cue.text()),
            motor_duration=float(self.ui.lineEdit_motor.text()),
            extra_duration=float(self.ui.lineEdit_extra.text()),
            save_dir=self.ui.lineEdit_savedir.text(),
            capture_blinks=self.ui.checkBox_blinks.isChecked(),
        )
        self._logger.debug("Session Configuration: %s", sess_config)

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
