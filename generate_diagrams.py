import pandas as pd
import numpy as np
import matplotlib
from statistics import median_low
import matplotlib.pyplot as plot
from scipy.signal import argrelextrema
from functions import group


# ------------------------ CONFIG --------------------------
volume_file = './Daten/180-Grad/1_K.csv'
pressure_file = './Daten/180-Grad/2_K.csv'
horiz_cutoff_left = -5
horiz_cutoff_right = -2
horiz_offset = 5
ambient_pressure = 1.013
extreme_val_width = 0.05
pv_calculations = True

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


#find local extreme values
v_data.loc[:, 'max'] = v_data.iloc[argrelextrema(v_data.v_value.values, np.greater_equal, order = 100)[0]]['v_value']
p_data.loc[:, 'max'] = p_data.iloc[argrelextrema(p_data.p_value.values, np.greater_equal, order = 100)[0]]['p_value']


#only use one extreme value per group/peak
v_data_max = v_data.dropna(subset='max')
v_data_max_groups = group(v_data_max['time'], extreme_val_width)
v_max_list = []
for g in v_data_max_groups:
    v_max_list.append(median_low(g))

v_data_max = v_data_max[v_data_max['time'].isin(v_max_list)]

p_data_max = p_data.dropna(subset='max')
p_data_max_groups = group(p_data_max['time'], extreme_val_width)
p_max_list = []
for g in p_data_max_groups:
    p_max_list.append(median_low(g))

p_data_max = p_data_max[p_data_max['time'].isin(p_max_list)]


# configure plot
if(pv_calculations):
    figure, axes = plot.subplots(1, 2)
    v_axis = axes[0]
    pv_axes = axes[1]
else:
    figure, axes = plot.subplots()
    v_axis = axes

p_axis = v_axis.twinx()

v_color = 'red'
v_axis.set_xlabel('Time (s)')
v_axis.set_ylabel('Volume (L)')
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
v_axis.scatter(v_data_max['time'], v_data_max['max'], c='red')
p_axis.scatter(p_data_max['time'], p_data_max['max'], c='blue')

plot.tight_layout()

# add p/v graph if program is run with constant cycle data
if(pv_calculations):
    #merge data
    pv_data = pd.merge(v_data, p_data, on='time')

    # only use one rotation worth of p/v data
    #pv_data = pv_data[pv_data['time'] < v_data_max[v_data_max['v_value'] == sorted(set(v_max_list))[-2]]['time'].iloc[0]]
    #pv_data = pv_data[pv_data['time'] > v_data_max[v_data_max['v_value'] == sorted(set(v_max_list))[-3]]['time'].iloc[0]]

    pv_axes.plot(pv_data['v_value'], pv_data['p_value'])
    pv_axes.set_xlabel('Volume (L)')
    pv_axes.set_ylabel('Pressure (bar)')
    pv_axes.legend(loc='upper right')


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