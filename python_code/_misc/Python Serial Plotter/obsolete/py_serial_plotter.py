import serial
import time
import pyqtgraph as pg
from collections import deque
from pyqtgraph.Qt import QtGui, QtCore

# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM5', 9600,timeout = 0.001)
time_record = []

class Graph:
    def __init__(self, ):
        # Set up empty deque object dat to store values to plot
        # Set up Qapplication and graph windows
        # Open plot and add curve
        self.dat = deque()
        self.maxLen = 50 #max number of data points to show on graph
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow()
       
        self.p1 = self.win.addPlot(colspan=2)
        self.win.nextRow()
        self.curve1 = self.p1.plot()
       
        # Set up plotting speed, start plot timer, and start plotting
        graphUpdateSpeedMs = 10
        timer = QtCore.QTimer() #to create a thread that calls a function at intervals
        timer.timeout.connect(self.update) #the update function keeps getting called at intervals
        self.update()
        timer.start(graphUpdateSpeedMs)
        QtGui.QApplication.instance().exec_()
       
    def update(self):
        if len(self.dat) > self.maxLen:
            self.dat.popleft() #remove oldest

        t1 = time.time()
        value = read_value()
        t2 = time.time()
        time_record.append(t2-t1)
        # print(max(time_record))
        # if value:
        self.dat.append(value)
        # elif value == -1:
        #     if len(self.dat)>0:
        #         self.dat.append(self.dat[-1])
        #     else:
        #         self.dat.append(0)
        self.curve1.setData(self.dat)
        self.app.processEvents()

def read_value():
    ser.reset_input_buffer()
    time.sleep(0.05)
    value = ser.read_until(terminator = "*", size = 15) # Read more then one line
    value = value.decode()
    pos = value.find('\r\n')  # select the first full number
    value = value[pos+2:]
    pos = value.find('\r\n')
    value = value[0:pos]
    print("Cropped Value is: ", value, "Type is: ", type(value))
    try:
        value = float(value)
        # print("Value is: ", value, "Type is: ", type(value)) 
        return value
    except:
        print("Fail")
        # print("Fail, value is ", value)
        return read_value()
        # print("FAIL, Value is: ", value, "Type is: ", type(value))
        # return -1
    
if __name__ == '__main__':
    g = Graph()
