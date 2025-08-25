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

def move_XRD():
    Det_1_Z.move(D2)
    try:
        os.remove(config_dir + "xpdAcq_calib_info.poni")
    except Exception:
        pass     
    shutil.copy(config_dir + "/XRD/" + "xpdAcq_calib_info.poni" , config_dir)
    try:
        os.remove(config_dir + "Mask.npy")
    except Excemption:
        pass
    shutil.copy(config_dir + "/XRD/" + "Mask.npy" , config_dir)


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


for j in range(repeat):
    print(j)
    for i in range(len(SP)):
        print(j)
        SP[i]()
        time.sleep(st)
        xrun(SI[i], scan_plan, more_info = measurement_data())
