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
#Drone: 2 inputs, 4 outputs
#Pro Con: 1 input, 2 outputs

#Fixes Scaling for high resolution monitors. Must be called before App is created
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class SerialComm:
    """
    Python Serial Communication Class. Methods are derived from 
    exisiting pyserial library
    """
    def __init__(self, port, baudrate, timeout):
        """
        Initializes class with port, baudrate, and timeout
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout    
        self.thread = None

    def serialOpen(self):
        """
        Opens serial communication
        """
        self.ser = serial.Serial(port = self.port,
                                 baudrate = self.baudrate,
                                 timeout = self.timeout)
        return(self.ser)
    
    def serialClose(self):
        """
        Closes serial communication
        """
        self.ser.close()

    def serialIsOpen(self):
        """
        Checks if serial communication is open
        """
        return(self.ser.is_open)

    def handshake(self):
        """
        Old method to ensure Arduino and Python are communicating with 
        each other. Hasn't been used for final design.
        """
        self.ser.flushInput()
        self.ser.write(b"H0,\0")
        print("Handshake request sent")
        response = self.ser.readline().decode().replace('\r\n','') #No need for comma delimiter
        
        if(response == "Contact established"):
            print("Handshake success")
        
        else:
            print("Handshake failed")
            self.handshake()

    def flushInput(self):
        """
        Flushes serial input
        """
        self.ser.flushInput()

    def readValues(self):
        """
        Method to send byte (request) so Arduino can send back byte of data.
        Current format of received data is b"T23533228,S0.00,A0.00,Q0.00,\0\r\n"
        T is time 
        S is Setpoint
        A is Response (can be position or velocity)
        Q is PWM Voltage
        """
        self.ser.write(b"R0,\0") 
        arduinoData = self.ser.readline().decode().replace('\r\n','').split(",")
        return arduinoData        

    def readValuesOL(self):
        """
        Note: this will ONLY be for Open-Loop Speed Control
        Arduino will send over ONE really long byte, so use read()
        $ will be used to separate each point, which is in the format of
        D1,T1,P1,V1,I1$D2,T2,P2,V2,I2$\0 
        D is index
        T is microseconds
        P is position
        V is velocity
        I is input voltage
        """
        #print('Received Data')
        arduinoData = self.ser.readline().decode().split("$")#.replace('\r\n','')
        #print(len(arduinoData))
        return arduinoData

    #Below are all methods to write to Arduino. Each are different based on GUI input
    def writePID(self,P,I,D):
        values = f"S0,P{P},I{I},D{D},\0"
        self.ser.write(str.encode(values))
        print("S0:", values)
    #S1
    def writeSetpoint(self,Setpoint):
        values = f"S1,Z{Setpoint},\0"
        self.ser.write(str.encode(values))
        print("S1:", values)
    #S2
    def writeLabType(self,LabType):
        values = f"S2,Y{LabType},\0"
        self.ser.write(str.encode(values))
        print("S2:", values)
    #S3
    def writeController(self,Controller):
        values = f"S3,M{Controller},\0"
        self.ser.write(str.encode(values))
        print("S3:", values)
    #S4
    def writeSampleTime(self,SampleTime):
        values = f"S4,T{SampleTime},\0"
        self.ser.write(str.encode(values))
        print("S4:", values)
    #S5
    def writeSaturation(self,Saturation):
        Saturation = [item for item in Saturation.split(",") if item != ""]
        values = f"S5,L{Saturation[0]},U{Saturation[1]},\0"
        self.ser.write(str.encode(values))
        print("S5:", values)
        
        """
        if len(Saturation) != 2:
            raise ValueError("Saturation field is not inputted properly! Make sure it is a comma separated pair!")
        elif Saturation[0] >= Saturation[1]:
            raise ValueError("Second value should always be GREATER than the first")
        else:
            values = f"S5,L{Saturation[0]},U{Saturation[1]},\0"
            self.ser.write(str.encode(values))
            print("S5:", values)
        """     
    #S6
    def writeOLPWM(self,OLPWM):
        if OLPWM != None:
            values = f"S6,O{OLPWM},\0"
            self.ser.write(str.encode(values))
            print("S6:", values)
    #S7 A is coefficient to x^2, B is coefficient to x, C is coefficient to x^0 (constant)
    def writeFF(self,FF):
        if FF != None:
            FF = [item for item in FF.split(",") if item != ""]
            values = f"S7,A{FF[0]},B{FF[1]},C{FF[2]},\0"
            self.ser.write(str.encode(values))
            print("S7:", values)
            """
            if len(FF) != 3:
                raise ValueError("Feedforward field is not inputted properly! Make sure it is a comma separated triple!")
            else:
                values = f"S7,A{FF[0]},B{FF[1]},C{FF[2]},\0"
                self.ser.write(str.encode(values))
                print("S7:", values)                
            """
    #S8 T is binary (1 is activated, 0 is not)
    def writeOLCharacterization(self):
        values = f"S8,T1,\0"
        self.ser.write(str.encode(values))
        print("S8:", values)
    
    #S10 W is binary (1 is activated, 0 is not)
    def writeAntiWindup(self,AntiWindup):
        values = f"S10,W{AntiWindup},\0"
        self.ser.write(str.encode(values))
        print("S10:", values)


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
    

class Window(QWidget):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.title = "Motor Control"
        self.setWindowTitle(self.title)

        #Application Size
        self.left = 100
        self.top = 100
        self.width = 1000
        self.height = 700
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.thread = None
        self.initUI()

    def initUI(self):

        self.setStyleSheet(qdarkstyle.load_stylesheet())

        horizontalLayout = QHBoxLayout()
        leftVerticalLayout = QVBoxLayout()
        leftVerticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        leftVerticalLayout.setSpacing(6)
        horizontalLayout.addLayout(leftVerticalLayout)
        mainGridLayout = QGridLayout()
        rightVerticalLayout = QVBoxLayout()
        horizontalLayout.addLayout(rightVerticalLayout)
        groupBoxPlotting =  QGroupBox("Plot Settings")
        groupBoxParameters =  QGroupBox("Controller Parameters")

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        groupBoxParameters.setSizePolicy(sizePolicy)
        groupParaGridLayout = QGridLayout()
        groupBoxParameters.setLayout(groupParaGridLayout)        
        
        groupBoxPlotting.setSizePolicy(sizePolicy)
        plotGridLayout = QGridLayout()
        groupBoxPlotting.setLayout(plotGridLayout)

        self.imageLabel = QLabel()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageLabel.sizePolicy().hasHeightForWidth())
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setMinimumSize(QSize(200, 130))
        self.imageLabel.setMaximumSize(QSize(200, 130))
        #Gets the absolute path for the logo for any user (Windows tested)
        script_dir = os.path.dirname(__file__)
        rel_path = r"logo\CUAtHomeLogo-Horz.png"
        abs_file_path = os.path.join(script_dir, rel_path)
        self.imageLabel.setPixmap(QPixmap(abs_file_path).scaled(200, 130, Qt.KeepAspectRatio, Qt.FastTransformation))
        leftVerticalLayout.addWidget(self.imageLabel,alignment=Qt.AlignCenter)
        
        self.LEDLabel = QLabel("Arduino Status",self)
        self.LEDLabel.setMinimumSize(QSize(88, 21))
        self.LEDLabel.setMaximumSize(QSize(88, 21))
        mainGridLayout.addWidget(self.LEDLabel, 0, 0, 1, 1, alignment=Qt.AlignCenter)

        self._led = QLed(self, onColour=QLed.Red, shape=QLed.Circle)
        self._led.clickable = False
        mainGridLayout.addWidget(self._led, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        self._led.value = True
        self._led.setMinimumSize(QSize(15,15))
        self._led.setMaximumSize(QSize(15,15))        

        self.serialOpenButton = QPushButton("Open Serial",self)
        self.serialOpenButton.setCheckable(False)  
        self.serialOpenButton.clicked.connect(self.serialOpenPushed)  
        #self.serialOpenButton.setMinimumSize(QSize(88, 21))       
        self.serialOpenButton.setMaximumSize(QSize(88, 21))
        #print(self.serialOpenButton.sizeHint())
        mainGridLayout.addWidget(self.serialOpenButton, 1, 0, 1, 1)

        self.serialCloseButton = QPushButton("Close Serial",self)
        self.serialCloseButton.setCheckable(False)  
        #self.serialCloseButton.clicked.connect(self.serialClosePushed)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serialCloseButton.sizePolicy().hasHeightForWidth())
        self.serialCloseButton.setSizePolicy(sizePolicy)
        self.serialCloseButton.setMaximumSize(QSize(88, 21))
        #print(self.serialCloseButton.sizeHint())
        mainGridLayout.addWidget(self.serialCloseButton, 1, 1, 1, 1)

        self.startbutton = QPushButton("Start Plot",self)
        self.startbutton.setCheckable(False)  
        #self.startbutton.clicked.connect(self.startbuttonPushed)        
        self.startbutton.setMaximumSize(QSize(88, 21))
        mainGridLayout.addWidget(self.startbutton, 2, 0, 1, 1)

        self.stopbutton = QPushButton("Stop Plot",self)
        self.stopbutton.setCheckable(False)  
        self.stopbutton.clicked.connect(self.stopbuttonPushed)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopbutton.sizePolicy().hasHeightForWidth())
        self.stopbutton.setSizePolicy(sizePolicy)
        self.stopbutton.setMaximumSize(QSize(88, 21))
        mainGridLayout.addWidget(self.stopbutton, 2, 1, 1, 1)
    
        self.clearbutton = QPushButton("Clear Plot",self)
        self.clearbutton.setCheckable(False)
        self.clearbutton.clicked.connect(self.clearbuttonPushed)
        self.clearbutton.setMaximumSize(QSize(88, 21))
        mainGridLayout.addWidget(self.clearbutton, 3, 0, 1, 1)

        self.savebutton = QPushButton("Save Plot",self)
        self.savebutton.setCheckable(False)
        self.savebutton.clicked.connect(self.savebuttonPushed)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.savebutton.sizePolicy().hasHeightForWidth())
        self.savebutton.setSizePolicy(sizePolicy)
        self.savebutton.setMaximumSize(QSize(88, 21))
        mainGridLayout.addWidget(self.savebutton, 3, 1, 1, 1)

        self.settings = QPushButton("Settings",self)
        self.settings.clicked.connect(self.settingsMenu)
        self.settings.setMaximumSize(QSize(1, 21))
        self.settings.setMaximumSize(QSize(300, 21))
        mainGridLayout.addWidget(self.settings, 4, 0, 1, 2)



        self.checkBoxShowAll = QCheckBox("Show All Plots", self)
        self.checkBoxShowAll.setMaximumSize(QSize(88, 21))
        self.checkBoxShowAll.setChecked(True)
        self.checkBoxShowAll.toggled.connect(self.visibilityAll)
        plotGridLayout.addWidget(self.checkBoxShowAll, 0, 0, 1, 1)

        self.checkBoxHideAll = QCheckBox("Hide All Plots", self)
        self.checkBoxHideAll.setChecked(False)
        self.checkBoxHideAll.toggled.connect(self.hideAll)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBoxHideAll.sizePolicy().hasHeightForWidth())
        self.checkBoxHideAll.setSizePolicy(sizePolicy)
        self.checkBoxHideAll.setMaximumSize(QSize(88, 21))
        plotGridLayout.addWidget(self.checkBoxHideAll, 0, 1, 1, 1)

        self.checkBoxPlot1 = QCheckBox("Setpoint", self)
        self.checkBoxPlot1.toggled.connect(self.visibility1)
        self.checkBoxPlot1.setMaximumSize(QSize(88, 21))
        plotGridLayout.addWidget(self.checkBoxPlot1, 1, 0, 1, 1)

        self.checkBoxPlot2 = QCheckBox("Response", self)
        self.checkBoxPlot2.toggled.connect(self.visibility2)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBoxPlot2.sizePolicy().hasHeightForWidth())
        self.checkBoxPlot2.setSizePolicy(sizePolicy)
        self.checkBoxPlot2.setMaximumSize(QSize(88, 21))
        plotGridLayout.addWidget(self.checkBoxPlot2, 1, 1, 1, 1)

        self.checkBoxShowAll.stateChanged.connect(self.checkbox_logic) 
        self.checkBoxHideAll.stateChanged.connect(self.checkbox_logic) 
        self.checkBoxPlot1.stateChanged.connect(self.checkbox_logic) 
        self.checkBoxPlot2.stateChanged.connect(self.checkbox_logic)


        self.maxYLabel = QPushButton("Y max",self)
        self.maxYLabel.setMinimumSize(QSize(100, 20))
        self.maxYLabel.setMaximumSize(QSize(100, 20))
        self.maxYLabel.clicked.connect(self.YMax)
        plotGridLayout.addWidget(self.maxYLabel, 2, 0, 1, 1)

        self.maxYInput = QLineEdit("",self)
        self.maxYInput.setText("100")
        self.maxYInput.setMaximumSize(QSize(88, 21))
        self.maxYInput.setValidator(QDoubleValidator(0.0000, 1000.0000, 4, notation=QDoubleValidator.StandardNotation))
        plotGridLayout.addWidget(self.maxYInput, 2, 1, 1, 1)


        self.LabLabel = QLabel("Lab Type")
        self.LabLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.LabLabel, 0, 0, 1, 1)
        self.LabType = QComboBox()
        self.LabType.addItems(["Position","Speed","Open-Loop"])
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LabType.sizePolicy().hasHeightForWidth())
        self.LabType.setSizePolicy(sizePolicy)
        self.LabType.setMaximumSize(QSize(100, 20))
        self.LabType.activated.connect(self.onlyOpenLoop)
        self.LabType.activated.connect(self.onlySpeedControl)
        self.LabType.activated.connect(self.getLabTypeAxes)
        self.LabType.activated.connect(self.OLCState)
        groupParaGridLayout.addWidget(self.LabType, 0, 1, 1, 1)

        self.ffLabel = QLabel("Feedforward",self)
        self.ffLabel.setMinimumSize(QSize(100, 20))
        self.ffLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.ffLabel, 1, 0, 1, 1)
        self.ffInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ffInput.sizePolicy().hasHeightForWidth())
        self.ffInput.setSizePolicy(sizePolicy)
        self.ffInput.setMaximumSize(QSize(100, 20))
        self.ffInput.setText("0,0,0")
        #triplet of comma separated values
        self.ffInput.setValidator(QRegExpValidator(QRegExp("^(-?\d)*(\.\d{0,6})?,(-?\d)*(\.\d{0,6})?,(-?\d)*(\.\d{0,6})?$")))
        self.ffInput.setEnabled(False)
        groupParaGridLayout.addWidget(self.ffInput, 1, 1, 1, 1)

        self.openLoopLabel = QLabel("OL Voltage (V)",self)
        self.openLoopLabel.setMinimumSize(QSize(100, 20))
        self.openLoopLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.openLoopLabel, 2, 0, 1, 1)
        self.openLoopInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openLoopInput.sizePolicy().hasHeightForWidth())
        self.openLoopInput.setSizePolicy(sizePolicy)
        self.openLoopInput.setMaximumSize(QSize(100, 20))
        self.openLoopInput.setText("12")
        #-12.0000 to 12.0000
        self.openLoopInput.setValidator(QRegExpValidator(QRegExp("^(((-?([0-9]|1[0-1])(\.\d{0,4})?))|-?(12)(\.0{0,4})?)$")))
        self.openLoopInput.setEnabled(False)
        groupParaGridLayout.addWidget(self.openLoopInput, 2, 1, 1, 1)

        self.SetpointLabel = QLabel("Setpoint",self)
        self.SetpointLabel.setMinimumSize(QSize(100, 20))
        self.SetpointLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.SetpointLabel, 3, 0, 1, 1)
        self.SetpointInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SetpointInput.sizePolicy().hasHeightForWidth())
        self.SetpointInput.setSizePolicy(sizePolicy)
        self.SetpointInput.setMaximumSize(QSize(100, 20))
        self.SetpointInput.setValidator(QDoubleValidator())
        self.SetpointInput.setText("100")
        groupParaGridLayout.addWidget(self.SetpointInput, 3, 1, 1, 1)

        self.SaturationLabel = QLabel("Saturation (V)",self)
        self.SaturationLabel.setMinimumSize(QSize(100, 20))
        self.SaturationLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.SaturationLabel, 4, 0, 1, 1)
        self.SaturationInput = QLineEdit("",self)
        self.SaturationInput.setText("-12,12")
        #pair of comma separated numbers, each from -12.0000 to 12.0000
        self.SaturationInput.setValidator(QRegExpValidator(QRegExp("^(-?(((([0-9]|1[0-1])(\.\d{0,4})?))|(12)(\.0{0,4})?|)\,-?(((([0-9]|1[0-1])(\.\d{0,4})?))|(12)(\.0{0,4})?|))$")))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SaturationInput.sizePolicy().hasHeightForWidth())
        self.SaturationInput.setSizePolicy(sizePolicy)
        self.SaturationInput.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.SaturationInput, 4, 1, 1, 1)

        self.SampleTimeLabel = QLabel("PID Sample Time (s)",self)
        self.SampleTimeLabel.setMinimumSize(QSize(110, 20))
        self.SampleTimeLabel.setMaximumSize(QSize(110, 20))
        groupParaGridLayout.addWidget(self.SampleTimeLabel, 5, 0, 1, 1)
        self.SampleTimeInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SampleTimeInput.sizePolicy().hasHeightForWidth())
        self.SampleTimeInput.setSizePolicy(sizePolicy)
        self.SampleTimeInput.setMaximumSize(QSize(100, 20))
        self.SampleTimeInput.setText("0.005")
        #0.0000 to  100.0000
        self.SampleTimeInput.setValidator(QRegExpValidator(QRegExp("^((((\d|[1-9]\d)(\.\d{0,4})?))|(100)(\.0{0,4})?)$"))) 
        groupParaGridLayout.addWidget(self.SampleTimeInput, 5, 1, 1, 1)

        #PID_validator = QRegExpValidator(QRegExp("^((((\d|[1-9]\d)(\.\d{0,4})?))|(100)(\.0{0,4})?)$"))

        self.PCheckBox = QCheckBox("P (V/unit)",self)
        self.PCheckBox.setMaximumSize(QSize(100, 20))
        self.PCheckBox.setChecked(True)
        self.PCheckBox.toggled.connect(self.PCheckBoxLogic)
        groupParaGridLayout.addWidget(self.PCheckBox, 6, 0, 1, 1)
        self.PInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PInput.sizePolicy().hasHeightForWidth())
        self.PInput.setSizePolicy(sizePolicy)
        self.PInput.setMaximumSize(QSize(100, 20))
        #self.PInput.setValidator(PID_validator)
        self.PInput.setText("1")
        groupParaGridLayout.addWidget(self.PInput, 6, 1, 1, 1)

        self.ICheckBox = QCheckBox("I (V/(s*unit))",self)
        self.ICheckBox.setMaximumSize(QSize(100, 20))
        self.ICheckBox.setChecked(True)
        self.ICheckBox.toggled.connect(self.ICheckBoxLogic)
        groupParaGridLayout.addWidget(self.ICheckBox, 7, 0, 1, 1)
        self.IInput = QLineEdit("",self)    
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.IInput.sizePolicy().hasHeightForWidth())
        self.IInput.setSizePolicy(sizePolicy)
        self.IInput.setMaximumSize(QSize(100, 20))
        #self.IInput.setValidator(PID_validator)
        self.IInput.setText("0")
        groupParaGridLayout.addWidget(self.IInput, 7, 1, 1, 1)

        self.DCheckBox = QCheckBox("D (V*s/unit)",self)
        self.DCheckBox.setMaximumSize(QSize(100, 20))
        self.DCheckBox.setChecked(True)
        self.DCheckBox.toggled.connect(self.DCheckBoxLogic)
        groupParaGridLayout.addWidget(self.DCheckBox, 8, 0, 1, 1)
        self.DInput = QLineEdit("",self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DInput.sizePolicy().hasHeightForWidth())
        self.DInput.setSizePolicy(sizePolicy)
        self.DInput.setMaximumSize(QSize(100, 20))
        #self.DInput.setValidator(PID_validator)
        self.DInput.setText("0")
        groupParaGridLayout.addWidget(self.DInput, 8, 1, 1, 1)

        self.ControllerLabel = QLabel("Controller Off/On",self)
        self.ControllerLabel.setMinimumSize(QSize(100, 20))
        self.ControllerLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.ControllerLabel, 9, 0, 1, 1)
        self.ControllerSwitch = Switch(thumb_radius=11, track_radius=8)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ControllerSwitch.sizePolicy().hasHeightForWidth())
        self.ControllerSwitch.setSizePolicy(sizePolicy)
        #self.ControllerSwitch.setMaximumSize(QSize(100, 20))
        self.ControllerSwitch.clicked.connect(self.controllerToggle)
        groupParaGridLayout.addWidget(self.ControllerSwitch, 9, 1, 1, 1, alignment=Qt.AlignCenter)

        self.AntiWindupLabel = QLabel("AW Off/On",self)
        self.AntiWindupLabel.setMinimumSize(QSize(100, 20))
        self.AntiWindupLabel.setMaximumSize(QSize(100, 20))
        groupParaGridLayout.addWidget(self.AntiWindupLabel, 10, 0, 1, 1)
        self.AntiWindSwitch = Switch(thumb_radius=11, track_radius=8)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AntiWindSwitch.sizePolicy().hasHeightForWidth())
        self.AntiWindSwitch.setSizePolicy(sizePolicy)
        #self.AntiWindSwitch.setMaximumSize(QSize(100, 20))
        self.AntiWindSwitch.clicked.connect(self.antiwindupToggle)
        groupParaGridLayout.addWidget(self.AntiWindSwitch, 10, 1, 1, 1, alignment=Qt.AlignCenter)
        


        self.OLCButton = QPushButton("OL Characterization",self)
        #Below line is commented as this button should on be live when
        #serial communication is open
        self.OLCButton.setMaximumSize(QSize(300, 20))
        groupParaGridLayout.addWidget(self.OLCButton, 11, 0, 1, 2)


        self.updateButton = QPushButton("Update Parameters",self)
        #Below line is commented as this button should on be live when
        #serial communication is open
        #self.updateButton.clicked.connect(self.updateParameters)
        self.updateButton.setMaximumSize(QSize(300, 20))
        groupParaGridLayout.addWidget(self.updateButton, 12, 0, 1, 2)

        leftVerticalLayout.addLayout(mainGridLayout)
        leftVerticalLayout.addWidget(groupBoxPlotting)
        leftVerticalLayout.addWidget(groupBoxParameters)
        spacerItem = QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Fixed)
        leftVerticalLayout.addItem(spacerItem)

        #Fixes some spacing issues on GUI
        self.label = QLabel()
        self.label.setMaximumSize(QSize(200, 130))
        self.label.setText("")
        leftVerticalLayout.addWidget(self.label)

        self.graphWidgetOutput = PlotWidget()
        self.graphWidgetInput = PlotWidget()

        #Adds grid lines
        self.graphWidgetOutput.showGrid(x = True, y = True, alpha=None)
        self.graphWidgetInput.showGrid(x = True, y = True, alpha=None)

        #Changes viewboxes of each plot window
        #self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,100], padding=None, update=True, disableAutoRange=True)
        self.graphWidgetInput.setRange(rect=None, xRange=None, yRange=[-13,13], padding=None, update=True, disableAutoRange=True)
        #self.graphWidgetInput.setYRange(0, 100, padding=0)
        
        #Changes background color of graph
        self.graphWidgetOutput.setBackground((0,0,0))
        self.graphWidgetInput.setBackground((0,0,0))

        #Adds a legend after data starts to plot NOT before
        self.legendOutput = self.graphWidgetOutput.addLegend()
        self.legendInput = self.graphWidgetInput.addLegend()
        #self.legend.setParentItem(self.graphWidgetOutput)

        self.graphWidgetInput.setLabel('left',"<span style=\"color:white;font-size:16px\">Voltage</span>")
        self.graphWidgetInput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.graphWidgetInput.setTitle("Input Voltage", color="w", size="12pt")

        rightVerticalLayout.addWidget(self.graphWidgetOutput)
        rightVerticalLayout.addWidget(self.graphWidgetInput)

        self.setLayout(horizontalLayout)

        #Plot time update settings
        self.timer = QTimer()
        self.timer.setInterval(50) #Changes the plot speed. Defaulted to 50. Can be placed in startbuttonPushed() method
        self.initialState()
        time.sleep(2)
        try:
            self.timer.timeout.connect(self.updatePlot)
        except AttributeError:
            print("Something went wrong")
        #self.show()

    #Checkbox logic
    def checkbox_logic(self, state): 
  
        # checking if state is checked 
        if state == Qt.Checked: 
  
            if self.sender() == self.checkBoxShowAll: 
                self.checkBoxHideAll.setChecked(False) 
                self.checkBoxPlot1.setChecked(False)
                self.checkBoxPlot2.setChecked(False)
  
            elif self.sender() == self.checkBoxHideAll:
                self.checkBoxShowAll.setChecked(False) 
                self.checkBoxPlot1.setChecked(False) 
                self.checkBoxPlot2.setChecked(False)   
            
            elif self.sender() == self.checkBoxPlot1: 
                self.checkBoxShowAll.setChecked(False) 
                self.checkBoxHideAll.setChecked(False)
                self.checkBoxPlot2.setChecked(False)

            elif self.sender() == self.checkBoxPlot2:
                self.checkBoxShowAll.setChecked(False) 
                self.checkBoxHideAll.setChecked(False)
                self.checkBoxPlot1.setChecked(False)

    def YMax(self):
        """
        Changes range of the Output Graph Viewbox to be constrained between -1 to y specified
        """
        if self.maxYInput.text() != "":
            try:
                self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,float(self.maxYInput.text())], padding=None, update=True, disableAutoRange=True)
            except:
                pass

    #Setup for Serial Open and Serial Close is that only 1 button can be active at a time
    def serialOpenPushed(self):
        #Try/except/else/finally statement is to check whether settings menu was opened/changed
        try:
            self.size = self.serial_values[3] #Value from settings. Windows data
            self.serialInstance = SerialComm(self.serial_values[0],self.serial_values[1],self.serial_values[2])
            self.serialInstance.serialOpen()
            time.sleep(2)
            print("Serial successfully open!")

            if self.serialInstance.serialIsOpen() == True:
                self._led.onColour = QLed.Green   
        except AttributeError:
            print("Settings menu was never opened")
        except TypeError:
            print("Settings menu was opened, however OK was not pressed to save values")

        #self.serialInstance.handshake()
        #self.serialInstance.flushInput()
        try:
            self.serialInstance.writePID(self.PIDInput()["P"],
                                         self.PIDInput()["I"],
                                         self.PIDInput()["D"])
            self.serialInstance.writeSetpoint(self.getSetpointValue())
            self.serialInstance.writeLabType(self.getLabType())        
            self.serialInstance.writeController(self.getControllerState())
            self.serialInstance.writeSampleTime(self.getSampleTimeValue())
            self.serialInstance.writeSaturation(self.getSaturationValue())
            self.serialInstance.writeOLPWM(self.getOLPWMValue())
            self.serialInstance.writeFF(self.getFFValue())
            self.serialInstance.writeAntiWindup(self.getAntiWindupState())

        except AttributeError:
            print("Some fields are empty. Recheck then try again")
        else: 
            self.serialOpenButton.clicked.disconnect(self.serialOpenPushed)
            self.updateButton.clicked.connect(self.updateParameters)
            #self.OLCButton.clicked.connect(self.OLCState)
            self.serialCloseButton.clicked.connect(self.serialClosePushed)
            self.startbutton.clicked.connect(self.startbuttonPushed)
            self.sc = QShortcut(QKeySequence("Return"), self)
            self.sc.activated.connect(self.updateParameters)

    def serialClosePushed(self):
        if self.serialInstance.serialIsOpen() == True:
            self.serialInstance.serialClose()
            print("Serial was open. Now closed")   
        elif self.serialInstance.serialIsOpen() == False:
            print("Serial is already closed")
        
        try:
            self.serialOpenButton.clicked.connect(self.serialOpenPushed)
        except:
            print("Serial Open button already connected")
        try:
            self.updateButton.clicked.disconnect(self.updateParameters)
            self.sc.activated.connect(self.updateParameters)
        except:
            print("Update Button already disconnected")
        self._led.onColour = QLed.Red

        self.serialCloseButton.clicked.disconnect(self.serialClosePushed)

    #Resets data arrays and starts plotting. Disables itself after clicking
    def startbuttonPushed(self):
        print("Recording Data")
        self.timer.start()
        self.curve()
        self.startbutton.clicked.disconnect(self.startbuttonPushed)
        """
        if self.thread == None:
            self.thread = threading.Thread()
            try:
                self.thread.start(target=self.temptest)
            except:
                pass
        """

    #Stops timer and ends plotting
    def stopbuttonPushed(self):
        self.timer.stop()
        print("Stopping Data Recording")
        """
        try:
            self.thread.join()
        except:
            pass
        """

    #Resets both plotting windows and reenables Start Button
    def clearbuttonPushed(self):
        self.graphWidgetOutput.clear()
        self.graphWidgetInput.clear()
        #Come back to this
        self.graphWidgetOutput.addLegend()
        self.graphWidgetInput.addLegend()
        self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,100], padding=None, update=True, disableAutoRange=True)
        self.graphWidgetInput.setRange(rect=None, xRange=None, yRange=[-13,13], padding=None, update=True, disableAutoRange=True)
        self.startbutton.clicked.connect(self.startbuttonPushed)
        self.initialState() #Reinitializes arrays in case you have to retake data
        print("Cleared All Graphs")

    #Dumps data into a csv file to a selected path
    def savebuttonPushed(self):
        if str(self.LabType.currentText()) != "Open-Loop":
            self.createCSV()
        else: 
            self.createCSVOL()
        path = QFileDialog.getSaveFileName(self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if path[0] != '':
            with open(path[0], 'w', newline = '') as csvfile:
                csvwriter = csv.writer(csvfile)
                #csvwriter.writerow(self.header)
                csvwriter.writerows(self.data_set)
        print("Saved All Data")

    #Creates csv data
    def createCSV(self):
        self.header = ['time', 'setpoint', 'response', 'voltage', '', 'Parameters']
        self.parameters_label = ["Labtype", "Feedforward", "OL Voltage", "Setpoint", "Saturation", "PID Sample Time", "P", "I", "D", "Controller State"]
        self.data_set = zip_longest(*[self.time,self.y1,self.y2,self.y3,[],self.parameters_label,self.parameters], fillvalue="")

    def createCSVOL(self):
        self.header = ["index", "time (ms)", "position", "velocity", "voltage", '', "Parameters"]
        #self.parameters_label = ["Labtype", "Feedforward", "OL Voltage", "Setpoint", "Saturation", "PID Sample Time", "P", "I", "D", "Controller State"]
        self.data_set = zip_longest(*[self.d,self.time,self.position,self.velocity,self.voltage], fillvalue="")#[],self.parameters_label,self.parameters], fillvalue="")


    #Initilizes lists/arrays and initial values for the .csv
    def initialState(self):
        self.buffersize = 500 #np array size that is used to plot data
        self.step = 0 #Used for repositioning data in plot window to the left
        self.parameters = [ self.LabType.currentText(),
                            self.getFFValue(),
                            self.getOLPWMValue(),
                            self.getSetpointValue(),
                            self.getSaturationValue(),
                            self.getSampleTimeValue(),
                            self.PIDInput()["P"],
                            self.PIDInput()["I"],
                            self.PIDInput()["D"],     
                            self.getControllerState(),
                            self.getAntiWindupState()
                            ]

        #Data buffers. What is being plotted in the 2 windows
        self.time_zeros = np.zeros(self.buffersize+1, float)
        self.y1_zeros = np.zeros(self.buffersize+1, float)
        self.y2_zeros = np.zeros(self.buffersize+1, float)
        self.y3_zeros = np.zeros(self.buffersize+1, float)

        #Complete data. What will be written to the csv file
        self.time = list()
        self.y1 = list()
        self.y2 = list()
        self.y3 = list()

        #only here for when the start button is pressed, and user didn't change 
        #labtype from default (position)
        self.getLabTypeAxes()

    #Initializes data# to have specific attributes
    def curve(self):
        pen1 = pg.mkPen(color = (255, 0, 0), width=1)
        pen2 = pg.mkPen(color = (0, 255, 0), width=1)
        pen3 = pg.mkPen(color = (0, 255, 255), width=1)

        self.data1 = self.graphWidgetOutput.plot(pen = pen1, name="Setpoint") #Setpoint
        self.data2 = self.graphWidgetOutput.plot(pen = pen2, name="Response") #Response
        self.data3 = self.graphWidgetInput.plot(pen = pen3, name="Input Voltage") #8 bit number to Voltage

    #Connected to timer to update plot. Incoming data is in the form of timestamp,data1,data2...    
    def updatePlot(self):
        fulldata = self.serialInstance.readValues()
        """
        if self.thread == None:
            self.thread = threading.Thread(target=self.serialInstance.readValues())
            self.thread.start()
            #self.thread.join()
            print("thread")
            que = queue.Queue()
            fulldata = que.get()

        elif self.thread.is_alive() == True:
            fulldata = que.get()
        """

        self.step = self.step + 1
        """
        New data format reading. Based off of GCode. Since incoming serial data
        is in the form b"T23533228,S0.00,A0.00,Q0.00,\0\r\n", this parsing searches for specific starting letter,
        converts from list to string as the list is length 1, then removes the starting character. 
        #result = [item for item in example if item.startswith('T')][0][1:]
        """

        """
        Serial command protocol
        H0 - Handshake
        R0 - Request data dependent on lab type
        S0,P#,I#,D# - Set PID gains on arduino
        S1,Z# - Set the setpoint of the controller
        S2,Y# - Lab type 0-angle, 1-ang_velocity, 2-openloop
        S3,M# - Turn controller on/off
        S4,T# - Set sample time
        S5,L#,U# - Set lower and upper controller output limits
        S6,O# - Open loop PWM
        
        Data to python protocol
        T# - time in micros
        S# - setpoint
        A# - value, angle or ang_speed dependent on labtype
        Q# - PMW
        """

        try:
            time_index = int(self.time_zeros[self.buffersize])
            self.time_zeros[time_index] = self.time_zeros[time_index+self.size] = float(self.gcodeParsing("T",fulldata))
            self.time_zeros[self.buffersize] = time_index = (time_index+1) % self.size
            self.time.append(self.gcodeParsing("T",fulldata))            
        except ValueError:
            print("Couldn't parse value")
        except IndexError:
            print("Couldn't parse index. Skipping point")

        try:
            i = int(self.y1_zeros[self.buffersize])
            self.y1_zeros[i] = self.y1_zeros[i+self.size] = float(self.gcodeParsing("S",fulldata))
            self.y1_zeros[self.buffersize] = i = (i+1) % self.size
            self.y1.append(self.gcodeParsing("S",fulldata))
        except ValueError:
            print("Couldn't parse")
        except IndexError:
            print("Couldn't parse index. Skipping point")

        try:
            j = int(self.y2_zeros[self.buffersize])
            self.y2_zeros[j] = self.y2_zeros[j+self.size] = float(self.gcodeParsing("A",fulldata))
            self.y2_zeros[self.buffersize] = j = (j+1) % self.size
            self.y2.append(self.gcodeParsing("A",fulldata))
        except ValueError:
            print("Couldn't parse")
        except IndexError:
            print("Couldn't parse index. Skipping point")
        
        try:
            k = int(self.y3_zeros[self.buffersize])
            self.y3_zeros[k] = self.y3_zeros[k+self.size] = float(self.gcodeParsing("Q",fulldata))
            self.y3_zeros[self.buffersize] = k = (k+1) % self.size
            self.y3.append(self.gcodeParsing("Q",fulldata))
        except ValueError:
            print("Couldn't parse")
        except IndexError:
            print("Couldn't parse index. Skipping point")

        self.data1.setData(self.time_zeros[time_index:time_index+self.size],self.y1_zeros[i:i+self.size])
        self.data1.setPos(self.step,0)
        self.data2.setData(self.time_zeros[time_index:time_index+self.size],self.y2_zeros[j:j+self.size])
        self.data2.setPos(self.step,0)
        self.data3.setData(self.time_zeros[time_index:time_index+self.size],self.y3_zeros[k:k+self.size])
        self.data3.setPos(self.step,0)

    def gcodeParsing(self,letter,input_list):
        result = [_ for _ in input_list if _.startswith(letter)][0][1:]
        return(result)

    #Below 4 change visibility of data# in the curves() method
    def visibilityAll(self):
        showall = self.sender()
        if showall.isChecked() == True:
            self.data1.setVisible(True)
            self.data2.setVisible(True) 

    def hideAll(self):
        disappearall = self.sender()
        if disappearall.isChecked() == True:
            self.data1.setVisible(False)
            self.data2.setVisible(False)

    def visibility1(self):
        test1 = self.sender()
        if test1.isChecked() == True:
            self.data1.setVisible(True)
            self.data2.setVisible(False)
    
    def visibility2(self):
        test2 = self.sender()
        if test2.isChecked() == True:
            self.data2.setVisible(True)
            self.data1.setVisible(False)

    #Class instance of settings menu. Creates a dialog (popup)
    def settingsMenu(self):
        self.settingsPopUp = SettingsClass()
        self.settingsPopUp.show()
        #self.settingsPopUp.exec()
        self.serial_values = self.settingsPopUp.getDialogValues()

    def PCheckBoxLogic(self):
        test1 = self.sender()
        if test1.isChecked() == True:
            self.PInput.setEnabled(True)
        elif test1.isChecked() == False:
            self.PInput.setEnabled(False)

    def ICheckBoxLogic(self):
        test1 = self.sender()
        if test1.isChecked() == True:
            self.IInput.setEnabled(True)
        elif test1.isChecked() == False:
            self.IInput.setEnabled(False)

    def DCheckBoxLogic(self):
        test1 = self.sender()
        if test1.isChecked() == True:
            self.DInput.setEnabled(True)
        elif test1.isChecked() == False:
            self.DInput.setEnabled(False)

    #GCode format for PID values (float)
    def PIDInput(self):
        if self.PInput.text() == "" or self.PCheckBox.checkState() == False:
            self.Pvalue = 0
        else:
            self.Pvalue = self.PInput.text()

        if self.IInput.text() == "" or self.ICheckBox.checkState() == False:
            self.Ivalue = 0
        else:
            self.Ivalue = self.IInput.text()

        if self.DInput.text() == "" or self.DCheckBox.checkState() == False:
            self.Dvalue = 0
        else:
            self.Dvalue = self.DInput.text()
        return({
                "P": self.Pvalue, 
                "I": self.Ivalue, 
                "D": self.Dvalue
                })

    #GCode format for Setpoint (float?)
    def getSetpointValue(self):
        SetpointValue = self.SetpointInput.text()
        if SetpointValue == "":
            raise ValueError("Setpoint Field is empty. Enter in a value")
                    
        return(SetpointValue)

    #GCode format for Labtype (int)
    def getLabType(self):
        test1 = str(self.LabType.currentText())
        if test1 == "Position":
            return("0")
        
        elif test1 =="Speed":
            return("1")

        elif test1 =="Open-Loop":
            return("2")

    #Changes axes labels depending on what lab is selected
    def getLabTypeAxes(self):
        inputType = str(self.LabType.currentText())
        if inputType == "Position":
            self.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">&theta; (unit = degrees)</span>")
            self.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
            self.graphWidgetOutput.setTitle("Position Control", color="w", size="12pt")
            self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,100], padding=None, update=True, disableAutoRange=True)
        elif inputType == "Speed":
            self.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">&omega; (unit = RPM)</span>")
            self.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
            self.graphWidgetOutput.setTitle("Speed Control", color="w", size="12pt")
            self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,550], padding=None, update=True, disableAutoRange=True)
        elif inputType == "Open-Loop":
            self.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">&omega; (unit = RPM)</span>")
            self.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (ms)</span>")
            self.graphWidgetOutput.setTitle("Open Loop Speed Control", color="w", size="12pt")
            self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,550], padding=None, update=True, disableAutoRange=True)

    #Enables/disables field for the feedforward regression
    def onlySpeedControl(self):
        test1 = str(self.LabType.currentText())
        if test1 == "Speed":
            self.ffInput.setEnabled(True)
        else:
            self.ffInput.setEnabled(False)

    #Enables/disables field for the open loop voltage
    def onlyOpenLoop(self):
        test1 = str(self.LabType.currentText())
        if test1 == "Open-Loop":
            self.openLoopInput.setEnabled(True)
        else:
            self.openLoopInput.setEnabled(False)

    #This method will only be activated once serial is starting up
    def getControllerState(self):
        if self.ControllerSwitch.isChecked() == False:
            return("0")
        elif self.ControllerSwitch.isChecked() == True:
            return("1")


    #This method can be activated as many times as long as Led is Green.
    # which is when serial communication is open. Otherwise it will do nothing
    def controllerToggle(self):
        test1 = self.sender()
        if self._led.onColour == QLed.Green:
            if test1.isChecked() == False:
                self.serialInstance.writeController("0")

            elif test1.isChecked() == True:
                self.serialInstance.writeController("1")

    #This method will only be activated once serial is starting up
    def getAntiWindupState(self):
        if self.AntiWindSwitch.isChecked() == False:
            return("0")
        elif self.AntiWindSwitch.isChecked() == True:
            return("1")


    #This method can be activated as many times as long as Led is Green
    #AND lab type is position/speed
    # which is when serial communication is open. Otherwise it will do nothing
    def antiwindupToggle(self):
        test1 = self.sender()
        if self._led.onColour == QLed.Green:
            if test1.isChecked() == False:
                self.serialInstance.writeAntiWindup("0")
            
            elif test1.isChecked() == True:
                self.serialInstance.writeAntiWindup("1")


    #GCode format for Sample Time
    def getSampleTimeValue(self):
        SampleTimeValue = self.SampleTimeInput.text()
        if SampleTimeValue == "":
            raise ValueError("Sample Time Field is empty. Enter in a value")

        return(SampleTimeValue)

    #GCode format for Saturation (float?)
    def getSaturationValue(self):
        SaturationValue = self.SaturationInput.text()
        if SaturationValue == "":
            raise ValueError("Saturation Field is empty. Enter in a comma separated value")
                    
        return(SaturationValue)

    def getOLPWMValue(self):
        #If Labtype isn't OL or Input Field is disabled, then returns None. 
        #In SerialComm.writeOLPWM(), checks if input value is None. 
        #If it is None, doesn't write anything, else it does

        if self.openLoopInput.isEnabled() == True:
            OLPWMValue = self.openLoopInput.text()
            if OLPWMValue == "":
                raise ValueError("OLPWM Field is empty. Enter in a value")
            return(OLPWMValue)

        elif self.openLoopInput.isEnabled() == False:
            return None

    def getFFValue(self):
        #If Labtype isn't Speed Control or Input Field is disabled, then returns None.
        #In SerialComm.writeFF(), checks if input value is None.
        #If it is None, doesn't write anything, else it does

        if self.ffInput.isEnabled() == True:
            ffValue = self.ffInput.text()
            if ffValue == "":
                raise ValueError("Feedforward Field is empty. Enter in a triplet of comma separated values")
            return(ffValue)

    def OLCState(self):
        inputType = str(self.LabType.currentText())
        if inputType == "Open-Loop":
            self.OLCButton.clicked.connect(self.OLGraph)
        else:
            try:
                self.OLCButton.clicked.disconnect(self.OLGraph)
            except:
                pass


    def OLGraph(self):
        """
        Note, this is a static plot. Will not be used for realtime, besides each time the OL Characterization button is pressed
        """
        self.timer.stop()
        self.graphWidgetOutput.clear()
        self.graphWidgetInput.clear()
        self.serialInstance.writeOLCharacterization()
        
        # Sleep for 2 seconds to wait for arduino to finish sending data over serial to prevent empty plotting
        time.sleep(2)
        
        fulldata = self.serialInstance.readValuesOL()
        print(fulldata)

        self.d = self.gcodeParsingOL("D",fulldata)
        self.time = self.gcodeParsingOL("T",fulldata)
        self.position = self.gcodeParsingOL("P",fulldata)
        self.velocity = self.gcodeParsingOL("V",fulldata)
        self.voltage = self.gcodeParsingOL("I",fulldata)
        
        print(self.velocity)

        pen1 = pg.mkPen(color = (0, 255, 0), width=1)
        pen2 = pg.mkPen(color = (0, 255, 255), width=1)
        

        self.graphWidgetOutput.plot(self.time, self.velocity, pen=pen1, name="Response")
        self.graphWidgetInput.plot(self.time, self.voltage, pen=pen2, name="Voltage")
        

    def gcodeParsingOL(self,letter,input_list):
        empty_list = list()
        for i in input_list:
            i = i.split(",")
            for j in i:
                if j.startswith(letter):
                    empty_list.append(float(j[1:]))    
        return(empty_list)


    def updateParameters(self):
        #if self.serialInstance.serialIsOpen() == True:
        try:
            self.serialInstance.writePID(self.PIDInput()["P"],
                                         self.PIDInput()["I"],
                                         self.PIDInput()["D"])
            self.serialInstance.writeSetpoint(self.getSetpointValue())
            self.serialInstance.writeLabType(self.getLabType())        
            self.serialInstance.writeSampleTime(self.getSampleTimeValue())
            self.serialInstance.writeSaturation(self.getSaturationValue())
            self.serialInstance.writeOLPWM(self.getOLPWMValue())
            self.serialInstance.writeFF(self.getFFValue())

        except AttributeError:
            print("Some fields are empty when trying to update values. Recheck then try again")

def main():
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()