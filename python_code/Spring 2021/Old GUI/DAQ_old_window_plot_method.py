import sys
import os
import time
from pyqtgraph import PlotWidget
import qdarkstyle #has some issues on Apple devices and high dpi monitors
import CoursesDataClass
from SettingsClass import *
from ui_file import Ui_MainWindow
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

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.currentItemsSB = [] # Used to store variables to be displayed in status bar at the bottom right
        self.verbose = True # Initialization. Used in the thread generated in application

        script_dir = os.path.dirname(__file__)
        logo_rel_path = r"logo\CUAtHomeLogo-Horz.png"
        logo_abs_file_path = os.path.join(script_dir, logo_rel_path)
        self.ui.imageLabel.setPixmap(QPixmap(logo_abs_file_path).scaled(200, 130, 
                                                                   Qt.KeepAspectRatio, 
                                                                   Qt.FastTransformation))
        
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.getFonts()
        self.initalConnections()
        self.initialGraphSettings()
        self.arduinoStatusLed()
        self.initialTimer()
        self.initialState()

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

    def currentValueSB(self,labtype):
        '''
        Used to add/remove values in the status bar in 
        the bottom of the application
        '''
        try:
            for item in self.currentItemsSB:
                self.statusBar().removeWidget(item)
        except:
            pass

        if labtype == "Statics":
            self.voltage_label = QLabel("Voltage")
            self.voltage_value = QLabel("")
            self.currentItemsSB = [self.voltage_label, self.voltage_value]
            for item in self.currentItemsSB:
                self.statusBar().addPermanentWidget(item)
                item.setFont(QFont("Roboto", 12)) 

        elif labtype == "Beam":
            self.accel_label = QLabel("Acceleration")
            self.accel_value = QLabel("")
            self.currentItemsSB = [self.accel_label, self.accel_value]
            for item in self.currentItemsSB:
                self.statusBar().addPermanentWidget(item)
                item.setFont(QFont("Roboto", 12)) 

        elif labtype == "Sound":
            self.mic1_label = QLabel("Mic 1:")
            self.mic1_value = QLabel("")
            self.mic2_label = QLabel("Mic 2:")
            self.mic2_value = QLabel("")
            self.temperature_label = QLabel("Temp:")
            self.temperature_value = QLabel("")
            self.currentItemsSB = [self.mic1_label, self.mic1_value,
                                   self.mic2_label, self.mic2_value,
                                   self.temperature_label, self.temperature_value]
            for item in self.currentItemsSB:
                self.statusBar().addPermanentWidget(item)
                item.setFont(QFont("Roboto", 12)) 

    def initalConnections(self):
        """
        Menubar
        """
        self.ui.actionStatics.triggered.connect(self.staticsPushed)
        self.ui.actionBeam.triggered.connect(self.beamPushed)
        self.ui.actionSound.triggered.connect(self.soundPushed)
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

    def staticsPushed(self):
        self.course = "Statics"    
        self.setWindowTitle(self.course)

        # Graph settings for specific lab
        self.ui.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">Voltage (V)</span>")
        self.ui.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetOutput.setTitle("Voltage????? Might be resistance IDK", 
                                           color="w", size="12pt")

        self.ui.graphWidgetInput.setLabel('left',"")
        self.ui.graphWidgetInput.setLabel('bottom',"")
        self.ui.graphWidgetInput.setTitle("")
        self.currentValueSB(self.course)

    def beamPushed(self):
        self.course = "Beam"    
        self.setWindowTitle(self.course)

        # Graph settings for specific lab
        self.ui.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">Acceleration (m/s^2)</span>")
        self.ui.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetOutput.setTitle("Acceleration", color="w", size="12pt")

        self.ui.graphWidgetInput.setLabel('left',"")
        self.ui.graphWidgetInput.setLabel('bottom',"")
        self.ui.graphWidgetInput.setTitle("")
        self.currentValueSB(self.course)

    def soundPushed(self):
        self.course = "Sound"    
        self.setWindowTitle(self.course)

        # Graph settings for specific lab
        self.ui.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">Speed (m/s)</span>")
        self.ui.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetOutput.setTitle("Speed", color="w", size="12pt")

        self.ui.graphWidgetInput.setLabel('left',"<span style=\"color:white;font-size:16px\">°C</span>")
        self.ui.graphWidgetInput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        self.ui.graphWidgetInput.setTitle("Temperature", color="w", size="12pt")
        self.currentValueSB(self.course)

    def serialOpenPushed(self):
        #Try/except/else/finally statement is to check whether settings menu was opened/changed

        try:
            self.size = self.serial_values[3] #Value from settings. Windows data
            
            if self.course == "Statics":
                self.serialInstance = CoursesDataClass.StaticsLab(self.serial_values[0],
                                                                  self.serial_values[1],
                                                                  self.serial_values[2])
                self.serialInstance.flush()
                self.serialInstance.reset_input_buffer()
                self.serialInstance.reset_output_buffer()

            if self.course == "Sound":
                self.serialInstance = CoursesDataClass.SoundLab(self.serial_values[0],
                                                                self.serial_values[1],
                                                                self.serial_values[2])
                self.serialInstance.gcodeLetters = ["T","S","A"]
                self.serialInstance.flush()
                self.serialInstance.reset_input_buffer()
                self.serialInstance.reset_output_buffer()

            elif self.course == "Beam":
                self.serialInstance = CoursesDataClass.BeamLab(self.serial_values[0],
                                                               self.serial_values[1],
                                                               self.serial_values[2])
                self.serialInstance.flush()
                self.serialInstance.reset_input_buffer()
                self.serialInstance.reset_output_buffer()
            print(f"Now in {self.course} Lab")

            if not self.serialInstance.is_open():
                self.serialInstance.open() # COME BACK TO THIS. I THINK IT'S WRONG 
                
            time.sleep(2)
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
        self.legendOutput.clear() #Clears Legend upon replotting without closing GUI
        self.legendInput.clear() #Clears Legend upon replotting without closing GUI
        self.timer.start()
        self.curve()
        self.serialInstance.labSelection(self.course)


        self.serialInstance.requestByte()
        self.ui.startbutton.clicked.disconnect(self.startbuttonPushed)
        #self.ui.stopbutton.clicked.connect(self.stopbuttonPushed)
        
        self.verbose = True
        self.threadRecordSave = threading.Thread(target=self.readStoreValues)
        self.threadRecordSave.daemon = True #exits program when non-daemon (main) thread exits. Required if serial is open and application is suddenly closed
        self.threadRecordSave.start()

    def readStoreValues(self):
        '''
        Function that is run by a separate thread. 
        Will continuously read in serial data and append to various lists.
        Those lists will be used to save in the CSV file.
        Reason for doing this is that originally the GUI refreshes every X ms,
        requesting that datapoint every X ms. Using this, there should be a smaller
        amount of datapoints that are missed.
        '''
        while self.verbose:
            data = self.serialInstance.readValues()
            print(data)
            
            if data != None:
                self.fulldata = data
                if self.course == "Statics":
                    self.time.append(self.gcodeParsing("T", self.fulldata))
                    self.y1.append(self.gcodeParsing("S", self.fulldata))

                elif self.course == "Beam":
                    self.time.append(self.gcodeParsing("T", self.fulldata))
                    self.y1.append(self.gcodeParsing("S", self.fulldata))

                elif self.course == "Sound":
                    self.time.append(self.gcodeParsing("T", self.fulldata))
                    self.y1.append(self.gcodeParsing("S", self.fulldata))
                    self.y2.append(self.gcodeParsing("A", self.fulldata))
                    self.y3.append(self.gcodeParsing("Q", self.fulldata))
            else: 
                pass

    def stopbuttonPushed(self):
        self.verbose = False
        self.threadRecordSave.join()
        try:
            self.timer.stop()
            self.serialInstance.stopRequestByte() #
            #self.ui.startbutton.clicked.connect(self.startbuttonPushed)
            #self.ui.stopbutton.clicked.disconnect(self.stopbuttonPushed)
        except:
            pass

        print("Stopping Data Recording")

    def clearbuttonPushed(self):
        self.ui.graphWidgetOutput.clear()
        self.ui.graphWidgetInput.clear()
        self.legendOutput.clear()
        self.legendInput.clear()
        self.ui.graphWidgetOutput.addLegend()# Come back to this
        self.ui.graphWidgetInput.addLegend()# Come back to this
        #self.graphWidgetOutput.setRange(rect=None, xRange=None, yRange=[-1,100], padding=None, update=True, disableAutoRange=True)
        #self.graphWidgetInput.setRange(rect=None, xRange=None, yRange=[-13,13], padding=None, update=True, disableAutoRange=True)
        self.ui.startbutton.clicked.connect(self.startbuttonPushed)
        self.initialState() #Reinitializes arrays in case you have to retake data
        print("Cleared All Graphs")

    def savebuttonPushed(self):
        self.createCSV(self.course)
        path = QFileDialog.getSaveFileName(self, 'Save CSV', 
                                           os.getenv('HOME'), 'CSV(*.csv)')
        if path[0] != '':
            with open(path[0], 'w', newline = '') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.header)
                csvwriter.writerows(self.data_set)        
        print("Saved All Data")

    def settingsMenu(self):
        self.settingsPopUp = SettingsClass()
        self.settingsPopUp.show()
        #self.settingsPopUp.exec()
        self.serial_values = self.settingsPopUp.getDialogValues()

    def initialState(self):
        ''' 
        Initializes various arrays
        '''
        self.buffersize = 500 #np array size that is used to plot data
        self.step = 0 #Used for repositioning data in plot window to the leftz
        '''
        All of these X_zeros arrays are for the plotting in the pyqtgraphs
        '''
        self.time_zeros = np.zeros(self.buffersize+1, float)
        self.y1_zeros = np.zeros(self.buffersize+1, float)
        self.y2_zeros = np.zeros(self.buffersize+1, float)
        self.y3_zeros = np.zeros(self.buffersize+1, float)        

        ''' 
        These other arrays are the raw data that are saved to the CSV
        '''
        self.time = []
        self.y1 = []
        self.y2 = []
        self.y3 = []

    def curve(self):
        '''
        Initializes drawing tool for graphs, and creates objects that
        are used to be plotted on graphs
        '''
        pen1 = pg.mkPen(color = (255, 0, 0), width=1)
        pen2 = pg.mkPen(color = (0, 255, 0), width=1)
        pen3 = pg.mkPen(color = (0, 255, 255), width=1)

        if self.course == "Statics":
            self.data = self.ui.graphWidgetOutput.plot(pen = pen1, name="Voltage???") 

        elif self.course == "Beam":
            self.data = self.ui.graphWidgetOutput.plot(pen = pen1, name="Acceleration") 

        elif self.course == "Sound":
            self.data1 = self.ui.graphWidgetOutput.plot(pen=pen1, name="Mic 1") 
            self.data2 = self.ui.graphWidgetOutput.plot(pen=pen2, name="Mic 2") 
            self.data3 = self.ui.graphWidgetInput.plot(pen=pen3, name="Temperature")

    def createCSV(self,labtype):
        '''
        Creates headers and zipped object to be used in CSV file
        '''
        if labtype == "Statics":
            self.header = ["Time (ms???)", "Voltage???"]
            self.data_set = zip_longest(*[self.time,self.y1], fillvalue="")

        elif labtype == "Beam":
            self.header = ["Time (ms???)", "Acceleration???"]
            self.data_set = zip_longest(*[self.time,self.y1], fillvalue="")

        elif labtype == "Sound":
            self.header = ["Time (ms???)", "Mic 1", "Mic 2", "Temperature (°C)"]
            self.data_set = zip_longest(*[self.time, self.y1, self.y2, self.y3], 
                                        fillvalue="")

    def updatePlot(self):
        self.step = self.step + 1

        if self.course == "Statics":
            time_index, _ = self.dataWindow(self.fulldata, 
                                              self.time_zeros, "T")
            i, voltage = self.dataWindow(self.fulldata, self.y1_zeros, "S")

            self.data.setData(self.time_zeros[time_index:time_index+self.size],
                              self.y1_zeros[i:i+self.size])
            self.data.setPos(self.step,0)
            self.voltage_value.setText(str(voltage))

        elif self.course == "Beam":
            time_index, _ = self.dataWindow(self.fulldata, 
                                              self.time_zeros, "T")
            i, voltage = self.dataWindow(self.fulldata, self.y1_zeros, "S")

            self.data.setData(self.time_zeros[time_index:time_index+self.size],
                              self.y1_zeros[i:i+self.size])
            self.data.setPos(self.step, 0)
            self.accel_value.setText(str(voltage))

        elif self.course == "Sound":
            time_index, _ = self.dataWindow(self.fulldata, self.time_zeros, "T")
            i, mic1 = self.dataWindow(self.fulldata, self.y1_zeros, "S")
            j, mic2 = self.dataWindow(self.fulldata, self.y2_zeros, "A")
            k, temp = self.dataWindow(self.fulldata, self.y3_zeros, "Q")

            self.data1.setData(self.time_zeros[time_index:time_index+self.size],
                               self.y1_zeros[i:i+self.size])
            self.data1.setPos(self.step, 0)
            self.mic1_value.setText(str(mic1))

            self.data2.setData(self.time_zeros[time_index:time_index+self.size],
                               self.y2_zeros[j:j+self.size])
            self.data2.setPos(self.step, 0)
            self.mic2_value.setText(str(mic2))

            self.data3.setData(self.time_zeros[time_index:time_index+self.size],
                               self.y3_zeros[k:k+self.size])
            self.data3.setPos(self.step, 0)
            self.temperature_value.setText(str(temp))
        

    def dataWindow(self, datastream, data_zeros, char):
        '''
        datastream is the live stream of values from Arduino
        data_zeros is the list where the data is windowed in the live graphs
        char is the character where it parses for the starting letter using Gcode
        '''
        buffersize = self.buffersize
        size = self.size
        try:
            temp = self.gcodeParsing(char, datastream)
            i = int(data_zeros[buffersize])
            data_zeros[i] = data_zeros[i+size] = float(temp)
            data_zeros[buffersize] = i = (i+1)%size 
            return i, temp
        except ValueError:
            print("Couldn't parse value. Skipping point")
        except IndexError:
            print("Couldn't parse index. Skipping point")
        except TypeError:
            print("Couldn't unpack due to a None Object. Skipping point")
    '''
    def dataWindow(self, datastream, data_zeros, char):
        datastream is the live stream of values from Arduino
        data_zeros is the list where the data is windowed in the live graphs
        char is the character where it parses for the starting letter using Gcode
        buffersize = self.buffersize
        size = self.size
        try:
            temp = self.gcodeParsing(char, datastream)
            i = int(data_zeros[buffersize])
            data_zeros[i] = data_zeros[i+size] = float(temp)
            data_zeros[buffersize] = i = (i+1)%size 
            return i, temp
        except ValueError:
            print("Couldn't parse value. Skipping point")
        except IndexError:
            print("Couldn't parse index. Skipping point")
        except TypeError:
            print("Couldn't unpack due to a None Object. Skipping point")
    '''
    def gcodeParsing(self, letter, input_list):
        """
        Unpacks data by using list comprehension. For example, if 
        input_list is ["A1","B2","C3"] and letter is "A", this method returns 1. 
        """
        result = [_ for _ in input_list if _.startswith(letter)][0][1:]
        return result

    def cleanUp(self):
        '''
        Method that should only be called in the application instance.
        Used to close all running threads besides MainThread.
        Main instance where this occurs is when serial is open and is
        returning values, but application is suddenly closed. Not needed
        right now as self.threadRecordSave is a daemon thread. 
        In main(), app.aboutToQuit.connect(main.cleanUp) should be called after
        main.show() 
        '''
        for thread in threading.enumerate(): 
            thread.join()

def main():
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    #app.aboutToQuit.connect(main.cleanUp) #See Window.cleanUp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()