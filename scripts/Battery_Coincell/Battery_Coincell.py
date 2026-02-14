

from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys


####Only XRD measurement
####Detector position on XRD measurement

sample_ID = []
scan_plan = []

xstage = OT_stage_2_X
ystage = OT_stage_2_Y

pos_x = [158.15, 158.15, 158.15, 158.15, 158.15, 158.15]
pos_y = [158.15, 158.15, 158.15, 158.15, 158.15, 158.15]

det_exp_time = []

sleep_time = [60,60,60,60,60,60] # or put list = [x,x,x,x,x,x] length needs to be same as sample_ID

glbl['dk_window']=0.1
glbl['frame_acq_time']=0.1 #XRD det exposure time in situ cells 
xpd_configuration["area_det"] = pe1c #pilatus1 # pe1c, pe2c

#if you use Pilatus detector
# dark_strategy = no_dark

#if you use PE detector
dark_strategy = None

number_of_repeat = 10000

def tqdm_sleep(rest_time, message='Sleep'):
    from tqdm import tqdm
    for j in tqdm(range(0,100), desc=message):
        time.sleep(rest_time/100)


for num in range (number_of_repeat):  #10000$$$$$$$$$$$$$
    
    for i in range(len(sample_ID)):

        glbl['frame_acq_time'] = det_exp_time[i]
        RE(mv(xstage, pos_x[i], ystage, pos_y[i]))
        xrun(sample_ID[i], scan_plan[i], useful_info = measurement_data(), dark_strategy=dark_strategy)

        try:
            tqdm_sleep(sleep_time[i], message='Sleep after changing sample')    #if you use "list", use tqdm_sleep(sleep_time, )
        except (KeyError, ValueError):
            tqdm_sleep(sleep_time[0], message='Sleep after changing sample')