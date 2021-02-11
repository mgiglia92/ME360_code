import matplotlib.pyplot as plt
import csv
import os 
 
os.chdir(r"D:\\") #Change directory
x = []
y1 = []
y2 = []
 
def csv2list(input):
    with open(input,'r') as csvfile:
        next(csvfile, None)
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(float(row[0]))
            y1.append(float(row[1]))
            y2.append(float(row[2]))
 
csv2list('test1.csv')
 
plt.plot(x,y1, label='y1')
plt.plot(x,y2, label='y2')
plt.xlabel('x')
plt.ylabel('Data')
plt.title('Data from PyQt')
plt.legend()
plt.show()