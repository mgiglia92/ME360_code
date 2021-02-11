import sys 
import os
import time
from PyQt5.QtGui import QDoubleValidator, QKeySequence, QPixmap, QRegExpValidator, QIcon
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QComboBox, 
QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QGridLayout, QDialog, 
QLabel, QLineEdit, QDialogButtonBox, QFileDialog, QSizePolicy, QLayout,
QSpacerItem, QGroupBox, QShortcut)
from PyQt5.QtCore import Qt, QTimer, QRegExp, QCoreApplication, QSize, QRunnable, QThread, QThreadPool
from pyqtgraph import PlotWidget, plot, ScatterPlotItem
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import numpy as np
import csv
from itertools import zip_longest
import qdarkstyle #has some issues on Apple devices and high dpi monitors
from QLed import QLed #LED indicator on GUI
from QSwitch import Switch #toggle switch
import threading
import multiprocessing
import queue

class SettingsClass(QDialog):
    """
    Settings Class. Creates inputs to SerialComm class 
    """
    def __init__(self, *args, **kwargs):
        super(SettingsClass, self).__init__(*args, **kwargs)
        
        self.title = "Settings"
        self.setWindowTitle(self.title)        
        self.setModal(True)
        self.width = 200
        self.height = 200
        self.setFixedSize(self.width, self.height)
        self.initUI()
        
    def initUI(self):
        """
        Creates UI of Settings
        """
        #self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        mainLayout = QHBoxLayout() 
        leftFormLayout = QFormLayout()
        mainLayout.addLayout(leftFormLayout,100)

        self.port_label = QLabel("Ports:",self)
        
        self.port = QComboBox(self)
        self.port.setFixedWidth(100)
        self.list_port()

        self.baudrate_label = QLabel("Baud Rate:",self)
        self.baudrate = QComboBox(self)
        self.baudrate.setFixedWidth(100)
        self.baudrate.addItems(["9600","115200","250000","500000"])
        self.baudrate.setCurrentIndex(3)
        self.baudrate.SizeAdjustPolicy(1)
        
        self.timeout_label = QLabel("Timeout:",self)
        self.timeout = QLineEdit(self)
        self.timeout.setFixedWidth(100)
        self.timeout.setText("0.1")
        #self.timeout.setText("1")

        timeout_validator = QDoubleValidator(0.0000, 5.0000, 4, notation=QDoubleValidator.StandardNotation)
        self.timeout.setValidator(timeout_validator)
         
        regex = QRegExp("([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|1000)") #takes 1-1000 as input
        sampnum_buffernum_validator = QRegExpValidator(regex,self)

        self.samplenum_label = QLabel("Sample Size:",self)
        self.samplenum = QLineEdit(self)
        self.samplenum.setFixedWidth(100)
        self.samplenum.setText("150") #Default is 150
        self.samplenum.setValidator(sampnum_buffernum_validator)

        #Ok and cancel button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
       
        leftFormLayout.addRow(self.port_label,self.port)
        leftFormLayout.addRow(self.baudrate_label,self.baudrate)
        leftFormLayout.addRow(self.timeout_label,self.timeout)
        leftFormLayout.addRow(self.samplenum_label,self.samplenum)
        #leftFormLayout.addRow(self.buffernum_label,self.buffernum)
        leftFormLayout.addRow(buttonBox)

        self.setLayout(mainLayout)

    def list_port(self): 
        """
        Determines what COM Ports are available
        """
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' or 'tty' in p.description  
        ]
        if not arduino_ports:
            raise IOError("No Arduino found. Replug in USB cable and try again.")
        arduino_ports.sort(key=lambda s: (s[:-2], int(s[-2:])) if s[-2] in '0123456789' else (s[:-1], int(s[-1:])))
        self.port.addItems(arduino_ports)

    def getDialogValues(self):
        """
        Returns inputs to be used in SerialComm class in the main window
        """
        if self.exec_() == QDialog.Accepted:
            self.com_value = str(self.port.currentText())
            self.baudrate_value = str(self.baudrate.currentText())
            self.timeout_value = float(self.timeout.text())
            self.samplenum_value = int(self.samplenum.text())
            print("Settings Menu Saved!")
            return([self.com_value, self.baudrate_value, self.timeout_value, self.samplenum_value])#, self.buffernum_value])
            
        else:
            print("Settings Menu Closed. No options were saved!")
    