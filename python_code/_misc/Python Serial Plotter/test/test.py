# arduino_LED_user.py

import serial
import time
import random
import pyqtgraph as pg
from collections import deque
from pyqtgraph.Qt import QtGui, QtCore

# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM5', 9600)
time.sleep(2)  # This line is critical for windows PC, waits for serial port to initialize
# Porblem is documented here: https://forum.arduino.cc/index.php?topic=85467.0
first_handshake = True

def read_value(first_handshake):
    if(first_handshake):
        ser.write(b'A')
        ser.reset_input_buffer()
        values = ser.readline().decode()
        print(values)
        ser.write(b'B')
        values = ser.readline().decode()
        first_handshake = False
        # readline().decode()
        # ser.reset_input_buffer()
    else:
        ser.write(b'B')
        values = ser.readline().decode()
        # readline().decode()
        # ser.reset_input_buffer()
    print(values)
    return first_handshake
    
    # time.sleep(0.05)
    # value = ser.read_until(terminator = "*", size = 50) # Read more then one line
    # value = value.decode()
    # pos = value.find('\r\n')  # # select the first full line, each full line contains all signals
    # value = value[pos+2:]
    # pos = value.find('\r\n')
    # value = value[0:pos]
    # print("Cropped Value is: ", value, "Type is: ", type(value))
    # try:
    #     value = float(value)
    #     # print("Value is: ", value, "Type is: ", type(value)) 
    #     return value
    # except:
    #     print("Fail")
    #     # print("Fail, value is ", value)
    #     return read_value()
    #     # print("FAIL, Value is: ", value, "Type is: ", type(value))
    #     # return -1
    
if __name__ == '__main__':
    # g = Graph()
    first_handshake = True
    while True:
        first_handshake = read_value(first_handshake)
        time.sleep(0.01)
