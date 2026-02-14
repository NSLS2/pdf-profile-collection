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

pos_list_x1 = [-131.5,  -135.67, -139.58, -143.49, -147.66, -151.56]   #####low int.
pos_list_x2 = [-162.6]   #####medium int.
# pos_list_x3 = [-95.58, -99.58, -103.6, -107.74, -115.57, -119.67, -123.49, -127.61]   #####high int.
#pos_list_x4 = [-144.05, -148.05, -152.05]   #####staturate det.

posy1 = [21.2]
posy2 = [21.2]
#posy3 = [21.2]
#posy4 = [21.2]


# array([ -131.5,  -135.67, -139.58, -143.49, -147.66, -151.56,-162.6])



smpl_list_PDF_1=[104, 105, 106, 107, 108, 109] #PDF   #####
smpl_list_PDF_2=[111] #PDF   #####
# smpl_list_PDF_3=[56, 57, 58, 59, 61, 62, 63, 64] #PDF   #####
#smpl_list_PDF_4=[18, 19, 20] #PDF   #####

smpl_list_XRD_1=[118, 119, 120, 121, 122, 123] #XRD   #####
smpl_list_XRD_2=[125] #XRD   #####
# smpl_list_XRD_3=[73, 74, 75, 76, 78, 79, 80, 81] #XRD   #####
#smpl_list_XRD_4=[36, 37, 38] #XRD   #####

#detector exposure time. 
# one number in List will be applied all of sample in specific y positon.
#if you want to vary detector exposure time(=frame_exp_time), you can add number for each x position.
#jog function needs to use total exposure time instead of "ScanPlan, ct=300"
#total_exp_time_PDF or _XRD is actual total exposure time for data collection (just like ScanPlan, ct=300). 
total_exp_time_PDF1 = [300]*len(pos_list_x1)  # [120, 120, 120, 120] 
frame_exp_time_PDF1 = [4]*len(pos_list_x1)
total_exp_time_PDF2 = [120]*len(pos_list_x2)  # [120, 120, 120, 120] 
frame_exp_time_PDF2 = [0.5]*len(pos_list_x2)
# total_exp_time_PDF3 = [120]*len(pos_list_x3)  # [120, 120, 120, 120] 
# frame_exp_time_PDF3 = [0.1]*len(pos_list_x3)
# total_exp_time_PDF4 = [60]*len(pos_list_x4)  # [120, 120, 120, 120] 
# frame_exp_time_PDF4 = [0.1]*len(pos_list_x4)

total_exp_time_XRD1 = [120]*len(pos_list_x1) #[60, 60, 60, 60]
frame_exp_time_XRD1 = [4]*len(pos_list_x1)
total_exp_time_XRD2 = [60]*len(pos_list_x2) #[60, 60, 60, 60]
frame_exp_time_XRD2 = [0.3]*len(pos_list_x2)
# total_exp_time_XRD3 = [60]*len(pos_list_x3) #[60, 60, 60, 60]
# frame_exp_time_XRD3 = [0.1]*len(pos_list_x3)
# total_exp_time_XRD4 = [60]*len(pos_list_x4) #[60, 60, 60, 60]
# frame_exp_time_XRD4 = [0.1]*len(pos_list_x4)

####### image number for all racks ###############
# if we have 3 racks of sample changers with "num_PDF = 4, num_XRD = 2", 
# first take 1 pdf for 3 racks, after then take 1 xrd.
# the second loop also repeat "take 1 pdf for 3 racks, after then take 1 xrd".
# the third and fourth loop only take 1 pdf for 3 racks.
num_PDF = 5  #3
num_XRD = 3  #2

#number of image at each rack (Do not change)
num_img_PDF_1 = 1
num_img_PDF_2 = 1
# num_img_PDF_3 = 1
# num_img_PDF_4 = 1

num_img_XRD_1 = 1
num_img_XRD_2 = 1
# num_img_XRD_3 = 1
# num_img_XRD_4 = 1

# jog distance (unit: mm)
jog_dist = 0    #actual distance is 2*jog_dist,  jogstart = y-jog_dist, jogstop = y +jog_dist
jog_motor = OT_stage_2_X

#Sleep time between images
spleeptime_btw_smpl_PDF = 120  #unit: sec
spleeptime_btw_smpl_XRD = 60  #unit: sec

D1 = 2553   # Det_1_Z position for PDF
D2 = 3321 # Det_1_Z positio for XRD


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

config_dir = '/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/'

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
    if len(frame_exp_time) == 1, it means frame_exp_time is xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=dark_strategy)fixed
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

            #xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=dark_strategy)
            xrun(smplist[idx], plan, more_info = measurement_data())

            glbl['frame_acq_time']=0.1
            tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
            # glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5    


############################## Execution Measurement ##############################################

for p, x in zip_longest(range(num_PDF), range(num_XRD), fillvalue=None):

    if p is not None:
        move_PDF()

        #rack1
        one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, posy1, total_exp_time_PDF1, frame_exp_time_PDF1, 
                        jog_motor, jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_1)

        #rack2
        one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, posy2, total_exp_time_PDF2, frame_exp_time_PDF2, 
                        jog_motor, jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_2)

        # #rack3
        # RE(mv(fb2.flt2, 0))
        # RE(mv(fb2.flt3, 0))
        # one_rack_jog_rel(smpl_list_PDF_3, pos_list_x3, posy3, total_exp_time_PDF3, frame_exp_time_PDF3, 
        #                 jog_motor, jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_3)
        # RE(mv(fb2.flt2, 1))
        # RE(mv(fb2.flt3, 1))


        # # #rack4
        # RE(mv(fb2.flt3, 0))
        # one_rack_jog_rel(smpl_list_PDF_4, pos_list_x4, posy4, total_exp_time_PDF4, frame_exp_time_PDF4, 
        #                 jog_motor, jog_dist, spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_4)
        # RE(mv(fb2.flt3, 1))


    if x is not None:
        move_XRD()

        #rack1
        one_rack_jog_rel(smpl_list_XRD_1, pos_list_x1, posy1, total_exp_time_XRD1, frame_exp_time_XRD1, 
                        jog_motor, jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_1)

        #rack2
        one_rack_jog_rel(smpl_list_XRD_2, pos_list_x2, posy2, total_exp_time_XRD2, frame_exp_time_XRD2, 
                        jog_motor, jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_2)

        # #rack3
        # RE(mv(fb2.flt2, 0))
        # RE(mv(fb2.flt3, 0))
        # one_rack_jog_rel(smpl_list_XRD_3, pos_list_x3, posy3, total_exp_time_XRD3, frame_exp_time_XRD3, 
        #                 jog_motor, jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_3)
        # RE(mv(fb2.flt2, 1))
        # RE(mv(fb2.flt3, 1))

        # # #rack4
        # RE(mv(fb2.flt3, 0))
        # one_rack_jog_rel(smpl_list_XRD_4, pos_list_x4, posy4, total_exp_time_XRD4, frame_exp_time_XRD4, 
        #                 jog_motor, jog_dist, spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_4)
        # RE(mv(fb2.flt3, 1))



