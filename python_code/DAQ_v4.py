import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import argparse
import atexit
from time import sleep
import os
from openpyxl import Workbook
import datetime
# import soundfile as sf

#COMMENT

# Modules for GUI
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import qdarkstyle #has some issues on Apple devices and high dpi monitors
from main_ui import Ui_MainWindow, Ui_Dialog
from QLed import QLed
from PyQt5.QtGui import QDoubleValidator, QKeySequence, QPixmap, QRegExpValidator, QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QComboBox, 
QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QGridLayout, QDialog, 
QLabel, QLineEdit, QDialogButtonBox, QFileDialog, QSizePolicy, QLayout,
QSpacerItem, QGroupBox, QShortcut, QMainWindow, QSlider)
from PyQt5.QtCore import QDir, Qt, QTimer, QRegExp, QCoreApplication, QSize, QRunnable, QThread, QThreadPool

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
directory = os.getcwd()
# plt.ion()
    
class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.currentItemsSB = [] # Used to store variables to be displayed in status bar at the bottom right
        self.verbose = True # Initialization. Used in the thread generated in application

        self.fs = 1000;
        self.N = 5000;
        self.dt = 1.0/self.fs
        self.sample_time = self.N*self.dt
        self.data = []
        
        self.delay = 2
        
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.getLogo()
        self.getFonts()
        self.initalConnections()
        # self.initialGraphSettings()
        self.arduinoStatusLed()
        # self.initialTimer()
        # self.initialState()
        
        # self.ui.graphWidgetOutput.setLabel('left',"<span style=\"color:white;font-size:16px\">Speed (m/s)</span>")
        # self.ui.graphWidgetOutput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        # self.ui.graphWidgetOutput.setTitle("Speed", color="w", size="12pt")

        # self.ui.graphWidgetInput.setLabel('left',"<span style=\"color:white;font-size:16px\">°C</span>")
        # self.ui.graphWidgetInput.setLabel('bottom',"<span style=\"color:white;font-size:16px\">Time (s)</span>")
        # self.ui.graphWidgetInput.setTitle("Temperature", color="w", size="12pt")
        # # self.currentValueSB(self.course)
        
        # self.course = "Sound"
        self.list_ports()
        self.COM = str(self.com_ports[0])
        self.ui.com_port.addItems(self.com_ports)
        self.ui.com_port.setCurrentIndex(self.com_ports.index(self.COM))
        
        atexit.register(self.closeSerial)
        
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
        self.statusLabel = QLabel("Teensy Status:")
        self.statusLabel.setFont(QFont("Roboto", 12)) 

        self.statusBar().addWidget(self.statusLabel)
        #self.statusBar().reformat()
        self.statusBar().addWidget(self._led)
        
    def initalConnections(self):
        """
        6 Main Buttons (for now)
        """
        self.ui.serialOpenButton.clicked.connect(self.serialOpenPushed)  
        self.ui.settingsButton.clicked.connect(self.settingsPushed)
        self.ui.recordbutton.clicked.connect(self.recordbuttonPushed)        
        self.ui.sendbutton.clicked.connect(self.sendbuttonPushed)
        self.ui.plotbutton.clicked.connect(self.plotbuttonPushed)
        self.ui.savebutton.clicked.connect(self.savebuttonPushed)
        # self.ui.clearbutton.clicked.connect(self.clearbuttonPushed)
        # self.ui.settings.clicked.connect(self.settingsMenu)
        
    def serialOpenPushed(self):
        self.COM = str(self.ui.com_port.currentText())
        self.ser = serial.Serial(port=self.COM)
        sleep(2)
        self.ser.flush()
        print("Serial opened successfully!")
        
        if self.ser.is_open:
            self._led.onColour = QLed.Green  
            self.ui.serialOpenButton.clicked.disconnect(self.serialOpenPushed)
            # self.ui.serialCloseButton.clicked.connect(self.serialClosePushed)
            # self.ui.startbutton.clicked.connect(self.recordbuttonPushed)
            
            # Set N and fs on Teensy
            write_string = f"S0,N{self.N},%".encode('utf-8')
            self.ser.write(write_string)
            
            write_string = f"S1,T{self.fs},%".encode('utf-8')
            self.ser.write(write_string)
            
            write_string = f"S2,T{self.delay},%".encode('utf-8')
            self.ser.write(write_string)
            
    def closeSerial(self):
        if self.ser.is_open:
            self.ser.close()
            print("Serial closed.")
            
    def recordbuttonPushed(self):
        print('Recording...',end='',flush=True)
        self.ser.write(b'R1,%')
        sleep(self.sample_time+self.delay)
        print('Done.')
        
    def sendbuttonPushed(self):
        print('Sending Data...',end='',flush=True)
        # Initialize data list
        self.raw_data=[]
        # Continue reading the data until '#' is found
        while(1):
            self.ser.write(b'R0%') # Request a data point from arduino
            line = [] # initialize as empty array, line buffer 
            string_buff='' # intiailze as empty string
            while(1): # Read char by char until '\0' found
                if(self.ser.in_waiting > 0): # if data in buffer read
                    line.append(self.ser.read(1).decode()) # Read 1 character and decode from bytes to characters
                if '\0' in line: break # if '\0' found break out of line loop
            # print(''.join(line)) # See line received
            self.raw_data.append(''.join(line)) # Append line read (joined as one single string)  to data block
            if '#' in line: # if '#' found break out of reading loop
                break
        print('Done.')
        self.decipher_raw_data()
        
    def decipher_raw_data(self):
        # Get first letter of each segment separated by commas
        # Give the pandas dataframe column names
        col_name = [i[0] for i in self.raw_data[0].split(',')[:-1]]

        # Initialize data buffers
        buff=[]
        for row in self.raw_data:
            # Get all but first character in each segment separated by commas
            # Get all the numbers in the data into a 2d list
            new_data = row.split(',')[:-1]
            # print(new_data)
            buff.append([float(j[1:]) for j in new_data])
        # print(col_name)
        self.data = pd.DataFrame(buff, columns=col_name)
        self.data = self.data.drop(columns=['C'])
        self.data['B'] = self.data['B']/10000
        
        # # Conversion to temperature: R_therm = 10k*exp(K*(1/T-1/T0)
        # # and ADC = R/(R+10k)*(2^12-1)
        # T0 = 25+273.15 # K
        # K = 3950 # K
        # self.data['Temp'] = 1.0/(1.0/T0+np.log(self.data['C']/((2**12-1)-self.data['C']))/K)-273.15 # oC
        
    # def initialGraphSettings(self):
        # self.ui.graphWidgetOutput.showGrid(x=True, y=True, alpha=None)
        # self.ui.graphWidgetInput.showGrid(x=True, y=True, alpha=None)
        # self.ui.graphWidgetOutput.setBackground((0, 0, 0))
        # self.ui.graphWidgetInput.setBackground((0, 0, 0))
    
    def plotbuttonPushed(self):
        # self.ui.graphWidgetOutput.clear()
        # self.ui.graphWidgetInput.clear()
        # self.legendOutput.clear()
        # self.legendInput.clear()
        
        self.time = self.data['T'].to_numpy()
        self.A = self.data['A'].to_numpy()/(2^12-1)
        self.B = self.data['B'].to_numpy()
        
        self.A = self.A-self.A.mean()
        # self.B = self.B-self.B.mean()
        
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        ax.plot(self.time, self.A)
        self.update_line, = ax.plot(self.time,self.B)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.show()
    
    def savebuttonPushed(self):
        print('Saving...',end='',flush=True)
        self.now = datetime.datetime.now()
        self.nrow = 1
        self.result_file = Workbook()
        self.dl = self.result_file.worksheets[0]
        self.writerow(self.dl,['Data Logged From Teensy '+ self.now.strftime("%Y-%m-%d %H-%M")])
        self.writerow(self.dl,['Time (s)','Strain Gage', 'Accelerometer'])
        
        for row in self.data.to_numpy():
            self.writerow(self.dl,row)
        self.result_file.save(directory+'\\data\\Experiment Data '+ self.now.strftime("%Y-%m-%d %H-%M") +'.xlsx') 
        print('Done.')
        
    def writerow(self,ws,output=[]):
          for dd, data in enumerate(output):
              ws.cell(row = self.nrow,column = dd+1).value = data
          self.nrow = self.nrow+1
          
    def settingsPushed(self):
        self.settingsDialog = QDialog()
        self.settingsDialog.setStyleSheet(qdarkstyle.load_stylesheet())
        self.settingsDialog.setWindowTitle("Settings")
        
        layout = QVBoxLayout(self.settingsDialog)
        
        # com_widget = QComboBox(self.settingsDialog)
        # self.list_ports()
        # com_widget.addItems(self.com_ports)
        # com_widget.setCurrentIndex(self.com_ports.index(self.COM))
        # layout.addWidget(com_widget)
        
        fs_layout = QHBoxLayout()
        fs_label = QLabel()
        fs_label.setText("Sampling Rate (fs)")
        fs_widget = QLineEdit(self.settingsDialog)
        fs_widget.setText(str(self.fs))
        fs_layout.addWidget(fs_label)
        fs_layout.addWidget(fs_widget)
        layout.addLayout(fs_layout)
        
        N_layout = QHBoxLayout()
        N_label = QLabel()
        N_label.setText("Number of Samples (N)")
        N_widget = QLineEdit(self.settingsDialog)
        N_widget.setText(str(self.N))
        N_layout.addWidget(N_label)
        N_layout.addWidget(N_widget)
        layout.addLayout(N_layout)
        
        delay_layout = QHBoxLayout()
        delay_label = QLabel()
        delay_label.setText("Record Delay (s)")
        delay_widget = QLineEdit(self.settingsDialog)
        delay_widget.setText(str(self.delay))
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(delay_widget)
        layout.addLayout(delay_layout)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save
                             | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.settingsDialog.accept)
        buttonBox.rejected.connect(self.settingsDialog.reject)
        layout.addWidget(buttonBox)
        
        self.settingsDialog.setLayout(layout)
        
        if self.settingsDialog.exec_() == QDialog.Accepted:
            self.fs = int(fs_widget.text())
            self.N = int(N_widget.text())
            self.dt = 1.0/self.fs
            self.sample_time = self.N*self.dt

            self.delay = int(delay_widget.text())
            
            write_string = f"S0,N{self.N},%".encode('utf-8')
            self.ser.write(write_string)
        
            write_string = f"S1,T{self.fs},%".encode('utf-8')
            self.ser.write(write_string)
            
            write_string = f"S2,T{self.delay},%".encode('utf-8')
            self.ser.write(write_string)
            print('Settings saved.')
        else:
            print('Settings NOT saved.')
        # print(f"Current fs is {self.fs}.")
        # self.fs = int(input('Specify Sampling Rate (fs): '));
        # print(f"Current N is {self.N}.")
        # self.N = int(input('Specify Number of Samples (N): '));
        
        # self.dt = 1.0/self.fs;
        # self.sample_time = self.N*self.dt

        # write_string = f"S0,N{self.N},%".encode('utf-8')
        # self.ser.write(write_string)
    
        # write_string = f"S1,T{self.fs},%".encode('utf-8')
        # self.ser.write(write_string)
        
        # print ('Settings saved.')
        
    def list_ports(self):
        self.com_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' or 'tty' in p.description  
        ]
        if not self.com_ports:
            raise IOError("No COM ports found. Replug in USB cable and try again.")
        self.com_ports.sort(key=lambda s: (s[:-2], int(s[-2:])) if s[-2] in '0123456789' else (s[:-1], int(s[-1:])))

def main():
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    #app.aboutToQuit.connect(main.cleanUp) #See Window.cleanUp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()        
        
# def main(c):
    # global raw_data
    # global sample_time
    # global N
    # global fs
    # # Start recording of data on arduino
    # if c == 'r':
        # print('Recording...',end='',flush=True)
        # ser.write(b'R1,%')
        # sleep(sample_time)
        # print('Done.')

    # # Loop through saved data on arduino
    # # Each data point line ends with \0
    # # End of data ends with '#'
    # if c == 's':
        # print('Sending Data...',end='',flush=True)
        # # Initialize data list
        # raw_data=[]
        # # Continue reading the data until '#' is found
        # while(1):

            # ser.write(b'R0%') # Request a data point from arduino
            # line = [] # initialize as empty array, line buffer 
            # string_buff='' # intiailze as empty string
            # while(1): # Read char by char until '\0' found
                # if(ser.in_waiting > 0): # if data in buffer read
                    # line.append(ser.read(1).decode()) # Read 1 character and decode from bytes to characters
                # if '\0' in line: break # if '\0' found break out of line loop
            # # print(''.join(line)) # See line received
            # raw_data.append(''.join(line)) # Append line read (joined as one single string)  to data block
            # if '#' in line: # if '#' found break out of reading loop
                # break
        # print('Done.')
    # if c =='p':
        # #TODO: Fix plotting, y-axis is upside down
        # plot_data = decipher_raw_data(raw_data)
        # # fig = plt.figure(1)
        # # plt.clf()
        # # dnp = plot_data.to_numpy()
        # time = plot_data['T']
        # A = plot_data['A']
        # B = plot_data['B']
        # # print(time)
        # # print(A)

        # #setup plotting
        # #TODO: clean up figure and plotting
        # # plt.xticks([])
        
        # plt.plot(time, A)
        # plt.plot(time,B)
        # plt.ylim((0,2**12-1))
        # plt.show()     

    # if c == 't':
        # fs = int(input('Specify Sampling Rate (fs): '));
        # N = int(input('Specify Number of Samples (N): '));
        
        # dt = 1/fs;
        # sample_time = N*dt;
        # write_string = f"S0,N{N},%".encode('utf-8')
        # ser.write(write_string)
    
        # write_string = f"S1,T{fs},%".encode('utf-8')
        # ser.write(write_string)

# # Convert each line of data into pandas array
# def decipher_raw_data(d:list):
    # # Get first letter of each segment separated by commas
    # # Give the pandas dataframe column names
    # col_name = [i[0] for i in d[0].split(',')[:-1]]

    # # Initialize data buffers
    # buff=[]
    # for row in d:
        # # Get all but first character in each segment separated by commas
        # # Get all the numbers in the data into a 2d list
        # new_data = row.split(',')[:-1]
        # # print(new_data)
        # buff.append([float(j[1:]) for j in new_data])
    # # print(col_name)
    # df = pd.DataFrame(buff, columns=col_name)
    # # print(df)
    # return df
    
# def on_quit():
    # if ser.is_open:
        # ser.close()
        # print("Serial closed.")

# atexit.register(on_quit)
        
# if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="COM PORT")
    # parser.add_argument('--port', dest='port', required=True)
    # args = parser.parse_args()
    # port = args.port
        
    # # port = "COM3"
    # ser = serial.Serial(port=port)
    # ser.flush()
    
    # fs = 1000;
    # N = 1000;
    # dt = 1/fs;
    # sample_time = N*dt;
    
    # write_string = f"S0,N{N},%".encode('utf-8')
    # ser.write(write_string)
    
    # write_string = f"S1,T{fs},%".encode('utf-8')
    # ser.write(write_string)
    
    # # write_string = f"S0,T{dt},%".encode()
    # # ser.write(write_string)
    
    # global raw_data
    # raw_data=[]
    # line=[]
    # buff = []
    # d = ''
    # # df: pd.DataFrame
    # while(1):
        # try:
            # uin = input('r: record, s: send, p: plot, t: change settings, q: quit\n')
            # if(uin=='q'):break
            # main(uin)
        # except Exception as e:
            # print(e)