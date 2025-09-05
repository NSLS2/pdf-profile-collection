#Hui and Gihan modify this script on May 8, 2024.


from epics import PV
from epics import caget, caput
import datetime
import numpy as np
import pylab
from pylab import *
import os
from tifffile import imsave,  imread
import sys
from itertools import zip_longest

#config_dir = "/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"

pos_list_x1 = [-84, -85, -86, -87]   #####
pos_list_x2 = [-84, -85, -86, -87]
pos_list_x3 = [-84, -85, -86, -87]

posy1 = [-43]
posy2 = [-42]
posy3 = [-41]

smpl_list_PDF_1=[0, 1, 0, 1] #PDF   #####
smpl_list_PDF_2=[0, 1, 0, 1] #PDF   #####
smpl_list_PDF_3=[0, 1, 0, 1] #PDF   #####

smpl_list_XRD_1=[0, 1, 0, 1] #XRD   #####
smpl_list_XRD_2=[0, 1, 0, 1] #XRD   #####
smpl_list_XRD_3=[0, 1, 0, 1] #XRD   #####

#detector exposure time. 
# one number in List will be applied all of sample in specific y positon.
#if you want to vary detector exposure time(=frame_exp_time), you can add number for each x position.
#jog function needs to use total exposure time instead of "ScanPlan, ct=300"
#total_exp_time_PDF or _XRD is actual total exposure time for data collection (just like ScanPlan, ct=300). 
total_exp_time_PDF = [60]
frame_exp_time_PDF = [0.2]
total_exp_time_XRD = [60]
frame_exp_time_XRD = [0.2]

####### image number for all racks ###############
# if we have 3 racks of sample changers with "num_PDF = 4, num_XRD = 2", 
# first take 1 pdf for 3 racks, after then take 1 xrd.
# the second loop also repeat "take 1 pdf for 3 racks, after then take 1 xrd".
# the third and fourth loop only take 1 pdf for 3 racks.
num_PDF = 2  #2
num_XRD = 2 

#number of image at each rack
num_img_PDF_1 = 1
num_img_PDF_2 = 1
num_img_PDF_3 = 1
num_img_XRD_1 = 1
num_img_XRD_2 = 1
num_img_XRD_3 = 1

# jog distance (unit: mm)
jog_dist = 3    #actual distance is 2*jog_dist,  jogstart = y-jog_dist, jogstop = y +jog_dist

#Sleep time between images
spleeptime_btw_smpl_PDF = 60  #unit: sec
spleeptime_btw_smpl_XRD = 60  #unit: sec

D1 = 3011   # Det_1_Z position for PDF
D2 = 3011 + 777 # Det_1_Z positio for XRD


################################ Measure Functions #########################################

# def measurement_data(): # .......Captures metadata   ## Already lodaed into bsui from 98-CHL_EPICS_function.py
#     info_dict = {}
#     info_dict['OT_stage_2_X'] = OT_stage_2_X.read()
#     info_dict['OT_stage_2_Y'] = OT_stage_2_Y.read()
#     info_dict['Det_1_X'] = Det_1_X.read()
#     info_dict['Det_1_Y'] = Det_1_Y.read()
#     info_dict['Det_1_Z'] = Det_1_Z.read()
#     info_dict['ring_current'] = ring_current.read()
#     info_dict['frame_acq_time'] = glbl['frame_acq_time']
#     info_dict['dk_window'] = glbl['dk_window']
#     info_dict['Temperature'] = cryostream.T.get()
#     info_dict['Measurement_time'] = time.time()
#     return info_dict

def move_PDF():
    Det_1_Z.move(D1)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "/PDF/" + "Mask.npy" , config_dir)

def move_XRD():
    Det_1_Z.move(D2)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "/XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "/XRD/" + "Mask.npy" , config_dir)



def one_rack_jog(smplist, posxlist, posylist, total_exp_time, frame_exp_time, 
                 jog_motor, jogstart, jogstop, 
                 sleeptime_btw_smpl, num_imgs=1, ):
    """
    This plan is for multi samples on a rack holder.
    if len(posylist) == 1, it means y position is fixed
    if len(total_exp_time) == 1, it means total_exp_time is fixed
    if len(frame_exp_time) == 1, it means frame_exp_time is fixed
    """
    #jog_motor = OT_stage_2_Y
    area_det = xpd_configuration['area_det']

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            x = posxlist[idx]
            
            try:
                y = posylist[idx]
            except IndexError:
                y = posylist[-1]

            try:
                tt = total_exp_time[idx]
            except IndexError:
                tt = total_exp_time[-1]

            try:
                ft = frame_exp_time[idx]
            except IndexError:
                ft = frame_exp_time[-1]
            
            sample_name = bt.samples.sel(smplist[idx])['sample_name']
            print(f'\nmoving OT_stage_2_X, {x = }')
            print(f'moving OT_stage_2_Y, {y = }')
            print(f'{smplist[idx] = }, {sample_name = }\n')
            RE(mv(OT_stage_2_X, x, OT_stage_2_Y, y))

            glbl['frame_acq_time'] = ft
            tqdm_sleep(5.0, message='Sleep after changing frame time')
            
            if 'pilatus' in area_det.name:
                plan = jog_pila([area_det], tt, jog_motor, jogstart, jogstop)
                dark_strategy=no_dark
            else:
                plan = jog([area_det], tt, jog_motor, jogstart, jogstop)
                dark_strategy=None

            xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=dark_strategy)

            glbl['frame_acq_time']=0.1
            tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
            # glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5      


def one_rack_jog_rel(smplist, posxlist, posylist, total_exp_time, frame_exp_time, 
                     jog_motor, jog_dist, 
                     sleeptime_btw_smpl, num_imgs=1, ):
    """
    This plan is for multi samples on a rack holder.
    if len(posylist) == 1, it means y position is fixed
    if len(total_exp_time) == 1, it means total_exp_time is fixed
    if len(frame_exp_time) == 1, it means frame_exp_time is fixed
    """
    #jog_motor = OT_stage_2_Y
    area_det = xpd_configuration['area_det']

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            x = posxlist[idx]
            
            try:
                y = posylist[idx]
            except IndexError:
                y = posylist[-1]

            jogstart = y-jog_dist
            jogstop = y +jog_dist

            try:
                tt = total_exp_time[idx]
            except IndexError:
                tt = total_exp_time[-1]

            try:
                ft = frame_exp_time[idx]
            except IndexError:
                ft = frame_exp_time[-1]
            
            sample_name = bt.samples.sel(smplist[idx])['sample_name']
            print(f'\nmoving OT_stage_2_X, {x = }')
            print(f'moving OT_stage_2_Y, {y = }')
            print(f'{smplist[idx] = }, {sample_name = }\n')
            RE(mv(OT_stage_2_X, x, OT_stage_2_Y, y))

            glbl['frame_acq_time'] = ft
            tqdm_sleep(5.0, message='Sleep after changing frame time')
            
            if 'pilatus' in area_det.name:
                plan = jog_pila([area_det], tt, jog_motor, jogstart, jogstop)
                dark_strategy=no_dark
            else:
                plan = jog([area_det], tt, jog_motor, jogstart, jogstop)
                dark_strategy=None

            xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=dark_strategy)

            glbl['frame_acq_time']=0.1
            tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
            # glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5    


############################## Execution Measurement ##############################################

for p, x in zip_longest(range(num_PDF), range(num_XRD), fillvalue=None):

    if p is not None:
        move_PDF()

        #rack1
        one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, posy1, total_exp_time_PDF, frame_exp_time_PDF, 
                        jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_1)

        #rack2
        one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, posy2, total_exp_time_PDF, frame_exp_time_PDF, 
                        jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_2)

        #rack3
        one_rack_jog_rel(smpl_list_PDF_3, pos_list_x3, posy3, total_exp_time_PDF, frame_exp_time_PDF, 
                        jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_3)

        # #rack4
        # one_rack_jog_rel(smpl_list_PDF_4, pos_list_x4, posy4, total_exp_time_PDF, frame_exp_time_PDF, 
        #                 jog_dist, spleeptime_btw_smpl_PDF, num_imgs=1)


    if x is not None:
        move_XRD()

        #rack1
        one_rack_jog_rel(smpl_list_XRD_1, pos_list_x1, posy1, total_exp_time_XRD, frame_exp_time_XRD, 
                        jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_1)

        #rack2
        one_rack_jog_rel(smpl_list_XRD_2, pos_list_x2, posy2, total_exp_time_XRD, frame_exp_time_XRD, 
                        jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_2)

        #rack3
        one_rack_jog_rel(smpl_list_XRD_3, pos_list_x3, posy3, total_exp_time_XRD, frame_exp_time_XRD, 
                        jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_3)

        # #rack4
        # one_rack_jog_rel(smpl_list_XRD_4, pos_list_x4, posy4, total_exp_time_XRD, frame_exp_time_XRD, 
        #                 jog_dist, spleeptime_btw_smpl_XRD, num_imgs=1)  



