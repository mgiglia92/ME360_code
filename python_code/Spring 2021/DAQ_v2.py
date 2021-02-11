import sys
import os
import time
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import qdarkstyle #has some issues on Apple devices and high dpi monitors
import CoursesDataClass
from SettingsClass import *
from main_ui import Ui_MainWindow
from QLed import QLed
from PyQt5.QtGui import QDoubleValidator, QKeySequence, QPixmap, QRegExpValidator, QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QComboBox, 
QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QGridLayout, QDialog, 
QLabel, QLineEdit, QDialogButtonBox, QFileDialog, QSizePolicy, QLayout,
QSpacerItem, QGroupBox, QShortcut, QMainWindow)
from PyQt5.QtCore import QDir
import numpy as np
import csv
from itertools import zip_longest
import threading
import queue
import colorama

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class Window(QMainWindow):
    #colorama.init()
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.currentItemsSB = [] # Used to store variables to be displayed in status bar at the bottom right
        self.verbose = True # Initialization. Used in the thread generated in application

        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.getLogo()
        self.getFonts()
        self.initalConnections()
        self.initialGraphSettings()
        self.arduinoStatusLed()
        self.initialTimer()
        self.initialState()
        
        self.ui.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">Speed (m/s)</span>")
        self.ui.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetOutput.setTitle("Speed", color="w", size="12pt")

        self.ui.graphWidgetInput.setLabel('left',"<span style=\"color:white;font-size:16px\">°C</span>")
        self.ui.graphWidgetInput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetInput.setTitle("Temperature", color="w", size="12pt")
        # self.currentValueSB(self.course)
        
        # self.course = "Sound"
        self.serial_values = {'COM':'COM3','Baud Rate':'1000000','Timeout':0.1,'Data Window':150,'Sampling Rate':0.00002,'Sample Time':1}
        
    def getLogo(self):
        script_dir = os.path.dirname(__file__)
        logo_rel_path = r"logo\CUAtHomeLogo-Horz.png"
        logo_abs_file_path = os.path.join(script_dir, logo_rel_path)
        self.ui.imageLabel.setPixmap(QPixmap(logo_abs_file_path).scaled(200, 130, 
                                                                   Qt.KeepAspectRatio, 
                                                                   Qt.FastTransformation))
                                                                   
    def getFonts(self):
        script_dir = os.path.dirname(__file__)
        font_rel_path = r"fonts\Roboto" 
        font_abs_file_path = os.path.join(script_dir, font_rel_path)

        for f in os.listdir(font_abs_file_path):
            if f.endswith("ttf"):
                QFontDatabase.addApplicationFont(os.path.join(font_abs_file_path,f))
        #print(QFontDatabase().families())
        
    def arduinoStatusLed(self):
        self._led = QLed(self, onColour=QLed.Red, shape=QLed.Circle)
        self._led.clickable = False
        self._led.value = True
        self._led.setMinimumSize(QSize(15, 15))
        self._led.setMaximumSize(QSize(15, 15))     
        self.statusLabel = QLabel("Arduino Status:")
        self.statusLabel.setFont(QFont("Roboto", 12)) 

        self.statusBar().addWidget(self.statusLabel)
        #self.statusBar().reformat()
        self.statusBar().addWidget(self._led)
        
    def initalConnections(self):
        """
        Menubar
        """
        # self.ui.actionStatics.triggered.connect(self.staticsPushed)
        # self.ui.actionBeam.triggered.connect(self.beamPushed)
        # self.ui.actionSound.triggered.connect(self.soundPushed)
        #self.ui.menubar.triggered.connect(self.soundPushed) # COME BACK TO THIS
        """
        7 Main Buttons
        """
        self.ui.serialOpenButton.clicked.connect(self.serialOpenPushed)  
        #self.ui.serialCloseButton.clicked.connect(self.serialClosePushed)
        #self.ui.startbutton.clicked.connect(self.startbuttonPushed)        
        self.ui.stopbutton.clicked.connect(self.stopbuttonPushed) # this is originally enabled
        self.ui.savebutton.clicked.connect(self.savebuttonPushed)
        self.ui.clearbutton.clicked.connect(self.clearbuttonPushed)
        self.ui.settings.clicked.connect(self.settingsMenu)
        
    def initialGraphSettings(self):
        self.ui.graphWidgetOutput.showGrid(x=True, y=True, alpha=None)
        self.ui.graphWidgetInput.showGrid(x=True, y=True, alpha=None)
        self.ui.graphWidgetOutput.setBackground((0, 0, 0))
        self.ui.graphWidgetInput.setBackground((0, 0, 0))
        #self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,100], padding=None, update=True, disableAutoRange=True)
        #self.graphWidgetInput.setRange(rect=None, xRange=None, yRange=[-13,13], padding=None, update=True, disableAutoRange=True)
        self.legendOutput = self.ui.graphWidgetOutput.addLegend()
        self.legendInput = self.ui.graphWidgetInput.addLegend()
        
    def initialTimer(self,default=10):
        self.timer = QTimer()
        self.timer.setInterval(default) #Changes the plot speed. Defaulted to 50 ms. Can be placed in startbuttonPushed() method
        time.sleep(2)
        try: 
            self.timer.timeout.connect(self.updatePlot)
        except AttributeError:
            print("Something went wrong")
            
    def serialOpenPushed(self):
        #Try/except/else/finally statement is to check whether settings menu was opened/changed

        try:
            self.size = self.serial_values["Data Window"] #Value from settings. Windows data
            
            self.serialInstance = CoursesDataClass.SerialComm(self.serial_values["COM"],
                                                            self.serial_values["Baud Rate"],
                                                            self.serial_values["Timeout"])
            self.serialInstance.gcodeLetters = ["T","S","A"]
            self.serialInstance.flush()
            self.serialInstance.reset_input_buffer()
            self.serialInstance.reset_output_buffer()
            print("Opening DAQ...")

            if not self.serialInstance.is_open():
                self.serialInstance.open() # COME BACK TO THIS. I THINK IT'S WRONG 
                
            time.sleep(2)
            #print(colorama.Fore.RED + "Serial successfully open!")
            print("Serial successfully open!")

            if self.serialInstance.is_open():
                self._led.onColour = QLed.Green  
                self.ui.serialOpenButton.clicked.disconnect(self.serialOpenPushed)
                self.ui.serialCloseButton.clicked.connect(self.serialClosePushed)
                self.ui.startbutton.clicked.connect(self.startbuttonPushed)
            
            self.ui.menubar.setEnabled(False)
            #self.ui.serialOpenButton.clicked.disconnect(self.serialOpenPushed)
            #self.ui.serialCloseButton.clicked.connect(self.serialClosePushed)
        
        except AttributeError:
            print("Settings menu was never opened or Course was never selected in menubar")

        except TypeError:
            print("Settings menu was opened, however OK was not pressed to save values")
            
    def serialClosePushed(self):
        if self.serialInstance.is_open():
            self.serialInstance.close()
            print("Serial was open. Now closed")   

        try:
            self.ui.serialOpenButton.clicked.connect(self.serialOpenPushed)
        except:
            print("Serial Open button already connected")

        self._led.onColour = QLed.Red
        self.ui.menubar.setEnabled(True)
        
        '''
        try:
            self.ui.startbutton.clicked.disconnect(self.startbuttonPushed)
            self.ui.stopbutton.clicked.disconnect(self.stopbuttonPushed)
        except:
            pass #THIS TRY EXCEPT IS DIFFERENT
        '''
        self.ui.serialCloseButton.clicked.disconnect(self.serialClosePushed)
        
    def startbuttonPushed(self):
        print("Recording Data")
        # self.legendOutput.clear() #Clears Legend upon replotting without closing GUI
        # self.legendInput.clear() #Clears Legend upon replotting without closing GUI
        # self.timer.start()
        #self.serialInstance.sampleTimeSamplingRate(self.serial_values["Sampling Rate"],
                                                   #self.serial_values["Sample Time"])
        self.serialInstance.requestByte()