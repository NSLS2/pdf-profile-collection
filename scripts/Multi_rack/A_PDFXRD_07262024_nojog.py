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

config_dir = "/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/"

def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['OT_stage_2_X'] = OT_stage_2_X.read()
    info_dict['OT_stage_2_Y'] = OT_stage_2_Y.read()
    info_dict['Det_1_X'] = Det_1_X.read()
    info_dict['Det_1_Y'] = Det_1_Y.read()
    info_dict['Det_1_Z'] = Det_1_Z.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']
    info_dict['Temperature'] = cryostream.T.get()
    info_dict['Measurement_time'] = time.time()
    return info_dict

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


def one_rack_jog(smplist, posxlist, posylist, exp_time, jogstart, jogstop, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep):
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

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            print('moving OT_stage_2_Y', posylist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            RE(mv(OT_stage_2_Y, posylist[idx]))
            print(smplist[idx])
            plan = jog([area_det], exp_time, OT_stage_2_Y, jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(sleeptime_btw_smpl)    ### 90
            glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5        

def one_rack_jog_rel(smplist, posxlist, posylist, exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep):
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

    for num in range (num_imgs):
        for idx in range (len (posxlist)):
            print('moving OT_stage_2_X', posxlist[idx])
            print('moving OT_stage_2_Y', posylist[idx])
            RE(mv(OT_stage_2_X, posxlist[idx]))
            RE(mv(OT_stage_2_Y, posylist[idx]))
            print(smplist[idx])
            jogstart = posylist[idx]-jog_dist
            jogstop = posylist[idx] +jog_dist
            plan = jog([area_det], exp_time, OT_stage_2_Y, jogstart, jogstop)
            xrun(smplist[idx], plan, more_info = measurement_data())
            print('sleep')
            glbl['frame_acq_time']=0.1
            time.sleep(sleeptime_btw_smpl)    ### 90
            glbl['frame_acq_time']=det_exp_for_sleep   ######## 0.5  


# #def one_rack(smplist, posxlist, posy, ScanPlan, num_imgs, det_exp, sleeptime_btw_smpl):
#     '''
#     ###--> want to measure sample at only a positon of y.
#     posylist=[27]
#     smplist=[[1,2,3,4]]  #requaiare double brackets [[ ]]
#     for posy, smpl in zip(posylist, smplist):
#          print(posy, smpl)
     
#     27 [1, 2, 3, 4]
#     '''
#     RE(mv(OT_stage_2_Y, posy))
#     for num in range (num_imgs):
#         for idx in range (len (posxlist)):
#             print('moving OT_stage_2_X', posxlist[idx])
#             RE(mv(OT_stage_2_X, posxlist[idx]))
#             print(smplist[idx])

#             xrun(smplist[idx], ScanPlan, more_info = measurement_data())
#             print('sleep')
#             glbl['frame_acq_time']=0.1
#             time.sleep(sleeptime_btw_smpl)    ### 60
#             glbl['frame_acq_time']=det_exp   ######## 0.2        


D1 = 3011   # Det_1_Z position for PDF
D2 = 3011 + 777 # Det_1_Z positio for XRD



'''
pos_list_x1 = [-84, -85, -86, -87]   #####
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
det_exp_XRD = 1  #0.5



# image number
num_PDF = 2  #2
num_XRD = 2 

#Scanplan (ct_60,,,,)
ScanPlan_PDF = 4  #6 ct_60
ScanPlan_XRD = 5  #6 ct_120

#Sleep time between images
spleeptime_btw_smpl_PDF = 60  #unit: sec
spleeptime_btw_smpl_XRD = 60  #unit: sec

'''

'''

###############################################################################===========================================================================
###example PDF and XRD
#take images at PDF detector position
move_PDF()
one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan=ScanPlan_PDF, num_imgs=num_PDF, det_exp=det_exp_PDF, spleeptime_btw_smpl=spleeptime_btw_smpl_PDF)

glbl['frame_acq_time']=0.1
time.sleep(2)    ### 90

#take images at XRD detector position
move_XRD()
one_rack(smpl_list_PDF_1, pos_list_x1, posy1 , ScanPlan=ScanPlan_XRD, num_imgs=num_XRD, det_exp=det_exp_XRD, spleeptime_btw_smpl=spleeptime_btw_smpl_XRD)

glbl['frame_acq_time']=0.1
#####################################################################======================================================================================


#PDF1
glbl['frame_acq_time']=det_exp_PDF #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
#move_PDF()
time.sleep(2) ### 10


def jog(dets, exposure_s, motor, start, stop, md=None):
    """pass total exposure time (in seconds), motor name (i.e. Grid_Y), start and stop positions for the motor."""
    # yield from rocking_ct([pilatus], exposure_s, motor, start, stop)
    yield from rocking_ct(dets, exposure_s, motor, start, stop, md=md)

scan_time= total exposure time (sec)
    
xrun(0,jog([pe1c],scan_time, ystage, ymin, ymax), more_info = measurement_data())

one_rack_jog(smpl_list_PDF_1, pos_list_x1, posy1 , 10, posy1, posy1+3, num_imgs=num_PDF, det_exp=det_exp_PDF)

'''

'''
#emptykapton tape PDF
glbl['frame_acq_time']=2 #2   $$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
move_PDF()
RE(mv(OT_stage_2_X, -191.3))
RE(mv(OT_stage_2_Y, 66))

for x in range(3):   #3
	xrun(36, 5, more_info = measurement_data())   #5
     
glbl['frame_acq_time']=0.1
time.sleep(60) ### 60
'''

#toprack1
#PDF measurement
#high Intensity sample

#glbl['frame_acq_time'] = 0.1   #0.1

# smpl_list_PDF_1 = [3,4,5,6,7,8,9,10,11]
# pos_list_x1 = [-132.17,-143.37,-154.79,-164.37,-174.76,-187.21,-199.88,-211.31,-218.97]
# pos_list_y1 = [-26.5,-26.5,-26.5,-26.5,-26.5,-26.5,-26.5,-28.5,-26.5]
# smpl_list_PDF_2=[12,13,14,15,16,17]
# pos_list_x2=[-134.3,-143.3,-154.3,-174.3,-194.3,-214.3]
# pos_list_y2 = [4,2.5,2.5,2.5,1.5,1.5]
# smpl_list_PDF_3=[18,19,20,21,22,23,24,25,26,27,28]
# pos_list_x3=[-132.3,-141.3,-149.3,-157.3,-167.3,-175.3,-183.3,-192.3,-201.3,-210.3,-220.3]
# pos_list_y3 = [36,35,35,36,36,36,36,36,36,36,35]
# smpl_list_PDF_4=[29,30,31,32,33,34,35]
# pos_list_x4=[-133.3,-141.3,-149.3,-158.3,-167.3,-177.3,-185.3]
# pos_list_y4 = [65,66,66,66,66,66,66]
# smpl_list_XRD_1=[38,39,40,41,42,43,44,45,46]
# smpl_list_XRD_2=[47,48,49,50,51,52]
# smpl_list_XRD_3=[53,54,55,56,57,58,59,60,61,62,63]
smpl_list_XRD_4=[65,65,65,65,65,65,65,65,65,
                 66,66,66,66,66,66,66,66,66,
                 67,67,67,67,67,67,67,67,67,
                 68,68,68,68,68,68,68,68,68,
                 69,69,69,69,69,69,69,69,69,
                 70,70,70,70,70,70,70,70,70]
pos_list_x4=[-141.1,-141.3,-141.5,-141.1,-141.3,-141.5,-141.1,-141.3,-141.5,
             -149.1,-149.3,-149.5,-149.1,-149.3,-149.5,-149.1,-149.3,-149.5,
             -158.1,-158.3,-158.5,-158.1,-158.3,-158.5,-158.1,-158.3,-158.5,
             -167.1,-167.3,-167.5,-167.1,-167.3,-167.5,-167.1,-167.3,-167.5,
             -177.1,-177.3,-177.5,-177.1,-177.3,-177.5,-177.1,-177.3,-177.5,
             -185.1,-185.3,-185.5,-185.1,-185.3,-185.5,-185.1,-185.3,-185.5]
pos_list_y4 = [65.8,65.8,65.8,66,66,66,66.2,66.2,66.2,
               65.8,65.8,65.8,66,66,66,66.2,66.2,66.2,
               65.8,65.8,65.8,66,66,66,66.2,66.2,66.2,
               65.8,65.8,65.8,66,66,66,66.2,66.2,66.2,
               65.8,65.8,65.8,66,66,66,66.2,66.2,66.2,
               65.8,65.8,65.8,66,66,66,66.2,66.2,66.2]

#print(len(smpl_list_PDF_1),len(smpl_list_XRD_1),len(pos_list_x1),len(pos_list_y1))
#print(len(smpl_list_PDF_2),len(smpl_list_XRD_2),len(pos_list_x2),len(pos_list_y2))
#print(len(smpl_list_PDF_3),len(smpl_list_XRD_3),len(pos_list_x3),len(pos_list_y3))
#print(len(smpl_list_PDF_4),len(smpl_list_XRD_4),len(pos_list_x4),len(pos_list_y4))
print(len(smpl_list_XRD_4),len(pos_list_x4),len(pos_list_y4))


total_exp_time_rack1 = 30   #30    total exposure time
num_PDF_rack1 = 1        #1  number of images   
det_exp_PDF_rack1 = 0.1      #0.1  detector exposure time
sleeptime_btw_smpl_rack1 = 10   #60

jog_dist = 0

total_exp_time=total_exp_time_rack1
num_imgs=num_PDF_rack1
det_exp_for_sleep=det_exp_PDF_rack1
sleeptime_btw_smpl=sleeptime_btw_smpl_rack1
sleeptime_btw_smpl, det_exp_for_sleep


#rack1
#one_rack_jog_rel(smpl_list_PDF_1, pos_list_x1, pos_list_y1 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack2
#one_rack_jog_rel(smpl_list_PDF_2, pos_list_x2, pos_list_y2 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack3
#one_rack_jog_rel(smpl_list_PDF_3, pos_list_x3, pos_list_y3 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack4
#one_rack_jog_rel(smpl_list_PDF_4, pos_list_x4, pos_list_y4 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)


# glbl['frame_acq_time']=0.1
# time.sleep(60) ### 60


# move_XRD()
# total_exp_time_rack1 = 60 #60   redefine exp time to 60 for xrd

# #emptykapton tape XRD
# glbl['frame_acq_time']=2 #2$$$$$$  #PDF det exposure time #B_set $$$$$$$$$$$$$$$$
# RE(mv(OT_stage_2_X, -191.3))
# RE(mv(OT_stage_2_Y, 66))

# for x in range(3):   #3
# 	xrun(71, 5, more_info = measurement_data())   #5
     
# glbl['frame_acq_time']=0.5
# time.sleep(60) ### 60

glbl['frame_acq_time']=0.5

#rack1
#one_rack_jog_rel(smpl_list_XRD_1, pos_list_x1, pos_list_y1 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack2
#one_rack_jog_rel(smpl_list_XRD_2, pos_list_x2, pos_list_y2 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack3
#one_rack_jog_rel(smpl_list_XRD_3, pos_list_x3, pos_list_y3 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)

#rack4
one_rack_jog_rel(smpl_list_XRD_4, pos_list_x4, pos_list_y4 , total_exp_time, jog_dist, num_imgs, sleeptime_btw_smpl, det_exp_for_sleep)



#Toprack1:
#emptykaptpn=-131.72 @Y 60.0
#1st:emptykapton
#2nd: LaB6, X: -134.69
#3nd: Ni

# [-131.71, -134.69, -137.7 , -140.71, -143.73, -146.72, -149.74,
#        -152.77, -155.76, -158.75, -161.78, -164.76, -167.75, -170.78,
#        -173.78, -176.78, -179.8 , -182.82, -185.78, -188.8 , -191.82,
#        -194.81, -197.85, -200.83, -203.85, -206.83, -209.83, -212.82,
#        -215.84, -218.85, -221.81])



glbl['frame_acq_time']=0.1


