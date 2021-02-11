import serial
import time
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pandas as pd

ser = serial.Serial('COM7')
time.sleep(2)
t = []
motorspeed = []

# ser.write(b'P2,D2.5,\0')
# ser.write(b'\0')
# ser.write(b'P2,D0.5,H,\0')
# ser.write(b'D3.5,D08,\0')


ser.write(b'A')
print(ser.readline())

for i in range(0,500):
    ser.write(b'B')
    try:
        t_val,speed_val = ser.readline().decode().replace("\r\n","").split(',')
        t.append(t_val)
        motorspeed.append(speed_val)
    except:
        print("Error happened t: ",t,"spd: ",speed_val)

for i in range(0,100):
    ser.write(b'C')

# Plot PWM vs time / ms
df = pd.DataFrame(list(zip(t, motorspeed)), 
               columns =['time', 'rpm']) 
fig = px.line(df, x = 'time',y = "rpm")
fig.show()



