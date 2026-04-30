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

pos_list_x1 = [-186.5]  #####  [-171.82, -183.9, -187.91, -211.92 ] 


# array([-151.76, -155.81, -159.86, -163.76, -167.65, -171.82, -175.81,
#        -179.76, -183.9 , -187.91, -191.72, -195.78, -199.8 , -207.85,
#        -211.92, -215.95, -219.96, -223.87, -227.81, -231.72, -235.94])



#pos_list_x2 = [-223.87, -227.81, -231.72, -235.94]

 ##[-155.81, -159.86, -163.76, -167.65, -175.81, -179.76, -191.72, -195.78, -199.8, -207.85, -215.95, -219.96, -223.87, -227.81, -231.72, -235.94 ]


# pos_list_x3 = [-84, -85, -86, -87]

posy1 = [-64.9] #put the same number position as the number of sample
#posy2 = [-13.9]
# posy3 = [-41]

smpl_list_PDF_1=[63] #PDF   ##### [16, 19, 20, 25] 
#smpl_list_PDF_2=[28, 29, 30 ,31] #PDF   #####
# smpl_list_PDF_3=[0, 1, 0, 1] #PDF   #####

#smpl_list_XRD_1=[58, 59, 60]#XRD   #####
#smpl_list_XRD_2=[66] #XRD   #####
# smpl_list_XRD_3=[0, 1, 0, 1] #XRD   #####

#detector exposure time. 
# one number in List will be applied all of sample in specific y positon.
#if you want to vary detector exposure time(=frame_exp_time), you can add number for each x position.
#jog function needs to use total exposure time instead of "ScanPlan, ct=300"
#total_exp_time_PDF or _XRD is actual total exposure time for data collection (just like ScanPlan, ct=300). 

total_exp_time_PDF1 = [300]    #300  #put the same number exp time as the number of sample
frame_exp_time_PDF1 = [4]      #put the same number frame time as the number of sample

#total_exp_time_PDF2 = [120]      #put the same number exp time as the number of sample
#frame_exp_time_PDF2 = [1]      #put the same number frame time as the number of sample

#total_exp_time_XRD = [60]
#frame_exp_time_XRD = [4]

####### image number for all racks ###############
# if we have 3 racks of sample changers with "num_PDF = 4, num_XRD = 2", 
# first take 1 pdf for 3 racks, after then take 1 xrd.
# the second loop also repeat "take 1 pdf for 3 racks, after then take 1 xrd".
# the third and fourth loop only take 1 pdf for 3 racks.
# num_PDF = 2  #2
# num_XRD = 2 

#number of image at each rack
num_img_PDF_1 =50 #3
#num_img_PDF_2 = 1
# num_img_PDF_3 = 1

#num_img_XRD_1 = 0
#num_img_XRD_2 = 1
# num_img_XRD_3 = 1

# jog distance (unit: mm)
jog_dist = 0  #3    #actual distance is 2*jog_dist,  jogstart = y-jog_dist, jogstop = y +jog_dist
jog_motor = OT_stage_2_Y

#Sleep time between images
spleeptime_btw_smpl_PDF1 =120  #120 #unit: sec  sleep time between images
#spleeptime_btw_smpl_XRD = 60  #unit: sec

#spleeptime_btw_smpl_PDF2 = 120  #unit: sec  sleep time between images
#spleeptime_btw_smpl_XRD = 60  #unit: sec


################################ Measure Functions #########################################

# def one_rack_jog(smplist, posxlist, posylist, total_exp_time, frame_exp_time, 
#                  jog_motor, jogstart, jogstop, 
#                  sleeptime_btw_smpl, num_imgs=1, ):
#     """
#     This plan is for multi samples on a rack holder.
#     if len(posylist) == 1, it means y position is fixed
#     if len(total_exp_time) == 1, it means total_exp_time is fixed
#     if len(frame_exp_time) == 1, it means frame_exp_time is fixed
#     """
#     #jog_motor = OT_stage_2_Y
#     area_det = xpd_configuration['area_det']

#     for num in range (num_imgs):
#         for idx in range (len (posxlist)):
#             x = posxlist[idx]
            
#             try:
#                 y = posylist[idx]
#             except IndexError:
#                 y = posylist[-1]

#             try:
#                 tt = total_exp_time[idx]
#             except IndexErrormov:
#                 tt = total_exp_time[-1]

#             try:
#                 ft = frame_exp_time[idx]
#             except IndexError:
#                 ft = frame_exp_time[-1]
            
#             sample_name = bt.samples.sel(smplist[idx])['sample_name']
#             print(f'\nmoving OT_stage_2_X, {x = }')
#             print(f'moving OT_stage_2_Y, {y = }')
#             print(f'{smplist[idx] = }, {sample_name = }\n')
#             RE(mv(OT_stage_2_X, x, OT_stage_2_Y, y))

#             glbl['frame_acq_time'] = ft
#             tqdm_sleep(5.0, message='Sleep after changing frame time')
            
#             if 'pilatus' in area_det.name:
#                 plan = jog_pila([area_det], tt, jog_motor, jogstart, jogstop)
#                 dark_strategy=no_dark
#             else:
#                 plan = jog([area_det], tt, jog_motor, jogstart, jogstop)
#                 dark_strategy=None

#             xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=dark_strategy)

#             glbl['frame_acq_time']=0.1
#             tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
#             # glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5      


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
                plan = jog_pila2([area_det], tt, jog_motor, jogstart, jogstop)
                # dark_strategy=no_dark
                xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=no_dark)

            else:
                plan = jog([area_det], tt, jog_motor, jogstart, jogstop)
                # dark_strategy=None
                xrun(smplist[idx], plan, more_info = measurement_data())


            #xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=no_dark)
            glbl['frame_acq_time']=0.1
            tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
            #glbl['frame_acq_time']=0.5   ######## 0.5    


            #xrun(smplist[idx], plan, more_info = measurement_data(), dark_strategy=no dark)
            #glbl['frame_acq_time']=0.1
            #tqdm_sleep(sleeptime_btw_smpl, message='Sleep between Samples to clear detector')
            #glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5    


############################## Execution Measurement ##############################################


#for PDF
move_PDF()
one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, posy1, total_exp_time_PDF1, frame_exp_time_PDF1, 
                jog_motor, jog_dist, 
                spleeptime_btw_smpl_PDF1, num_imgs=num_img_PDF_1)

#sleeptime_btw_PDFXRD = 120
#glbl['frame_acq_time']=0.1
#tqdm_sleep(sleeptime_btw_PDFXRD, message='Sleep between Samples to clear detector')

#for PDF
#move_PDF()
#one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, posy2, total_exp_time_PDF2, frame_exp_time_PDF2, 
#                jog_motor, jog_dist, 
#                spleeptime_btw_smpl_PDF2, num_imgs=num_img_PDF_2)



# #for XRD
#move_XRD()
#one_rack_jog_rel(smpl_list_XRD_1, pos_list_x1, posy1, total_exp_time_XRD, frame_exp_time_XRD, 
#                 jog_motor, jog_dist, 
#                 spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_1)

#sleeptime_btw_PDFXRD = 120
#glbl['frame_acq_time']=0.1
#tqdm_sleep(sleeptime_btw_PDFXRD, message='Sleep between Samples to clear detector')


#move_PDF()
#one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, posy2, total_exp_time_PDF, frame_exp_time_PDF, 
                #jog_motor, jog_dist, 
                #spleeptime_btw_smpl_PDF, num_imgs=num_img_PDF_2)

#for XRD
#move_XRD()
#one_rack_jog_rel(smpl_list_XRD_2, pos_list_x2, posy2, total_exp_time_XRD, frame_exp_time_XRD, 
                #jog_motor, jog_dist, 
                #spleeptime_btw_smpl_XRD, num_imgs=num_img_XRD_2)
