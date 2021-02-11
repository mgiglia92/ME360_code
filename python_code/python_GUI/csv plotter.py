import matplotlib.pyplot as plt
import csv
import os 

os.chdir(r"C:\Users\qwert\Desktop\Python VSCode") #Change directory
x = []
y1 = []
y2 = []
y3 = []
def csv2list(input):
    with open(input,'r') as csvfile:
        next(csvfile, None)
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(float(row[0]))
            y1.append(float(row[1]))
            y2.append(float(row[2]))
            y3.append(float(row[3]))
csv2list('newest.csv')

plt.plot(x,y1, label='response')
plt.plot(x,y2, label='setpoint')
plt.plot(x,y3, label='pwm')
plt.xlabel('Time')
plt.ylabel('Data')
plt.title('Data from PyQt')
plt.legend()
plt.show()