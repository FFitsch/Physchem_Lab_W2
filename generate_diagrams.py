import pandas as pd
import numpy as np
import matplotlib
from statistics import median_low
import matplotlib.pyplot as plot
from scipy.signal import argrelextrema
from functions import group


# ------------------------ CONFIG --------------------------
horiz_cutoff_left = -5
horiz_cutoff_right = -4
horiz_offset = 5
ambient_pressure = 1.013
extreme_val_width = 0.05
pv_1st_maxima = 1
#marked_maxima_positions = [0,1,3,4] # for start
marked_maxima_positions = [1,2] # for constant
run_pv_calculations = False
run_temp = '190'
run_start = False

volume_file = './Daten/180-Grad/1_K.csv'
v_vert_scale = 1
v_vert_pos = -1.360
v_horiz_pos = 0
v_horiz_scale = 1
v_col_time = 0
v_col_volt = 1

pressure_file = './Daten/180-Grad/2_K.csv'
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
v_data = v_data[v_data['time'] <= horiz_cutoff_right]
p_data = p_data_raw[p_data_raw['time'] >= horiz_cutoff_left]
p_data = p_data[p_data['time'] <= horiz_cutoff_right]


# vertical scale corrections
v_data.loc[:, 'v_value'] += v_vert_pos
v_data.loc[:, 'v_value'] *= v_vert_scale

p_data.loc[:, 'p_value'] += p_vert_pos
p_data.loc[:, 'p_value'] *= p_vert_scale


# horizontal scale corrections
v_data.loc[:, 'time'] += (v_horiz_pos + horiz_offset)
v_data.loc[:, 'time'] *= v_horiz_scale

p_data.loc[:, 'time'] += (p_horiz_pos + horiz_offset)
p_data.loc[:, 'time'] *= p_horiz_scale


# convert voltage into volume/pressure
v_data.loc[:, 'v_value'] = (v_data.v_value + 41)/56
p_data.loc[:, 'p_value'] = ((p_data.p_value + 1.05)/3.1) + ambient_pressure


# find local extreme values
v_data.loc[:, 'max'] = v_data.iloc[argrelextrema(v_data.v_value.values, np.greater_equal, order = 100)[0]]['v_value']
p_data.loc[:, 'max'] = p_data.iloc[argrelextrema(p_data.p_value.values, np.greater_equal, order = 100)[0]]['p_value']


# only use one extreme value per group/peak
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


# only use maxima with sufficient height
v_max_offset = v_data['v_value'].min() + ((v_data['v_value'].max() - v_data['v_value'].min()) * 0.75)
v_data_max = v_data_max[v_data_max['max'] >= v_max_offset]
v_max_list = sorted(set(v_data_max['time'].tolist()))

p_max_offset = p_data['p_value'].min() + ((p_data['p_value'].max() - p_data['p_value'].min()) * 0.75)
p_data_max = p_data_max[p_data_max['max'] >= p_max_offset]
p_max_list = sorted(set(p_data_max['time'].tolist()))

# configure plot
figure, axes = plot.subplots()

if(not run_pv_calculations):
    v_axis = axes
    p_axis = v_axis.twinx()

    v_color = 'red'
    v_axis.set_xlabel('Time (s)')
    v_axis.set_ylabel('Volume (L)', color = 'red')
    v_axis.tick_params(axis='y', labelcolor = v_color)
    v_axis.plot(v_data['time'], v_data['v_value'], label = 'volume', color = v_color)


    p_color = 'blue'
    p_axis.set_ylabel('Pressure (bar)', color = 'blue')
    p_axis.tick_params(axis='y', labelcolor = p_color)
    p_axis.plot(p_data['time'], p_data['p_value'], label = 'pressure', color = p_color)

    # v_axis.xaxis.grid(True, which='both')
    v_axis.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    v_axis.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.2))

    # figure.legend(loc='upper left')

    # only show certain maxima
    p_data_max = p_data_max[p_data_max['time'].isin([p_max_list[x] for x in marked_maxima_positions])]

    # very ugly but need a maximum and minimum volume value for Q_1
    v_data_extr_range = v_data[p_data['time'] > p_max_list[marked_maxima_positions[0]]]
    v_data_extr_range = v_data_extr_range[v_data_extr_range['time'] < p_max_list[marked_maxima_positions[1]]]

    v_data_extr_mins = v_data_extr_range[v_data_extr_range['v_value'] == v_data_extr_range.v_value.min()]
    v_data_extr_min_value = v_data_extr_mins.iloc[len(v_data_extr_mins.index)//2]

    v_data_extr_maxs = v_data_extr_range[v_data_extr_range['v_value'] == v_data_extr_range.v_value.max()]
    v_data_extr_max_value = v_data_extr_maxs.iloc[len(v_data_extr_maxs.index)//2]

    v_data_extr = pd.DataFrame.from_dict([{'time': v_data_extr_min_value['time'], 'v_value': v_data_extr_min_value['v_value']}, {'time': v_data_extr_max_value['time'], 'v_value': v_data_extr_max_value['v_value']}])

    #add maxima
    #v_axis.scatter(v_data_max['time'], v_data_max['max'], c='red')
    p_axis.scatter(p_data_max['time'], p_data_max['p_value'], c='black', zorder=5)
    # v_axis.scatter(v_data_extr['time'], v_data_extr['v_value'], c='black', zorder=6)

    p_data_max = p_data_max._append({'time': v_data_extr_min_value['time'], 'p_value': p_data[p_data['time'] == v_data_extr_min_value['time']].iloc[0]['p_value']}, ignore_index = True)

    if(run_start):
        p_data_max.to_csv(run_temp + '_pt_start.csv')
    else:
        p_data_max.to_csv(run_temp + '_pt_constant.csv')
        v_data_extr.to_csv(run_temp + '_vt_constant.csv')


# add p/v graph if program is run with constant cycle data
if(run_pv_calculations):
    pv_axes = axes

    #merge data
    pv_data = pd.merge(v_data, p_data, on='time')

    # only use one rotation worth of p/v data
    pv_data = pv_data[pv_data['time'] > p_max_list[pv_1st_maxima]]
    pv_data = pv_data[pv_data['time'] < p_max_list[pv_1st_maxima + 1]]

    pv_data[['p_value', 'v_value']].iloc[::10, :].to_csv(run_temp + '_pv_values.csv', index = False)

    pv_axes.plot(pv_data['v_value'], pv_data['p_value'])
    pv_axes.set_xlabel('Volume (L)')
    pv_axes.set_ylabel('Pressure (bar)')


# render plot
figure.set_figheight(4)
if(run_start):
    figure.set_figwidth(8)
else:
    figure.set_figwidth(5)
figure.set_dpi(200)

plot.title('190 °C')
plot.tight_layout()

if(run_pv_calculations):
    plot.savefig(run_temp + '_pv_constant.png')
elif(run_start):
    plot.savefig(run_temp + '_pvt_start.png')
else:
    plot.savefig(run_temp + '_pvt_constant.png')

plot.show()
