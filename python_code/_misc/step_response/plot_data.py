import numpy as np
import plotly.express as px
import pandas as pd

def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

# # plot Speed
# t, counter, motorPWM = np.loadtxt('angle_PID.txt',delimiter = ',',unpack = True)
# # print(t,data)

# ppr = 600
# coeff = float(60*1000/ppr)
# speed = np.divide(np.diff(counter)*coeff,np.diff(t))
# # speed = smooth(speed,window_len=11,window='hamming')
# try:
#     fig = px.line(x=t[:-1],y=speed,
#                 labels = {'x':"Time [ms]",'y':"Speed [RPM]"},title="Motor Step response",
#                 range_y = [-10,450])
# except:
#     fig = px.line(x=t,y=speed[0:t.size],
#                 labels = {'x':"Time [ms]",'y':"Speed [RPM]"},title="Motor Step response",
#                 range_y = [-10,450])
# fig.show()

# Plot enc_count and PWM input
df = pd.read_csv("angle_PID.txt",sep = ",", header = None, names = ['time','enc_count','motorPWM'])
# df.plot(x = 'time',y = ['enc_count','motorPWM'])
df_melt = df.melt(id_vars='time', value_vars=['enc_count', 'motorPWM'])
fig = px.line(df_melt, x = "time",y = "value",color = 'variable')
fig.show()