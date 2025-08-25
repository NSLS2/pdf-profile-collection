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

glbl['dk_window']=0.1


def move_PDF():
    Det_1_Z.move(D1)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass      
    shutil.copy(config_dir + "/PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/PDF/" + "Mask.npy" , config_dir)


def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['Det_2_X'] = Det_1_X.read()
    info_dict['Det_2_Y'] = Det_1_Y.read()
    info_dict['Det_2_Z'] = Det_1_Z.read()
    info_dict['OT_stage_X'] = OT_stage_2_X.read()
    info_dict['OT_stage_Y'] = OT_stage_2_Y.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']
    info_dict['Measurement_time'] = time.time()
    return info_dict

def one_rack_jog(smplist, posxlist, posy, exp_time, jogstart, jogstop, num_PDF=3, det_exp_PDF=0.5):

    '''

    ###--> want to measure sample at only a positon of y.
    posylist=[27]
    smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
    for posy, smpl in zip(posylist, smplist):
         print(posy, smpl)
     
    27 [1, 2, 3, 4]
    '''
    #jog_motor = OT_stage_2_Y
    area_det = xpd_configuration['area_det']
    RE(mv(OT_stage_2_Y, posy))
    for num in range (num_PDF):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            print(smplist[idx])
            plan = jog([area_det], exp_time, OT_stage_2_Y,jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(1)    ### 90
            glbl['frame_acq_time']=det_exp_PDF   ######## 0.5        


def one_rack(smplist, posxlist, posy, ScanPlan_PDF, num_PDF=3, det_exp_PDF=0.5):

    '''

    ###--> want to measure sample at only a positon of y.
    posylist=[27]
    smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
    for posy, smpl in zip(posylist, smplist):
         print(posy, smpl)
     
    27 [1, 2, 3, 4]
    '''
    RE(mv(OT_stage_2_Y, posy))
    for num in range (num_PDF):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            print(smplist[idx])

            xrun(smplist[idx], ScanPlan_PDF, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(1)    ### 90
            glbl['frame_acq_time']=det_exp_PDF   ######## 0.5        


D1 = 4309   # Det_1_Z position

pos_list_x1 = [-84, -85, -86, -87]   #####\
pos_list_x2 = [-84, -85, -86, -87]
pos_list_x3 = [-84, -85, -86, -87]


posy1 = -43
posy2 = -42
posy3 = -41



smpl_list_PDF_1=[0, 1, 0, 1]#PDF   #####
smpl_list_PDF_2=[0, 1, 0, 1]#PDF   #####
smpl_list_PDF_3=[0, 1, 0, 1] #PDF   #####


#detector exposure time
det_exp_PDF = 0.1  #0.5
 
# image number
num_PDF = 1  #2

#Scanplan (ct_60,,,,)
ScanPlan_PDF = 2  #6 ct_60

#move_PDF()
glbl['frame_acq_time']=0.1

'''
#Air PDF
glbl['frame_acq_time']=2 #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
move_PDF()
RE(mv(OT_stage_2_X, -136.27))
for x in range(3):   #4
	xrun(110, 9, more_info = measurement_data())   #9
     
glbl['frame_acq_time']=0.1
time.sleep(120) ### 120
'''

#PDF1
glbl['frame_acq_time']=det_exp_PDF #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
#move_PDF()
time.sleep(2) ### 10


one_rack_jog(smpl_list_PDF_1, pos_list_x1, posy1 , 10, posy1, posy1+3, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)

'''

one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)
glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90
one_rack(smpl_list_PDF_2, pos_list_x2, posy2 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)
glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90
one_rack(smpl_list_PDF_3, pos_list_x3, posy3 , ScanPlan_PDF, num_PDF=num_PDF, det_exp_PDF=det_exp_PDF)

'''