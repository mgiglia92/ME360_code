import sys
import os
import time
import serial
import binascii

class SerialComm:

    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout    
        self.thread = None
        self._gcodeLetters = None #Private
        self.time = []
        self.ser = serial.Serial(port = self.port,
                                 baudrate = self.baudrate,
                                 timeout = self.timeout)
    '''
    def open(self):
        """
        Opens serial communication
        """
        self.ser = serial.Serial(port = self.port,
                                 baudrate = self.baudrate,
                                 timeout = self.timeout)
        return(self.ser)
    '''

    def open(self):
        """
        Opens serial communication
        """
        self.ser.open()

    def close(self):
        """
        Closes serial communication
        """
        self.ser.close()

    def is_open(self):
        """
        Checks if serial communication is active. Returns boolean
        """
        return(self.ser.is_open)

    def flushInput(self):
        """
        Ensures all data in buffer is sent, then clears buffer
        """
        self.ser.flushInput()
    
    def flush(self):
        self.ser.flush()

    def reset_input_buffer(self):
        self.ser.reset_input_buffer()
    
    def reset_output_buffer(self):
        self.ser.reset_output_buffer()

    def set_buffer_size(self, rx_size = 12800, tx_size = 12800):
        self.ser.set_buffer_size(rx_size, tx_size)

    def readValues(self):
        """
        Current format of received data is b"T23533228,S0.00,A0.00,Q0.00,\0\r\n"
        Returns a list of datapoints ["T23533228","S0.00","A0.00","Q0.00"]
        Incorporates error handling into the read data such that the datastream 
        will not contain an empty string, will always starts with "T" in the 0th element,
        and isn't of NoneType. If the datastream does not pass these checks, this method
        will return None. This None will then be processed by methods in the GUI to just
        skip saving/plotting this point in time.
        """
        data = self.ser.readline().decode().replace('\r\n','').split(",")
        if any(ele == '' for ele in data) == False and data[0].startswith("T") == True: 
            if data is not None:
                arduinoData = data
        else: 
            arduinoData = None 

        return arduinoData

    def requestByte(self):
        """
        Sends R1 command to start serial communication with arduino. 
        """
        self.ser.write("R1%".encode())

    def stopRequestByte(self):
        """
        Sends R0 command to stop serial communication with arduino. 
        """
        self.ser.write("R0%".encode())

    def labSelection(self,course):
        '''
        Sends L# command
        1 Procon
        2 Statics
        3 Speed of Sound
        4 Beam
        5 General DAQ
        '''
        all_courses = { "Procon" : 1,
                        "Statics": 2,
                        "Sound"  : 3,
                        "Beam"   : 4,
                        "General": 5}
        #print(f"L{all_courses[course]}%")
        self.ser.write(f"L{all_courses[course]}%".encode())

    def sampleTimeSamplingRate(self,srate,stime):
        '''
        Sends S1,A{srate},B{stime} where
        srate is sampling time 
        stime is the sample time (total elapsed time for Arduino to run)
        '''
        self.ser.write(f"S1,A{srate},B{stime}%".encode())

    def gcodeParsing(self,datastream,hex=False):
        '''
        Returns full list of data from Arduino given the specified gcode letters
        '''
        #result = [_ for _ in input_list if _.startswith(letter)][0][1:]
        result = [_ for _ in datastream if _.startswith(tuple(self._gcodeLetters))]
        #result = [_ for _ in fake_stream if _.startswith(tuple(classType.gcodeLetters))] 
        #result = [_[1:] for _ in result]
        return(result)

    @property
    def gcodeLetters(self):
        """
        Getter
        """
        return self._gcodeLetters
    
    @gcodeLetters.setter
    def gcodeLetters(self, var):
        """
        Sets _gcodeLetters attribute as a list of characters to be parsed
        """
        if type(var) is list:
            self._gcodeLetters = var 

        else:
            raise TypeError("Should be set to a list")

    def initialLabSelectionSend(self):
        pass

    def initialLabSelectionReceive(self):
        pass

    '''
    def sendInitialRequest(self):
        """
        This should be the first thing sent to Arduino. It is to send a byte of what
        variables should only be sent back
        """
        if self._gcodeLetters is not None:
            a = ','.join(self._gcodeLetters)
            a = a + "\0" #adds null terminator to just the initial request, NOT the _gcodeLetters
            a = a.encode()
            #return binascii.hexlify(a)
            self.ser.write(a)
            return a

    def dataPlot(self):
        try:
            j = int(self.y2_zeros[self.buffersize])
            self.y2_zeros[j] = self.y2_zeros[j+self.size] = float(self.gcodeParsing("A",fulldata))
            self.y2_zeros[self.buffersize] = j = (j+1) % self.size
            self.y2.append(self.gcodeParsing("A",fulldata))
        except ValueError:
            print("Couldn't parse")
        except IndexError:
            print("Couldn't parse index. Skipping point")
    '''


class StaticsLab(SerialComm):
    def __init__(self, port, baudrate, timeout):
        super().__init__(port, baudrate, timeout)

class BeamLab(SerialComm):
    def __init__(self, port, baudrate, timeout):
        super().__init__(port, baudrate, timeout)

class SoundLab(SerialComm):
    def __init__(self, port, baudrate, timeout):
        super().__init__(port, baudrate, timeout)

class GeneralDAQ(SerialComm):
    def __init__(self, port, baudrate, timeout):
        super().__init__(port, baudrate, timeout)

#self.serialInstance.gcodeLetters = ["T","S","A"]

'''
classType = Thermo("COM5",500000,0.1)
classType.gcodeLetters = ("T","Q")#, "\0"]

fake_stream = ['T1', 'S12', 'A1.23', 'Q6.56', '\x00']
fake_stream1 = ['T2', 'S13', 'A3.23', 'Q3.56', '\x00']
fake_stream2 = ['T3', 'S14', 'A153', 'Q4.66', '\x00']

classType  = Thermo("COM5",500000,0.1)
classType.gcodeLetters = ["T","Q"]#, "\0"]
print(classType.sendInitialRequest().decode())
#startswith intakes a tuple
result = [_ for _ in fake_stream if _.startswith(tuple(classType.gcodeLetters))] 
result = [_[1:] for _ in result]
print(result)

classType  = Drones("COM5",500000,0.1)
classType.gcodeLetters = ["S","A"]#, "\0"]
print(classType.sendInitialRequest().decode())
result = [_ for _ in fake_stream1 if _.startswith(tuple(classType.gcodeLetters))] 
result = [_[1:] for _ in result]
print(result)
'''

'''
example  = Thermo("COM5",500000,0.1)
example.gcodeLetters = ["S","A"]
example.serialOpen()
print(example.sendInitialRequest())

def main():
    count = 0
    while count != 20:
        data = example.readValues() 
        print(example.gcodeParsing(data))
        #print(data)
        count = count + 1
    example.serialClose()

if __name__ == '__main__':
    print("Is serial open?", example.serialIsOpen())
    main()
    print("Is serial open?", example.serialIsOpen())
'''