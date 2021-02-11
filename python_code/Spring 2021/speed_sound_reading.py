import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import argparse
import atexit
from time import sleep

def main(c):
    global raw_data
    global sample_time
    global N
    global fs
    # Start recording of data on arduino
    if c == 'r':
        print('Recording...',end='',flush=True)
        ser.write(b'R1,%')
        sleep(sample_time)
        print('Done.')

    # Loop through saved data on arduino
    # Each data point line ends with \0
    # End of data ends with '#'
    if c == 's':
        print('Sending Data...',end='',flush=True)
        # Initialize data list
        raw_data=[]
        # Continue reading the data until '#' is found
        while(1):

            ser.write(b'R0%') # Request a data point from arduino
            line = [] # initialize as empty array, line buffer 
            string_buff='' # intiailze as empty string
            while(1): # Read char by char until '\0' found
                if(ser.in_waiting > 0): # if data in buffer read
                    line.append(ser.read(1).decode()) # Read 1 character and decode from bytes to characters
                if '\0' in line: break # if '\0' found break out of line loop
            # print(''.join(line)) # See line received
            raw_data.append(''.join(line)) # Append line read (joined as one single string)  to data block
            if '#' in line: # if '#' found break out of reading loop
                break
        print('Done.')
    if c =='p':
        #TODO: Fix plotting, y-axis is upside down
        plot_data = decipher_raw_data(raw_data)
        # fig = plt.figure(1)
        # plt.clf()
        # dnp = plot_data.to_numpy()
        time = plot_data['T']
        A = plot_data['A']
        B = plot_data['B']
        # print(time)
        # print(A)

        #setup plotting
        #TODO: clean up figure and plotting
        # plt.xticks([])
        
        plt.plot(time, A)
        plt.plot(time,B)
        plt.ylim((0,2**12-1))
        plt.show()     

    if c == 't':
        fs = int(input('Specify Sampling Rate (fs): '));
        N = int(input('Specify Number of Samples (N): '));
        
        dt = 1/fs;
        sample_time = N*dt;
        write_string = f"S0,N{N},%".encode('utf-8')
        ser.write(write_string)
    
        write_string = f"S1,T{fs},%".encode('utf-8')
        ser.write(write_string)

# Convert each line of data into pandas array
def decipher_raw_data(d:list):
    # Get first letter of each segment separated by commas
    # Give the pandas dataframe column names
    col_name = [i[0] for i in d[0].split(',')[:-1]]

    # Initialize data buffers
    buff=[]
    for row in d:
        # Get all but first character in each segment separated by commas
        # Get all the numbers in the data into a 2d list
        new_data = row.split(',')[:-1]
        # print(new_data)
        buff.append([float(j[1:]) for j in new_data])
    # print(col_name)
    df = pd.DataFrame(buff, columns=col_name)
    # print(df)
    return df
    
def on_quit():
    if ser.is_open:
        ser.close()
        print("Serial closed.")

atexit.register(on_quit)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="COM PORT")
    parser.add_argument('--port', dest='port', required=True)
    args = parser.parse_args()
    port = args.port
        
    # port = "COM3"
    ser = serial.Serial(port=port)
    ser.flush()
    
    fs = 1000;
    N = 1000;
    dt = 1/fs;
    sample_time = N*dt;
    
    write_string = f"S0,N{N},%".encode('utf-8')
    ser.write(write_string)
    
    write_string = f"S1,T{fs},%".encode('utf-8')
    ser.write(write_string)
    
    # write_string = f"S0,T{dt},%".encode()
    # ser.write(write_string)
    
    global raw_data
    raw_data=[]
    line=[]
    buff = []
    d = ''
    # df: pd.DataFrame
    while(1):
        try:
            uin = input('r: record, s: send, p: plot, t: change settings, q: quit\n')
            if(uin=='q'):break
            main(uin)
        except Exception as e:
            print(e)