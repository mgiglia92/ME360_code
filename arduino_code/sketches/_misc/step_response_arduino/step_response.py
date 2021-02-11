import sys 
import os
import time
import serial
import numpy as np
import codecs

class serial_comm:
    def __init__(self, port, rate, timeout):
        self.port = port
        self.rate = rate
        self.timeout = timeout
    
    def open_serialport(self):
        self.ser = serial.Serial(port=self.port,baudrate=self.rate,timeout = self.timeout)
        time.sleep(2)
        return self.ser
    
    def hand_shake(self):
        # establish handshake
        self.ser.flushInput()
        self.ser.write(b'A')
        print("Handshake request sent")
        value = self.ser.readline().decode().replace('\r\n','')
        print(value)
        if(value == "Contact established"):
            print("Handshake success")
        else:
            print("Handshake failed, trying again")
            self.hand_shake()

    def read_serial_value(self):
        self.ser.write(b'B')
        values = self.ser.readline()
        try:
            values = long(values,16)
        except:
            try:
                values = values.decode('utf-8').strip('\r\n')
            except:
                print("Tried everything, cannot decode")
        #         values = 0
        # if(type(values)!=int and type(values)!= float):
        #     print(values,type(values))
        # # print(values)
        # # values = values.split(",")
        return values

if __name__ == '__main__':
    serial_port = 'COM6'
    baud_rate = 19200
    timeout = 0.5
    amplitude = []

    Arduino = serial_comm(serial_port,baud_rate,timeout)
    Arduino.open_serialport()
    Arduino.hand_shake()
    time.sleep(0.01)

    while(1):
        val = Arduino.read_serial_value()
        if(val != "End"):
            amplitude.append(val)
        else:
            print("Data aqcuisition terminate")
            break
        
with open('angle_PID.txt', 'w') as f:
    for item in amplitude:
        f.write("%s\n" % item)
    print("Data saved to", "\"",f.name,"\"")

