import serial
import serial.tools.list_ports
import sys 
import os
import time
from threading import Thread, Event
from queue import Queue


class SerialComm:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout 
        self.dataList = []   
        self.queue = Queue()
        self.runThread = Event()
        self.runThread.set()

    def serialOpen(self):
        self.ser = serial.Serial(port = self.port,
                                 baudrate = self.baudrate,
                                 timeout = self.timeout)
        return(self.ser)
    
    def serialClose(self):
        self.ser.close()

    def serialIsOpen(self):
        return(self.ser.is_open)

    def handshake(self):
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
        self.ser.flushInput()

    def readValues(self):
        while(1):
            self.runThread.wait()
            self.ser.write(b"R0,\0") #used to call for the next line (Request)
            #current format of received data is b"T23533228,S0.00,A0.00,Q0.00,\0\r\n"
            arduinoData = self.ser.readline().decode().replace('\r\n','').split(",")
            self.queue.put_nowait(arduinoData)        


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
        print('here')
        arduinoData = self.ser.readline().decode().split("$")#.replace('\r\n','')
        print(len(arduinoData))
        return arduinoData

    #S0 
    def writePID(self,P,I,D):
        self.runThread.clear()
        time.sleep(0.05)
        values = f"S0,P{P},I{I},D{D},\0"
        self.ser.write(str.encode(values))
        print("S0:", values)
        self.runThread.set()
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
    


if __name__ == "__main__":
    s = SerialComm('COM4', 2000000, 1)
    s.serialOpen()
    thread = Thread(target = s.readValues, daemon=True)
    thread.start()
    while(1):
        try:
            print(type(s.queue.get_nowait()))
            s.writePID(0,0,0)
            time.sleep(0.2)
        except:
            print('empty')