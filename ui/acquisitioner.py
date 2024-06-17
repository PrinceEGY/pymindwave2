# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acqeqFtgY.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    Qt,
)
from PySide6.QtGui import (
    QFont,
)
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QWidget,
)


class Ui_AcquisitionWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(821, 663)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.widget_3 = QWidget(self.centralwidget)
        self.widget_3.setObjectName("widget_3")

        self.gridLayout.addWidget(self.widget_3, 2, 1, 1, 1)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")

        self.gridLayout.addWidget(self.widget_2, 1, 2, 1, 1)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName("frame")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setStyleSheet(
            "QFrame{\n" "	background-color: rgb(255, 255, 0);\n" "}"
        )
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_class = QLabel(self.frame)
        self.label_class.setObjectName("label_class")
        self.label_class.setEnabled(True)
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_class.sizePolicy().hasHeightForWidth())
        self.label_class.setSizePolicy(sizePolicy2)
        font = QFont()
        font.setBold(True)
        self.label_class.setFont(font)
        self.label_class.setStyleSheet(
            "QLabel{\n" "color: Red;\n" "font-size: 48px;\n" "}"
        )
        self.label_class.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_class, 0, 0, 1, 1)

        self.gridLayout.addWidget(self.frame, 1, 1, 1, 1)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName("widget")

        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)

        self.widget_4 = QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")

        self.gridLayout.addWidget(self.widget_4, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.label_class.setText(
            QCoreApplication.translate("MainWindow", "Class", None)
        )

    # retranslateUi


class AcquisitionWindow(QMainWindow):
    def __init__(self, headset):
        super(AcquisitionWindow, self).__init__()
        self.ui = Ui_AcquisitionWindow()
        self.ui.setupUi(self)
        self.headset = headset
