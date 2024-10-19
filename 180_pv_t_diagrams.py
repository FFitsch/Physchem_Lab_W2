import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plot
from scipy.signal import argrelextrema


# ------------------------ CONFIG --------------------------
volume_file = './Daten/180-Grad/1_K.csv'
pressure_file = './Daten/180-Grad/2_K.csv'
horiz_cutoff_left = -5
horiz_cutoff_right = -2
horiz_offset = 5
ambient_pressure = 1.013

v_vert_scale = 1
v_vert_pos = -1.360
v_horiz_pos = 0
v_horiz_scale = 1
v_col_time = 0
v_col_volt = 1


p_vert_scale = 0.2
p_vert_pos = -1.904
p_horiz_pos = 0
p_horiz_scale = 1
p_col_time = 0
p_col_volt = 1
# ----------------------------------------------------------



# import data
v_data_raw = pd.read_csv(volume_file, skiprows=28, usecols=[v_col_time,v_col_volt], names=['time','v_value'])
p_data_raw = pd.read_csv(pressure_file, skiprows=28, usecols=[p_col_time,p_col_volt], names=['time','p_value'])

# set which portions of the data are shown
v_data = v_data_raw[v_data_raw['time'] >= horiz_cutoff_left]
v_data = v_data_raw[v_data_raw['time'] <= horiz_cutoff_right]
p_data = p_data_raw[p_data_raw['time'] >= horiz_cutoff_left]
p_data = p_data_raw[p_data_raw['time'] <= horiz_cutoff_right]

# vertical scale corrections
v_data.loc[:, 'v_value'] += v_vert_pos
v_data.loc[:, 'v_value'] *= v_vert_scale

p_data.loc[:, 'p_value'] += p_vert_pos
p_data.loc[:, 'p_value'] *= p_vert_scale

# horizontal scale corrections
v_data.loc[:, 'v_value'] += v_horiz_pos + horiz_offset
v_data.loc[:, 'v_value'] *= v_horiz_scale

p_data.loc[:, 'p_value'] += p_horiz_pos + horiz_offset
p_data.loc[:, 'p_value'] *= p_horiz_scale

# convert voltage into volume/pressure
v_data.loc[:, 'v_value'] = (v_data.v_value + 41)/56
p_data.loc[:, 'p_value'] = ((p_data.p_value - 1.05)/3.1) + ambient_pressure


#lets find some local extreme values
v_data.loc[:, 'max'] = v_data.iloc[argrelextrema(v_data.v_value.values, np.greater_equal, order = 100)[0]]['v_value']
p_data.loc[:, 'max'] = p_data.iloc[argrelextrema(p_data.p_value.values, np.greater_equal, order = 100)[0]]['p_value']

# configure plot
figure, v_axis = plot.subplots()
p_axis = v_axis.twinx()

v_color = 'red'
v_axis.set_xlabel('Time (s)')
v_axis.set_ylabel('Volume ()')
v_axis.tick_params(axis='y', labelcolor = v_color)
v_axis.plot(v_data['time'], v_data['v_value'], label = 'volume', color = v_color)


p_color = 'blue'
p_axis.set_ylabel('Pressure (bar)')
p_axis.tick_params(axis='y', labelcolor = p_color)
p_axis.plot(p_data['time'], p_data['p_value'], label = 'pressure', color = p_color)

v_axis.xaxis.grid(True, which='both')
v_axis.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
v_axis.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.2))

figure.legend(loc='upper left')

#add maxima
v_axis.scatter(v_data['time'], v_data['max'], c='red')
p_axis.scatter(p_data['time'], p_data['max'], c='blue')


plot.tight_layout()

# render plot
#plot.savefig('test.png')
plot.show()




















# center y values around 0
#v_start.volt -= (v_start.volt.max()/2 + v_start.volt.min()/2)
#p_start.volt -= (p_start.volt.max()/2 + p_start.volt.min()/2)

# normalize y axis
#v_start.volt /= v_start.volt.abs().max()
#p_start.volt /= p_start.volt.abs().max()

#plot.plot(v_start['second'], v_start['volt'], label = 'volume', color = 'orange')
#plot.plot(p_start['second'], p_start['volt'], label = 'pressure', color = 'blue')
#plot.legend(loc='upper left')
#plot.show()