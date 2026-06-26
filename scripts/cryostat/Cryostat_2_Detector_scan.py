# Cryostat T-dependent XRD and PDF measurements
# Date Created: 02/09/2024(MA) 
# Last modified: 05/29/2026(KB)
import time
import numpy as np
import shutil
import matplotlib.pyplot as plt 
import os
import epics
N = np.nan
DEBUG = True

#------------------------------------------------- Definition of variables -----------------------------------------------
''' Change below variables as necessay  🤔🤔🤔 '''
A = [300]
B = list(range(5, 305, 10))
C = list(range(145, 0, -5 ))
D = list(range(10, 300, 5))
# B = [300]#np.arange(25, 305, 10)  #Uper limit excluded
#Tlist_2 = Tlist_1[::-1]
Tlist =  A 

"""Temp control settings"""
st = 0              # sleep time for Temperature stabiliy
st2 = 5             # sleep time before each measuement. this time will also be used to stabilize detector after changing frame acquisition time
Q_INTERVAL = 1  # Query interval for PID and temp setting
GIVE_UP = 10*60/Q_INTERVAL   # After this many seconds proceed with data collectoin even if perfect temp has not been acheived
MIN_FLAT_CNTS = 3 *60/Q_INTERVAL    # Min number of seconds a curve needs to be flat to move on

#S_X = [-681.84, -679.84, -673.74]
#      Cs2CdI2Cl2, Cs2SnI2Cl2, Ni
SMPI_PDF = [9,8,7,6,5,4,3,2,1]     # bt.list() Sample indices for PDF
SMPI_XRD = [29,28,27,26,25,24,23,22,21]     # bt.list() Sample indices for XRD
SPI_PDF = [6,12,11,14,6,6,6,6,7]        # bt.list() Scan plan indices for PDF
SPI_XRD = 9*[4]        # bt.list() Scan plan indices for XRD
FMT = 9*[0.1]  # Frame acquisition times for the samples. Set this value based on PDF requirement
OPTION = 9*[1]         # Measurement option for each sample 0: PDF & XRD, 1: PDF only, 2:XRD Only 
repeat = 4 ## XRD measurement repeats for 20 minuts at every temperature

my_config = {'auto_mask': False, 'qmaxinst':20, 'qmax':20, 'rpoly':0.95,
    'user_mask': '/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/Mask.npy',    
    'method': 'splitpixel'}

temp_controller = lakeshore336_2
#------------------------------------------= ''' Do not change anything  below !!!'''---------------------.move----------------
config_dir = "/nsls2/data3/pdf/pdfhack/legacy/processed/xpdacq_data/user_data/config_base/" 
Time, T1, T2, Temperature, DetZ, SampleX, DI1, DI2, TCF, M_current = [],[],[],[],[],[],[],[],[],[] #TCF before measurement
#Tseries = lst(bt.samples.keys())[smpi] 

sample_temp = epics.PV("XF:28ID1-ES{LS336:1-Chan:C}T-I")
lakeshore_out = epics.PV("XF:28ID1-ES{LS336:1-Out:1}T-SP")
range_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Val:Range-Sel")
ramp_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Val:Ramp-SP")
p_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:P-SP")
i_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:I-SP")
d_gain_pv = epics.PV("XF:28ID1-ES{LS336:1-Out:1}Gain:D-SP")

def debug(statement):
    if DEBUG:
        print(statement)

def sanity_check(t_list: list)->bool:
    """Return True if temperature list is insane"""
    return any(x > 500 for x in t_list)

def Figure(name: str) -> plt.figure:
    fig = plt.figure(name)
    ax = fig.gca()
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Temperature (K)")
    return fig

def set_PDF(): # Move PDF poni and mask files to config directory
    xpd_configuration['area_det']=pilatus1
    try:
        os.remove(os.path.join(config_dir, "xpdAcq_calib_info.poni"))
    except Exception:
        pass      
    shutil.copy(config_dir + "pilatus_PDF/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "pilatus_PDF/" + "Mask.npy" , config_dir)

def set_XRD(): # Move XRD poni and mask files to config directory
    xpd_configuration['area_det']=pe1c
    #Grid_X.move(0)
    Grid_Y.move(120)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "pe1c_XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Exception:
        pass
    shutil.copy(config_dir + "pe1c_XRD/" + "Mask.npy" , config_dir)

def set_ramp(ramp_rate:float) -> float:
    ramp_pv.put(ramp_rate)
    return ramp_rate # Degrees K per second

def setPIDs(target_temp:float, t_diff:float, cooling:bool):
    """
    Set PID parameters of device

    Args:
        target_temp (float): Temp to be sent to lakshore 
        direction (bool):  If true unit is cooling

    Returns:
        min_complete_seconds (float): an estimate of min delta T in Kelvin/second
    """

    # Anything over 300K needs to be in 5K steps
    
    t_change_rate = set_ramp(6)

    if not cooling:
        
        """With the lower ramp rate we should be able to increase PI of >270 maybe 35 & 8"""
        if target_temp >= 400:
            if t_diff > 5:
                # t_change_rate = set_ramp(2)
                pass
            elif t_diff <= 5:
                pass
                # t_change_rate = set_ramp(4)
            p_gain_pv.put(35)
            i_gain_pv.put(8)
            d_gain_pv.put(2)

        elif target_temp >= 300:
            if t_diff > 5:
                pass
                # t_change_rate = set_ramp(2)
            elif t_diff <= 5:
                pass
                # t_change_rate = set_ramp(6)

        elif target_temp >= 270:
            # range_pv.put(3)
            # lowest_ramp_rate = .015 # K/s
            # t_change_rate = set_ramp(6)
            p_gain_pv.put(26)
            i_gain_pv.put(5)
            d_gain_pv.put(3)

        elif target_temp >= 140:
            # range_pv.put(3)
            # lowest_ramp_rate = .02 # K/s
            # t_change_rate = set_ramp(8)
            p_gain_pv.put(25)
            i_gain_pv.put(6)
            d_gain_pv.put(3)

        elif target_temp < 140:
            # range_pv.put(2)
            # lowest_ramp_rate = .04 # K/s
            # t_change_rate = set_ramp(8)
            p_gain_pv.put(50)
            i_gain_pv.put(10)
            d_gain_pv.put(1)

    
    elif cooling:
        # t_change_rate = set_ramp(8)

        if target_temp < 140:
            # range_pv.put(2)
            # lowest_ramp_rate = .04 # K/s
            p_gain_pv.put(25)
            i_gain_pv.put(4)
            d_gain_pv.put(3)

        elif target_temp > 200:
            # range_pv.put(3)
            # lowest_ramp_rate = .015 # K/s
            p_gain_pv.put(35)
            i_gain_pv.put(8)
            d_gain_pv.put(3)

        elif target_temp > 140:
            # range_pv.put(3)
            # lowest_ramp_rate = .02 # K/s
            p_gain_pv.put(25)
            i_gain_pv.put(6)
            d_gain_pv.put(3)

    return (abs(t_diff) / t_change_rate) * 60

def detect_target_reached(targ,actual):
    if targ + .5 > actual and targ -.5 < actual:
        debug("Target Reached")
        return 1
    else:
        return 0

def detect_flat(data):
    d_len = len(data)

    if d_len < MIN_FLAT_CNTS:
        return 0
    
    if max(data) - min(data) < 2:
        # debug("Its flat")
        return 1
    return 0

def change_T(target_temp:float): # Cryostat chanel A setpoint loop
    
    last_x_mins = []
    attempts = 0
    flat_curve = False
    temp_reached = False

    curr_temp = float(sample_temp.get())
    lakeshore_out.put(target_temp)

    # Determin temp diff and direction 
    t_diff = curr_temp - target_temp
    if t_diff > 1:
        cooling = True
    else:
        cooling = False

    minseconds = setPIDs(target_temp,t_diff,cooling)

    debug(f"Attempting to reach {target_temp}K giving up after {GIVE_UP + (minseconds/Q_INTERVAL)} seconds")

    while not flat_curve or not temp_reached: # At somepoint we must move on

        curr_temp = float(sample_temp.get())
        
        last_x_mins.append(curr_temp)
        if len(last_x_mins) > MIN_FLAT_CNTS:
            last_x_mins.pop(0)

        # Temp needs to be reached but flat may not happen at target temp
        # Once temp is reached latch
        if not temp_reached:
            temp_reached = detect_target_reached(target_temp,curr_temp)

        flat_curve = detect_flat(last_x_mins)
        
        # Check the range setting if things are taking too long
        if attempts > (3 * 60 / Q_INTERVAL) and not temp_reached:

            curr_range = int(range_pv.get())
            if curr_range < 3 and not cooling:
                debug(f"Raising range\n")
                range_pv.put(curr_range + 1)

            # if curr_range > 1 and cooling:
            #     debug(f"Lowering range\n")
            #     range_pv.put(curr_range - 1)

        # Give up if taking too long
        if attempts > GIVE_UP + (minseconds*60/Q_INTERVAL):
            break

        time.sleep(Q_INTERVAL)
        attempts += 1

# def change_T(t): # Cryostat chanel A setpoint loop
#     caput('XF:28ID1-ES{LS336:1-Out:1}T-SP',t)
#     while True:
#         tt =  temp_controller.read()['lakeshore336_temp_A_T']['value']
#         if t-1 <= tt <= t+1: # changed from +/- 0.3
#             break
#         else:
#             print(tt)
#         time.sleep(5)


def measurement_data(): # .......Captures metadata   
    info_dict = {}
    info_dict['OT_stage_1_X'] = OT_stage_1_X.read()
    info_dict['OT_stage_1_Y'] = OT_stage_1_Y.read()
    info_dict['Det_1_X'] = Det_1_X.read()
    info_dict['Det_1_Y'] = Det_1_Y.read()
    info_dict['Det_1_Z'] = Det_1_Z.read()
    info_dict['Grid_X'] = Grid_X.read()
    info_dict['Grid_Y'] = Grid_Y.read()
    info_dict['Grid_Z'] = Grid_Z.read()
    info_dict['ring_current'] = ring_current.read()
    info_dict['frame_acq_time'] = glbl['frame_acq_time']
    info_dict['dk_window'] = glbl['dk_window']
    info_dict['cryostat_A'] = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    info_dict['cryostat_A_V'] = caget('XF:28ID1-ES{LS336:1-Chan:A}Val:Sens-I')

    info_dict['cryostat_A_P'] = p_gain_pv.get()
    info_dict['cryostat_A_I'] = i_gain_pv.get()
    info_dict['cryostat_A_D'] = d_gain_pv.get()

    info_dict['cryostat_B'] = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    info_dict['cryostat_B_V'] = caget('XF:28ID1-ES{LS336:1-Chan:B}Val:Sens-I')
    info_dict['cryostat_C'] = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    info_dict['cryostat_C_V'] = caget('XF:28ID1-ES{LS336:1-Chan:C}Val:Sens-I')
    info_dict['cryostat_D'] = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    info_dict['cryostat_D_V'] = caget('XF:28ID1-ES{LS336:1-Chan:D}Val:Sens-I')
    info_dict['Measurement_time'] = time.time()
    return info_dict

def Det_scan(SI, SP, repeat): # Pilatus three position scan
    for j in range(repeat):
        # det_x = [40.644, 31.356, 36]
        # det_y = [-3.356, -12.644, -8]
        # for i in range(len(det_x)):
        #     Grid_X.move(det_x[i])
        #     Grid_Y.move(det_y[i])
        #     #xrun(SI, jog([pilatus1], SP, OT_stage_2_Y, use_ypos-.5, use_ypos+.5), dark_strategy=no_dark,  more_info = useful_info())
        xrun(SI, SP, dark_strategy= no_dark, more_info = measurement_data(), user_config = my_config)


def measurement_PDF(figure: plt.figure): # PDF measurement 
    time_ = time.time()
    Time.append(time_)
    temperature = lakeshore336.read()['lakeshore336_temp_A_T']['value']
    temperature1 = lakeshore336.read()['lakeshore336_temp_B_T']['value']
    temperature2 = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    temperature3 = lakeshore336.read()['lakeshore336_temp_D_T']['value']
    Det_scan(smpi,spi,repeat)  # Disable this in enable the previous line when 3 positions are not necessary
    ax = figure.gca()
    ax.plot((time_-Time[0])/3600,temperature, 'ro', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature1, 'go', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature2, 'bo', markersize=.8)
    ax.plot((time_-Time[0])/3600,temperature3, 'ko', markersize=.8)
    plt.ion()   
    plt.pause(0.05)

def measurement_XRD(): # XRD measurement
    time_ = time.time()
    Time.append(time_)
    temperature = lakeshore336.read()['lakeshore336_temp_C_T']['value']
    xrun(smpi, spi, more_info = measurement_data(), user_config = my_config) 


def shifter_T(motor: ophyd.device, temperature: float) -> list:
    #pos_list, I_list, peak_cen_list = scan_shifter_pos_ask(motor, -672.5, -691.5, 120, min_height=0.1, peak_rad=1.0)
    pos_list, I_list, peak_cen_list = scan_shifter_pos_ask(motor, -691, -672, 150, min_height=0.11, peak_rad=1.0)
    
    fn_scan = f'{motor.name}_{temperature}K_scan'
    fn_fitting = f'{motor.name}_{temperature}K_fitting'
    
    print('\noutput fitted peak position as csv file\n')
    fitting_pos_csv(peak_cen_list, save=True, fn_prefix=fn_fitting)
    
    print('\noutput scanned position, intensity profile as csv file\n')
    scan_pos_csv(pos_list, I_list, save=True, fn_prefix=fn_scan)

    return(peak_cen_list)


change_T(300)
# ------------------------------------------- ''' Main T dependent Measurement loop '''' -----------------------------------------
# for i in range(len(Tlist)):
#     #change_T(Tlist[i])
#     channel_range = 3
#     temp_controller.tolerance = 0.5
#     temp_controller.set_and_check(Tlist[i], channel_range, input_channel='temp.A', output_channel='out1')
#     S_X = shifter_T(OT_stage_1_X, Tlist[i])
#     # time.sleep(st)
#     tqdm_sleep(st, message='Waif for thermal equilibrium')

#     temp_fig = Figure(temp_controller.name)
#     if i == 0:
#         # Figure()
#         Time = []
    
#     set_PDF()    
#     for jj in range (len(S_X)):
#         #glbl['frame_acq_time']= FMT[jj]
#         time.sleep(st2)
#         OT_stage_1_X.move(S_X[jj])
#         spi_PDF = SPI_PDF[jj]
#         spi_XRD = SPI_XRD[jj]
#         smpi_PDF = SMPI_PDF[jj]
#         smpi_XRD = SMPI_XRD[jj]
#         option_1 = OPTION[jj]

#         if option_1 == 0:   # PDF+XRD       
#             spi = spi_PDF
#             smpi = smpi_PDF
#             measurement_PDF(temp_fig)
#         elif option_1 == 1:
#             spi = spi_PDF
#             smpi = smpi_PDF
#             measurement_PDF(temp_fig)
#         else:
#             pass

#     set_XRD()    
#     for kk in range (len(S_X)):
#         #glbl['frame_acq_time']= FMT[kk]
#         time.sleep(st2)
#         OT_stage_1_X.move(S_X[kk])
#         spi_PDF = SPI_PDF[kk]
#         spi_XRD = SPI_XRD[kk]
#         smpi_PDF = SMPI_PDF[kk]
#         smpi_XRD = SMPI_XRD[kk]
#         option_1 = OPTION[kk]

#         if option_1 == 0:   # PDF+XRD       
#             spi = spi_XRD
#             smpi = smpi_XRD
#             measurement_XRD()
#         elif option_1 == 2:
#             spi = spi_XRD
#             smpi = smpi_XRD
#             measurement_XRD()
#         else:
#             pass
            
'''
# -------Below part of the script insert metada in the headers of IQ, Itth, and Gr files in a way that pdfgui and GSAS-II can recognize and import-------
# meta_data function should be pre-defined by running "metadata_insert.py"
time.sleep(30)
for kk in range(len(SMPI_PDF)):
    try:
        meta_data(SMPI_PDF[kk])
        print(SMPI_PDF[kk])
    except Exception:
        pass
    
for ll in range(len(SMPI_XRD)):
    try:
        meta_data(SMPI_XRD[ll])
        print(SMPI_XRD[ll])
    except Exception:
        pass
        
'''