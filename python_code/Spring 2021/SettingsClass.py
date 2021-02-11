import sys 
import os
import time
from PyQt5.QtGui import QDoubleValidator, QKeySequence, QPixmap, QRegExpValidator, QIcon
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QComboBox, 
QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QGridLayout, QDialog, 
QLabel, QLineEdit, QDialogButtonBox, QFileDialog, QSizePolicy, QLayout,
QSpacerItem, QGroupBox, QShortcut)
from PyQt5.QtCore import Qt, QTimer, QRegExp, QCoreApplication, QSize, QRunnable, QThread, QThreadPool
import serial
import serial.tools.list_ports
import numpy as np
import qdarkstyle #has some issues on Apple devices and high dpi monitors
from settings_ui import Ui_Dialog

class SettingsClass(QDialog):
    """
    Settings Class. Creates inputs to SerialComm class 
    """
    def __init__(self, *args, **kwargs):
        super(SettingsClass, self).__init__(*args, **kwargs)
        
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.setWindowTitle("Settings")
        self.setModal(True) #Makes you close out of settings no matter what
        self.ui.baudrate.setCurrentIndex(2) #1000000

        self.list_port()
        self.initialConnections()
        self.initialValidators()

    def initialConnections(self):
        '''
        Allows for "Ok" and "Cancel" to work
        '''
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def initialValidators(self):
        '''
        Assigns validators to textboxes to prevent wrong text
        '''
        timeout_validator = QDoubleValidator(0.0000, 5.0000, 4, notation=QDoubleValidator.StandardNotation)
        self.ui.timeout.setValidator(timeout_validator)

        regex = QRegExp("([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|1000)") #takes 1-1000 as input
        datawindowsize_validator = QRegExpValidator(regex,self)
        self.ui.datawindowsize.setValidator(datawindowsize_validator)

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
        self.ui.ports.addItems(arduino_ports)

    def getDialogValues(self):
        """
        Returns inputs to be used in SerialComm class in the main window
        """
        if self.exec_() == QDialog.Accepted:
            self.com_value = str(self.ui.ports.currentText())
            self.baudrate_value = str(self.ui.baudrate.currentText())
            self.timeout_value = float(self.ui.timeout.text())
            self.datawindowsize_value = int(self.ui.datawindowsize.text())
            self.samplingrate_value = float(self.ui.samplingrate.text())
            self.sampletime_value = int(self.ui.sampletime.text())

            print("Settings Menu Saved!")
            val = {"COM": self.com_value,
                   "Baud Rate": self.baudrate_value,
                   "Timeout": self.timeout_value,
                   "Data Window": self.datawindowsize_value,
                   "Sampling Rate": self.samplingrate_value,
                   "Sample Time": self.sampletime_value
                   }
            return(val)
            
        else:
            print("Settings Menu Closed. No options were saved!")
    