import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
"""
Columns of  CSV are as follows
Col 1: Index
Col 2: Time
Col 3: ? (should be velocity, though not right now)
Col 4: Position
Col 5: Voltage
"""
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'voltage5.csv') #ONLY THIS LINE SHOULD BE CHANGED! THIS IS DEPENDENT ON WHAT YOU EXPORT DATA AS!!!!!!


if __name__ == "__main__":
    time= []
    pos = []
    voltage = []
    with open(filename) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            time.append(row[1]) 
            pos.append(row[3])
            voltage.append(row[4]) #will be an array of the same value, as voltage does not change for OL 

# Determines the index of the closest value in an existing array to a search value
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    #return array[idx]
    return(idx)

timepos = np.column_stack((time[1:],pos[1:])).astype(np.float)
#print(timepos[:,0])
vel = np.gradient(timepos[:,1], 0.003, axis=0)
# plt.plot(timepos[:,0], timepos[:,1])

# Signal Conditioning
lpf = signal.butter(1, 0.1, btype='lowpass', analog=False, output='sos', fs=1)
filtered = signal.sosfilt(lpf, vel)
vel_pre_filtered = np.gradient(filtered, timepos[:,0], axis=0)

# To find tau using (1-1/e)*SS
steady_state = np.mean(vel[-50:]) #steady state value taken as average of last 50 points
v_tau = 0.632*steady_state #velocity at time=tau
tau = time[find_nearest(filtered,v_tau)] 


#Plotting
plt.figure()
plt.axvline(x=float(tau),linestyle='--')
#plt.axhline(y=float(steady_state),linestyle='--')
#plt.plot(vel_pre_filtered, color='green',  linewidth=1)#[:,0], vel[:,1])
plt.plot(timepos[:,0], vel, color='red', linewidth=1, label="Raw Velocity")
plt.plot(timepos[:,0], filtered, color = 'blue', linewidth=1, label="Filtered Velocity")
#plt.plot(timepos[:,0], np.mod(timepos[:,1], 360), color='blue')
plt.text(float(tau),np.min(filtered),f" τ={tau}", horizontalalignment='left')
plt.xlabel("Time (ms)")
plt.ylabel("Angular Velocity (°/s)")
plt.legend()
plt.title(f"Post Processing Velocity Calculation with Voltage = {voltage[0]} V")
plt.savefig(f"voltage_of_{voltage[0]}.png")
plt.show()