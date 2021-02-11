import serial
import time

ser = serial.Serial('COM3', baudrate=500000, timeout=0.1)

def lab(lab_num):
    ser.flush()
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write('L{}%'.format(lab_num).encode())
    ser.write(b'R1%')

temp = True

while(1):
    if temp:
        time.sleep(2)
        lab(3)
        temp = False
    print(ser.readline())