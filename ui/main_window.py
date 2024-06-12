# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'backup0KzEZYP.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(596, 670)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_20 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, 15, 20, 15)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_username = QLabel(self.groupBox_2)
        self.label_username.setObjectName(u"label_username")

        self.verticalLayout.addWidget(self.label_username)

        self.lineEdit_username = QLineEdit(self.groupBox_2)
        self.lineEdit_username.setObjectName(u"lineEdit_username")

        self.verticalLayout.addWidget(self.lineEdit_username)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_age = QLabel(self.groupBox_2)
        self.label_age.setObjectName(u"label_age")

        self.verticalLayout_3.addWidget(self.label_age)

        self.spinBox_Age = QSpinBox(self.groupBox_2)
        self.spinBox_Age.setObjectName(u"spinBox_Age")

        self.verticalLayout_3.addWidget(self.spinBox_Age)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(5)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_gender = QLabel(self.groupBox_2)
        self.label_gender.setObjectName(u"label_gender")

        self.verticalLayout_5.addWidget(self.label_gender)

        self.comboBox_gender = QComboBox(self.groupBox_2)
        self.comboBox_gender.addItem("")
        self.comboBox_gender.addItem("")
        self.comboBox_gender.addItem("")
        self.comboBox_gender.setObjectName(u"comboBox_gender")

        self.verticalLayout_5.addWidget(self.comboBox_gender)


        self.verticalLayout_2.addLayout(self.verticalLayout_5)


        self.verticalLayout_20.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setSpacing(5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_trials = QLabel(self.groupBox_3)
        self.label_trials.setObjectName(u"label_trials")

        self.verticalLayout_6.addWidget(self.label_trials)

        self.spinBox_trials = QSpinBox(self.groupBox_3)
        self.spinBox_trials.setObjectName(u"spinBox_trials")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_trials.sizePolicy().hasHeightForWidth())
        self.spinBox_trials.setSizePolicy(sizePolicy)

        self.verticalLayout_6.addWidget(self.spinBox_trials)


        self.gridLayout.addLayout(self.verticalLayout_6, 0, 0, 1, 1)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setSpacing(5)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_ready = QLabel(self.groupBox_3)
        self.label_ready.setObjectName(u"label_ready")

        self.verticalLayout_11.addWidget(self.label_ready)

        self.lineEdit_ready = QLineEdit(self.groupBox_3)
        self.lineEdit_ready.setObjectName(u"lineEdit_ready")

        self.verticalLayout_11.addWidget(self.lineEdit_ready)


        self.gridLayout.addLayout(self.verticalLayout_11, 1, 3, 1, 1)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setSpacing(5)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_baseline = QLabel(self.groupBox_3)
        self.label_baseline.setObjectName(u"label_baseline")

        self.verticalLayout_9.addWidget(self.label_baseline)

        self.lineEdit_baseline = QLineEdit(self.groupBox_3)
        self.lineEdit_baseline.setObjectName(u"lineEdit_baseline")

        self.verticalLayout_9.addWidget(self.lineEdit_baseline)


        self.gridLayout.addLayout(self.verticalLayout_9, 1, 0, 1, 1)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setSpacing(5)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.checkBox_blinks = QCheckBox(self.groupBox_3)
        self.checkBox_blinks.setObjectName(u"checkBox_blinks")
        sizePolicy.setHeightForWidth(self.checkBox_blinks.sizePolicy().hasHeightForWidth())
        self.checkBox_blinks.setSizePolicy(sizePolicy)

        self.verticalLayout_15.addWidget(self.checkBox_blinks)


        self.gridLayout.addLayout(self.verticalLayout_15, 0, 3, 1, 1)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setSpacing(5)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_rest = QLabel(self.groupBox_3)
        self.label_rest.setObjectName(u"label_rest")

        self.verticalLayout_10.addWidget(self.label_rest)

        self.lineEdit_rest = QLineEdit(self.groupBox_3)
        self.lineEdit_rest.setObjectName(u"lineEdit_rest")

        self.verticalLayout_10.addWidget(self.lineEdit_rest)


        self.gridLayout.addLayout(self.verticalLayout_10, 1, 1, 1, 2)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setSpacing(5)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_motor = QLabel(self.groupBox_3)
        self.label_motor.setObjectName(u"label_motor")

        self.verticalLayout_13.addWidget(self.label_motor)

        self.lineEdit_motor = QLineEdit(self.groupBox_3)
        self.lineEdit_motor.setObjectName(u"lineEdit_motor")

        self.verticalLayout_13.addWidget(self.lineEdit_motor)


        self.gridLayout.addLayout(self.verticalLayout_13, 2, 1, 1, 2)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setSpacing(5)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_cue = QLabel(self.groupBox_3)
        self.label_cue.setObjectName(u"label_cue")

        self.verticalLayout_12.addWidget(self.label_cue)

        self.lineEdit_cue = QLineEdit(self.groupBox_3)
        self.lineEdit_cue.setObjectName(u"lineEdit_cue")

        self.verticalLayout_12.addWidget(self.lineEdit_cue)


        self.gridLayout.addLayout(self.verticalLayout_12, 2, 0, 1, 1)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setSpacing(5)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_extra = QLabel(self.groupBox_3)
        self.label_extra.setObjectName(u"label_extra")

        self.verticalLayout_14.addWidget(self.label_extra)

        self.lineEdit_extra = QLineEdit(self.groupBox_3)
        self.lineEdit_extra.setObjectName(u"lineEdit_extra")

        self.verticalLayout_14.addWidget(self.lineEdit_extra)


        self.gridLayout.addLayout(self.verticalLayout_14, 2, 3, 1, 1)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setSpacing(5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_classes = QLabel(self.groupBox_3)
        self.label_classes.setObjectName(u"label_classes")

        self.verticalLayout_7.addWidget(self.label_classes)

        self.lineEdit_classes = QLineEdit(self.groupBox_3)
        self.lineEdit_classes.setObjectName(u"lineEdit_classes")

        self.verticalLayout_7.addWidget(self.lineEdit_classes)


        self.gridLayout.addLayout(self.verticalLayout_7, 0, 1, 1, 2)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.label_savedir = QLabel(self.groupBox_3)
        self.label_savedir.setObjectName(u"label_savedir")

        self.verticalLayout_4.addWidget(self.label_savedir)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_savedir = QLineEdit(self.groupBox_3)
        self.lineEdit_savedir.setObjectName(u"lineEdit_savedir")
        sizePolicy.setHeightForWidth(self.lineEdit_savedir.sizePolicy().hasHeightForWidth())
        self.lineEdit_savedir.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.lineEdit_savedir)

        self.pushButton_savedir = QPushButton(self.groupBox_3)
        self.pushButton_savedir.setObjectName(u"pushButton_savedir")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_savedir.sizePolicy().hasHeightForWidth())
        self.pushButton_savedir.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pushButton_savedir)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout_4, 3, 0, 1, 4)


        self.verticalLayout_20.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_2 = QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_headset_connection = QLabel(self.groupBox_4)
        self.label_headset_connection.setObjectName(u"label_headset_connection")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_headset_connection.sizePolicy().hasHeightForWidth())
        self.label_headset_connection.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.label_headset_connection, 0, 0, 1, 1)

        self.label_headset_status = QLabel(self.groupBox_4)
        self.label_headset_status.setObjectName(u"label_headset_status")

        self.gridLayout_2.addWidget(self.label_headset_status, 0, 1, 1, 1)

        self.pushButton_headset_connect = QPushButton(self.groupBox_4)
        self.pushButton_headset_connect.setObjectName(u"pushButton_headset_connect")

        self.gridLayout_2.addWidget(self.pushButton_headset_connect, 1, 0, 1, 2)


        self.verticalLayout_20.addWidget(self.groupBox_4)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.pushButton_start_session = QPushButton(self.frame_2)
        self.pushButton_start_session.setObjectName(u"pushButton_start_session")

        self.verticalLayout_17.addWidget(self.pushButton_start_session)


        self.gridLayout_3.addLayout(self.verticalLayout_17, 0, 0, 1, 1)


        self.verticalLayout_20.addWidget(self.frame_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 596, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"User Information", None))
        self.label_username.setText(QCoreApplication.translate("MainWindow", u"Name", None))
        self.label_age.setText(QCoreApplication.translate("MainWindow", u"Age", None))
        self.label_gender.setText(QCoreApplication.translate("MainWindow", u"Gender", None))
        self.comboBox_gender.setItemText(0, QCoreApplication.translate("MainWindow", u"Male", None))
        self.comboBox_gender.setItemText(1, QCoreApplication.translate("MainWindow", u"Female", None))
        self.comboBox_gender.setItemText(2, QCoreApplication.translate("MainWindow", u"Perfer not to say", None))

        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Session Config", None))
        self.label_trials.setText(QCoreApplication.translate("MainWindow", u"Number of Trials", None))
        self.label_ready.setText(QCoreApplication.translate("MainWindow", u"Ready duration", None))
        self.lineEdit_ready.setText(QCoreApplication.translate("MainWindow", u"1.0", None))
        self.label_baseline.setText(QCoreApplication.translate("MainWindow", u"Baseline duration", None))
        self.lineEdit_baseline.setText(QCoreApplication.translate("MainWindow", u"15.0", None))
        self.checkBox_blinks.setText(QCoreApplication.translate("MainWindow", u"Capture Blinks", None))
        self.label_rest.setText(QCoreApplication.translate("MainWindow", u"Rest duration", None))
        self.lineEdit_rest.setText(QCoreApplication.translate("MainWindow", u"2.0", None))
        self.label_motor.setText(QCoreApplication.translate("MainWindow", u"Motor duration", None))
        self.lineEdit_motor.setText(QCoreApplication.translate("MainWindow", u"4.0", None))
        self.label_cue.setText(QCoreApplication.translate("MainWindow", u"Cue duration", None))
        self.lineEdit_cue.setText(QCoreApplication.translate("MainWindow", u"1.5", None))
        self.label_extra.setText(QCoreApplication.translate("MainWindow", u"Extra Motor duration", None))
        self.lineEdit_extra.setText(QCoreApplication.translate("MainWindow", u"3.0", None))
        self.label_classes.setText(QCoreApplication.translate("MainWindow", u"Classes (Seperated with comma)", None))
        self.lineEdit_classes.setText(QCoreApplication.translate("MainWindow", u"Left, Right", None))
        self.label_savedir.setText(QCoreApplication.translate("MainWindow", u"Save Directory", None))
        self.pushButton_savedir.setText(QCoreApplication.translate("MainWindow", u"Select Folder", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Headset", None))
        self.label_headset_connection.setText(QCoreApplication.translate("MainWindow", u"Connection State:", None))
        self.label_headset_status.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.pushButton_headset_connect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButton_start_session.setText(QCoreApplication.translate("MainWindow", u"Start Session", None))
    # retranslateUi

