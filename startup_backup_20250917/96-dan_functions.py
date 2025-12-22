import sys
#from slack import WebClient
#from slack.errors import SlackApiError
import os
import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
from bluesky.callbacks import LiveTable
import uuid
import numpy as np
import matplotlib.pyplot as plt

plt.ion()


##############
#slack_token = os.environ["SLACK_API_TOKEN"]
#client = WebClient(token=slack_token)


###


#def slack_message(my_message):
#    try:
#        response = client.chat_postMessage(
#            channel="pdf_dev",
#            # channel = user_name,
#            text=my_message,
#        )
#    # except SlackApiError as e:
#    #    assert e.response["something went wrong"]
#    except:
#        print("slack message failed")


#def check_heartbeat(
#    fname="hbeat.txt", tlapse=300, send_warning=False, notify_user=False
#):
#    fin = open(fname, "r")
#    tread = float(fin.read())
#    tpassed = time.time() - tread
#    if tpassed > tlapse:
#        tpassed_str = str(tpassed / 60)[:3]
#        if send_warning:
#            msg_to_send = "Issue detected, no pulse in " + tpassed_str + " mins"
#            if notify_user:
#                msg_to_send = "<@" + str(user_ID) + "> " + msg_to_send
#            slack_message(msg_to_send)
#        return False
#    return True


#def update_heartbeat(fname="hbeat.txt"):
#    fout = open(fname, "w")
#    fout.write(str(time.time()))
#    fout.close()


###


def show_me(my_im, per_low=1, per_high=99, use_colorbar=False, use_true_bounds=False, true_low=0, true_high=1000):
    my_low = np.percentile(my_im, per_low)
    my_high = np.percentile(my_im, per_high)
    if use_true_bounds:
        plt.imshow(my_im, vmin=true_low, vmax=true_high)
    else:
        plt.imshow(my_im, vmin=my_low, vmax=my_high)
    if use_colorbar:
        plt.colorbar()

def show_me_db_streams(
    my_id,
    per_low=1,
    per_high=99,
    true_low = 0,
    true_high = 1000,
    use_colorbar=False,
    use_true_bounds = False,
    dark_subtract=True,
    return_im=False,
    return_dark=False,
    suffix="_image",
):
    my_det_probably = db[my_id].start["detectors"][0] + suffix
    if "primary" in db[my_id].stream_names:
        my_im = np.array(list(db[my_id].data(my_det_probably, stream_name="primary")))[0][0]
    else:
        print ("Primary stream missing, wtf.")
    
    my_im = (db[my_id].table(fill=True)[my_det_probably][1][0]).astype(float)

    if len(my_im) == 0:
        print("issue... passing")
        pass

    if dark_subtract:
        if "dark" in db[my_id].stream_names:
            dark_im = np.array(list(db[my_id].data(my_det_probably, stream_name="dark")))[0][0]
            my_im = my_im - dark_im
        else:
            print("this run has no associated dark")
    if return_im:
        return my_im
    if return_dark:
        return dark_im

    show_me(my_im, per_low=per_low, per_high=per_high, use_colorbar=use_colorbar,
            true_low = true_low, true_high=true_high,use_true_bounds=use_true_bounds)


def show_me_db(
    my_id,
    per_low=1,
    per_high=99,
    use_colorbar=False,
    dark_subtract=True,
    return_im=False,
    return_dark=False,
    new_db=True,
    suffix="_image",
):
    my_det_probably = db[my_id].start["detectors"][0] + suffix
    if new_db:
        my_im = (db[my_id].table(fill=True)[my_det_probably][1][0]).astype(float)
    else:
        my_im = (db[my_id].table(fill=True)[my_det_probably][1]).astype(float)

    if len(my_im) == 0:
        print("issue... passing")
        pass
    if dark_subtract:
        if "sc_dk_field_uid" in db[my_id].start.keys():
            my_dark_id = db[my_id].start["sc_dk_field_uid"]
            if new_db:
                dark_im = (db[my_dark_id].table(fill=True)[my_det_probably][1][0]).astype(float)
            else:
                dark_im = (db[my_dark_id].table(fill=True)[my_det_probably][1]).astype(float)
    
            my_im = my_im - dark_im
        else:
            print("this run has no associated dark")
    if return_im:
        return my_im
    if return_dark:
        return dark_im

    show_me(my_im, per_low=per_low, per_high=per_high, use_colorbar=use_colorbar)


def make_me_a_name(my_id):
    if "sample_name" in db[my_id].start.keys():
        sample_name = db[my_id].start["sample_name"]
    elif "sp_plan_name" in db[my_id].start.keys():
        sample_name = db[my_id].start["sp_plan_name"]
    else:
        sample_name = "NoName"
    tot_time = str(
        round(
            db[my_id].start["sp_time_per_frame"] * db[my_id].start["sp_num_frames"], 2
        )
    )
    if len(tot_time) < 4:
        tot_time = "0" + tot_time
    # print ('sample name : '+sample_name)
    # print ('tot time : '+tot_time)
    my_name = sample_name + "T" + tot_time

    return my_name


def make_me_a_name2(my_id):
    # if 'sample_name' in db[my_id].start.keys():
    #    sample_name = db[my_id].start['sample_name']
    # elif 'sp_plan_name' in db[my_id].start.keys():
    #    sample_name = db[my_id].start['sp_plan_name']
    # else:
    #    sample_name = 'NoName'
    # tot_time = str(round(db[my_id].start['sp_time_per_frame'] * db[my_id].start['sp_num_frames'],2))

    this_delay = str(db[my_id].start["dans_md"]["delay"])
    sample_name = str(db[my_id].start["dans_md"]["sample"])
    tot_time = str(round(db[my_id].start["dans_md"]["exposure"] * 1.000, 2))

    if len(tot_time) < 4:
        tot_time = "0" + tot_time

    gridx = str(round(db[my_id].table(stream_name="baseline").loc[1, "Grid_X"], 2))
    gridy = str(round(db[my_id].table(stream_name="baseline").loc[1, "Grid_Y"], 2))
    gridz = str(round(db[my_id].table(stream_name="baseline").loc[1, "Grid_Z"], 2))

    my_name = "p3k_" + sample_name + "_GZ" + gridz + "_T" + tot_time

    return my_name


def make_colormap(num_colors, cmap="viridis"):
    my_cmap = plt.cm.get_cmap(cmap)
    color_list = my_cmap(np.linspace(0, 1, num_colors))
    return color_list


def plot_xline(my_id, *argv, use_offset=0, use_alpha=1, use_cmap="viridis"):
    my_det_probably = db[my_id].start["detectors"][0] + "_image"
    this_im = db[my_id].table(fill=True)[my_det_probably][1]
    try:
        arg_len = len(*argv)
        plot_mode = "typea"
    except Exception:
        arg_len = len(argv)
        plot_mode = "typeb"

    cc = make_colormap(arg_len, cmap=use_cmap)

    if arg_len > 1:  # two or more arguments passed
        ymin = min(*argv)
        ymax = max(*argv)
        if plot_mode == "typea":
            for i, this_one in enumerate(*argv):
                plt.plot(
                    this_im[this_one, :] + i * use_offset, color=cc[i], alpha=use_alpha
                )
        else:
            for i, this_one in enumerate(argv):
                plt.plot(
                    this_im[this_one, :] + i * use_offset, color=cc[i], alpha=use_alpha
                )
    if arg_len == 1:  # only one argument passed
        my_line = argv[0]
        plt.plot(this_im[my_line, :], "k")


def plot_yline(my_id, *argv, use_offset=0, use_alpha=1, use_cmap="viridis"):
    my_det_probably = db[my_id].start["detectors"][0] + "_image"
    this_im = db[my_id].table(fill=True)[my_det_probably][1]
    try:
        arg_len = len(*argv)
        plot_mode = "typea"
    except Exception:
        arg_len = len(argv)
        plot_mode = "typeb"

    cc = make_colormap(arg_len, cmap=use_cmap)

    if arg_len > 1:  # two or more arguments passed
        ymin = min(*argv)
        ymax = max(*argv)
        if plot_mode == "typea":
            for i, this_one in enumerate(*argv):
                plt.plot(
                    this_im[:, this_one] + i * use_offset, color=cc[i], alpha=use_alpha
                )
        else:
            for i, this_one in enumerate(argv):
                plt.plot(
                    this_im[:, this_one] + i * use_offset, color=cc[i], alpha=use_alpha
                )
    if arg_len == 1:  # only one argument passed
        my_line = argv[0]
        plt.plot(this_im[:, my_line], "k")


def read_twocol_data(
    filename,
    junk=None,
    backjunk=None,
    splitchar=None,
    do_not_float=False,
    shh=True,
    use_idex=[0, 1],
):
    with open(filename, "r") as infile:
        datain = infile.readlines()

    if junk == None:
        for i in range(len(datain)):
            try:
                for j in range(10):
                    x1, y1 = (
                        float(datain[i + j].split(splitchar)[use_idex[0]]),
                        float(datain[i + j].split(splitchar)[use_idex[1]]),
                    )
                junk = i
                break
            except Exception:
                pass  # print ('nope')

    if backjunk is None:
        for i in range(len(datain), -1, -1):
            try:
                x1, y1 = (
                    float(datain[i].split(splitchar)[use_idex[0]]),
                    float(datain[i].split(splitchar)[use_idex[1]]),
                )
                backjunk = len(datain) - i - 1
                break
            except Exception:
                pass
                # print ('nope')

    # print ('found junk '+str(junk))
    # print ('and back junk '+str(backjunk))

    if backjunk == 0:
        datain = datain[junk:]
    else:
        datain = datain[junk:-backjunk]

    xin = np.zeros(len(datain))
    yin = np.zeros(len(datain))

    if do_not_float:
        xin = []
        yin = []

    if not shh:
        print("length " + str(len(xin)))
    if do_not_float:
        if splitchar is None:
            for i in range(len(datain)):
                xin.append(datain[i].split()[use_idex[0]])
                yin.append(datain[i].split()[use_idex[1]])
        else:
            for i in range(len(datain)):
                xin.append(datain[i].split(splitchar)[use_idex[0]])
                yin.append(datain[i].split(splitchar)[use_idex[1]])
    else:
        if splitchar is None:
            for i in range(len(datain)):
                xin[i] = float(datain[i].split()[use_idex[0]])
                yin[i] = float(datain[i].split()[use_idex[1]])
        else:
            for i in range(len(datain)):
                xin[i] = float(datain[i].split(splitchar)[use_idex[0]])
                yin[i] = float(datain[i].split(splitchar)[use_idex[1]])

    return xin, yin


# setup pandas dataframe
def make_me_a_dataframe(found_pos,cut_start = None, cut_end = None):
    import glob as glob
    import pandas as pd

    my_excel_file = glob.glob("Import/*_sample.xlsx")
    if len(my_excel_file) >= 1:
        my_excel_file = my_excel_file[0]
    else:
        print("I couldn't find your sample info excel sheet")
        return None

    read_xcel = pd.read_excel(my_excel_file, skiprows=1, usecols=([0, 1]))
    if cut_start != None:
        print ('cutting down')
        read_xcel = read_xcel.loc[cut_start:cut_end,:]
        read_xcel.index = range(len(read_xcel.index))

    print ('expecting length '+str(len(np.array(read_xcel.index))))

    df_sample_pos_info = pd.DataFrame(index=np.array(read_xcel.index))
    df_sample_pos_info["name"] = read_xcel.iloc[:, 0]
    df_sample_pos_info["pos"] = np.hstack((found_pos[0], found_pos))
    df_sample_pos_info["xpdacq_name_num"] = np.array(read_xcel.index)
    df_sample_pos_info["formula"] = read_xcel.iloc[:, 1]
    df_sample_pos_info["xpdacq_scanplan_num"] = 5 * np.ones(
        len(read_xcel.index), dtype=int
    )


    return df_sample_pos_info


def measure_me_this(df_sample_info, sample_num, measure_time=None):
    print("Preparing to measure " + str(df_sample_info.loc[sample_num, "sample_names"]))
    print("Moving to position " + str(df_sample_info.loc[sample_num, "position"]))
    # move logic goes here
    if measure_time is None:
        print("Measuring for " + str(df_sample_info.loc[sample_num, "measure_time"]))
        # perform xrun here (or Re(Count))
    else:
        print("Override measuring for " + str(measure_time))
        # perform custom measure here
    return None


def scan_shifter_pos(
    motor,
    xmin,
    xmax,
    numx,
    num_samples=0,
    min_height=0.02,
    min_dist=5,
    peak_rad=1.5,
    use_det=True,
    abs_data = False,
    oset_data = 0.0,
    return_to_start = True,
    recover_last_scan = False
):
    def yn_question(q):
        return input(q).lower().strip()[0] == "y"

    init_pos = motor.position

    print("")
    if not recover_last_scan:
        print("I'm going to move the motor: " + str(motor.name))
        print("It's currently at position: " + str(motor.position))
        move_coord = float(xmin) - float(motor.position)
        if move_coord < 0:
            print(
                "So I will start by moving "
                + str(abs(move_coord))[:4]
                + " mm inboard from current location"
            )
        elif move_coord > 0:
            print(
                "So I will start by moving "
                + str(abs(move_coord))[:4]
                + " mm outboard from current location"
            )
        elif move_coord == 0:
            print("I'm starting where I am right now :)")
        else:
            print("I confused")
    
        if not yn_question("Confirm scan? [y/n] "):
            print("Aborting operation")
            return None
    
        pos_list, I_list = _motor_move_scan_shifter_pos(
            motor=motor, xmin=xmin, xmax=xmax, numx=numx)
    else:
        print ('recovering last scan from redis...')
        return_to_start = False
        pos_list, I_list = retrieve_recent_shifter_scan()
        plt.figure()
        plt.plot(pos_list, I_list)

    if len(pos_list) > 1:
        delx = pos_list[1] - pos_list[0]
    else:
        print("only a single point? I'm gonna quit!")
        return None

    if return_to_start:
        print ('returning to start position....')
        motor.move(init_pos)


    if oset_data != 0.0:
        I_list = I_list - oset_data

    if abs_data:
        I_list = abs(I_list)

    print("")
    if not yn_question(
        "Move on to fitting? (if not, I'll return [pos_list, I_list]) [y/n] "
    ):
        return pos_list, I_list
    plt.close()

    go_on = False
    tmin_height = min_height
    tmin_dist = min_dist
    tpeak_rad = peak_rad
    fit_attempts = 1

    while not go_on:
        print("\nI'm going to fit peaks with a min_height of " + str(tmin_height))
        print(
            "and min_dist [index values/real vals] of "
            + str(tmin_dist)
            + " / "
            + str(tmin_dist * delx)
        )
        print("and I'll fit a radius between each peak-center of " + str(tpeak_rad))
        if fit_attempts == 0:
            go_on, peak_cen_list = _identify_peaks_scan_shifter_pos(
                pos_list,
                I_list,
                num_samples=num_samples,
                min_height=tmin_height,
                min_dist=tmin_dist,
                peak_rad=tpeak_rad,
            )
        else:
            go_on, peak_cen_list = _identify_peaks_scan_shifter_pos(
                pos_list,
                I_list,
                num_samples=num_samples,
                min_height=tmin_height,
                min_dist=tmin_dist,
                peak_rad=tpeak_rad,
                open_new_plot=False,
            )
        fit_attempts += 1
        # if yn_question("\nHappy with the fit? [y/n] ") == False:
        if not go_on:
            qans = input(
                "\n1. Change min_height\n2. Change min_dist\n3. Change peak-fit rad\n0. Give up\n : "
            )
            try:
                qans = int(qans)
                if int(qans) == 1:
                    tmin_height = float(input("\nWhat is the new min_height value? "))
                if int(qans) == 2:
                    tmin_dist = float(input("\nWhat is the new min_dist value? "))
                if int(qans) == 3:
                    tpeak_rad = float(input("\nWhat is the new peak_rad value? "))
                if int(qans) == 0:
                    print("ok, giving up")
                    return None
            except Exception:
                print("what, what, whaaat?")
        else:
            print("Ok, great.")
            go_on = True

    return peak_cen_list


def _identify_peaks_scan_shifter_pos(
    x, y, num_samples=0, min_height=0.02, min_dist=5, peak_rad=1.5, open_new_plot=True
):
    from scipy.signal import find_peaks
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import numpy as np
    import pandas as pd

    if open_new_plot:
        print("making new figure")
        plt.figure()
    else:
        print("clearing figure")
        this_fig = plt.gcf()
        this_fig.clf()
        plt.pause(0.01)

    def yn_question(q):
        return input(q).lower().strip()[0] == "y"

    y -= y.min()
    y /= y.max()
    print("ymax is " + str(max(y)))
    print("ymin is " + str(min(y)))

    def cut_data(qt, sqt, qmin, qmax):
        qcut = []
        sqcut = []
        for i in range(len(qt)):
            if qt[i] >= qmin and qt[i] <= qmax:
                qcut.append(qt[i])
                sqcut.append(sqt[i])
        qcut = np.array(qcut)
        sqcut = np.array(sqcut)
        return qcut, sqcut

    # initial guess of position peaks
    print("finding things")
    peaks, _ = find_peaks(y, height=min_height, distance=min_dist)

    if num_samples == 0:
        print("I found " + str(len(peaks)) + " peaks.")
    elif num_samples == len(peaks):
        print("I think I found all " + str(num_samples) + " samples you expected.")
    else:
        print("WARNING: I saw " + str(len(peaks)) + " samples!")
    print("doing a thing")
    this_fig = plt.gcf()
    this_fig.clf()

    plt.plot(x, y)
    plt.plot(x[peaks], y[peaks], "kx")
    plt.show()
    print("done")
    plt.pause(0.01)
    if not yn_question("Go on? [y/n] "):
        return False, []

    # now refine positions
    peak_cen_guess_list = x[peaks]
    peak_amp_guess_list = y[peaks]

    fit_peak_cen_list = np.zeros(len(peaks))
    fit_peak_amp_list = np.zeros(len(peaks))
    fit_peak_bgd_list = np.zeros(len(peaks))
    fit_peak_wid_list = np.zeros(len(peaks))

    def this_func(x, c, w, a, b):

        return a * np.exp(-((x - c) ** 2.0) / (2.0 * (w ** 2))) + b

    this_fig = plt.gcf()
    this_fig.clf()
    for i in range(len(peaks)):
        cut_x, cut_y = cut_data(
            x, y, peak_cen_guess_list[i] - peak_rad, peak_cen_guess_list[i] + peak_rad
        )
        plt.plot(cut_x, cut_y)

        this_guess = [peak_cen_guess_list[i], 1, peak_amp_guess_list[i], 0.0001]
        low_limits = [peak_cen_guess_list[i] - peak_rad, 0.05, 0.0, 0.0]
        high_limits = [peak_cen_guess_list[i] + peak_rad, 3, 1.5, 0.5]

        popt, _ = curve_fit(
            this_func, cut_x, cut_y, p0=this_guess, bounds=(low_limits, high_limits)
        )
        plt.plot(cut_x, this_func(cut_x, *popt), "k--")

        fit_peak_amp_list[i] = popt[2]
        fit_peak_wid_list[i] = popt[1]
        fit_peak_cen_list[i] = popt[0]
        fit_peak_bgd_list[i] = popt[3]

    plt.show()
    plt.pause(0.01)

    # finally, return this as a numpy list
    return True, fit_peak_cen_list[::-1]  # return flipped


def get_total_counts():
    from epics import caget
    return float(caget("XF:28ID1-ES{Det:PE1}Stats2:Total_RBV"))
    #return float(caget("XF:28ID1-ES{Det:PE2}Stats1:Total_RBV")) #for pe2c


def _motor_move_scan_shifter_pos(motor, xmin, xmax, numx, use_pe2c=False):
    from epics import caget
    #ensure shutter is closedi
    print ('closing shutter')
    # RE(mv(fs,"Close"))
    # CHL revised for failed fs on 2025/05/23
    RE(mv(fs, 0))
    I_list = np.zeros(numx)
    dx = (xmax - xmin) / numx
    pos_list = np.linspace(xmin, xmax, numx)
    print ('moving to starting postion')
    RE(mv(motor,pos_list[0]))
    print ('opening shutter')
    # RE(mv(fs, "Open"))
    # CHL revised for failed fs on 2025/05/23
    RE(mv(fs, 1))
    time.sleep(1)
    fig1, ax1 = plt.subplots()
    use_det = True
    temp_pos_list = []
    temp_I_list = []
    for i, pos in enumerate(pos_list):
        print("moving to " + str(pos))
        try:
            motor.move(pos)
        except Exception:
            print("well, something bad happened")
            return None

        if use_det == True:
            my_int = float(caget("XF:28ID1-ES{Det:PE1}Stats2:Total_RBV"))
            if use_pe2c:
                my_int = float(caget("XF:28ID1-ES{Det:PE2}Stats5:Total_RBV"))  
                time.sleep(.5)
        else:
            my_int = float(caget("XF:28ID1B-OP{Det:1-Det:2}Amp:bkgnd"))

        temp_I_list.append(my_int)
        temp_pos_list.append(pos)
        stow_recent_shifter_scan(temp_pos_list, temp_I_list)

        I_list[i] = my_int
        ax1.scatter(pos, my_int, color="k")
        plt.pause(0.01)

    plt.plot(pos_list, I_list)
    # plt.close()
    # RE(mv(fs, "Close"))
    # CHL revised for failed fs on 2025/05/23
    RE(mv(fs, 0))
    stow_recent_shifter_scan(pos_list, I_list)
    return pos_list, I_list

def configure_area_det(det, exposure):
    '''Configure an area detector in "continuous mode"'''

    def _check_mini_expo(exposure, acq_time):
        if exposure < acq_time:
            raise ValueError(
                "WARNING: total exposure time: {}s is shorter "
                "than frame acquisition time {}s\n"
                "you have two choices:\n"
                "1) increase your exposure time to be at least"
                "larger than frame acquisition time\n"
                "2) increase the frame rate, if possible\n"
                "    - to increase exposure time, simply resubmit"
                " the ScanPlan with a longer exposure time\n"
                "    - to increase frame-rate/decrease the"
                " frame acquisition time, please use the"
                " following command:\n"
                "    >>> {} \n then rerun your ScanPlan definition"
                " or rerun the xrun.\n"
                "Note: by default, xpdAcq recommends running"
                "the detector at its fastest frame-rate\n"
                "(currently with a frame-acquisition time of"
                "0.1s)\n in which case you cannot set it to a"
                "lower value.".format(
                    exposure,
                    acq_time,
                    ">>> glbl['frame_acq_time'] = 0.5  #set" " to 0.5s",
                )
            )

    # todo make
    ret = yield from bps.read(det.cam.acquire_time)
    if ret is None:
        acq_time = 1
    else:
        acq_time = ret[det.cam.acquire_time.name]["value"]
    _check_mini_expo(exposure, acq_time)
    if hasattr(det, "images_per_set"):
        # compute number of frames
        num_frame = np.ceil(exposure / acq_time)
        yield from bps.mov(det.images_per_set, num_frame)
    else:
        # The dexela detector does not support `images_per_set` so we just
        # use whatever the user asks for as the thing
        # TODO: maybe put in warnings if the exposure is too long?
        num_frame = 1
    computed_exposure = num_frame * acq_time

    # print exposure time
    print(
        "INFO: requested exposure time = {} - > computed exposure time"
        "= {}".format(exposure, computed_exposure)
    )
    return num_frame, acq_time, computed_exposure


def simple_ct(dets, exposure, *, md=None):
    """A minimal wrapper around count that adjusts exposure time."""
    md = md or {}

    # setting up area_detector
    (ad,) = (d for d in dets if hasattr(d, "cam"))
    (num_frame, acq_time, computed_exposure) = yield from configure_area_det(
        ad, exposure
    )

    sp = {
        "time_per_frame": acq_time,
        "num_frames": num_frame,
        "requested_exposure": exposure,
        "computed_exposure": computed_exposure,
        "type": "ct",
        "uid": str(uuid.uuid4()),
        "plan_name": "ct",
    }

    # update md
    _md = {"sp": sp, **{f"sp_{k}": v for k, v in sp.items()}}
    _md.update(md)
    plan = bp.count(dets, md=_md)
    plan = bpp.subs_wrapper(plan, LiveTable([]))
    return (yield from plan)


def save_history(histfile,LIMIT=5000):
    ip = get_ipython()
    """save the IPython history to a plaintext file"""
    #histfile = os.path.join(ip.profile_dir.location, "history.txt")
    print("Saving plaintext history to %s" % histfile)
    lines = []
    # get previous lines
    # this is only necessary because we truncate the history,
    # otherwise we chould just open with mode='a'
    if os.path.exists(histfile):
        with open(histfile, 'r') as f:
            lines = f.readlines()

    # add any new lines from this session
    lines.extend(record[2] + '\n' for record in ip.history_manager.get_range())

    with open(histfile, 'w') as f:
        # limit to LIMIT entries
        f.writelines(lines[-LIMIT:])



def phase_parser(phase_str):
    """parser for field with <chem formula>: <phase_amount>
    Parameters
    ----------
    phase_str : str
        a string contains a series of <chem formula> : <phase_amount>.
        Each phase is separated by a comma.
    Returns
    -------
    composition_dict : dict
        a dictionary contains {element: stoichiometry}.
    phase_dict : dict
        a dictionary contains relative ratio of phases.
    composition_str : str
        a string with the format PDF transfomation software
        takes. default is pdfgetx
    Examples
    --------
    rv = cls.phase_parser('NaCl:1, Si:2')
    rv[0] # {'Na':0.33, 'Cl':0.33, 'Si':0.67}
    rv[1] # {'Nacl':0.33, 'Si':0.67}
    rv[2] # 'Na0.33Cl0.5Si0.5'
    Raises:
    -------
    ValueError
        if ',' is not specified between phases
    """
    phase_dict = {}
    composition_dict = {}
    composition_str = ""
    # figure out ratio between phases
    compound_meta = phase_str.split(",")
    for el in compound_meta:
        _el = el.strip()
        # if no ":" in the string
        if ":" not in _el:
            com = _el
            amount = 1.0
        # ":" in the string
        else:
            meta = _el.split(":")
            # there is a ":" but nothing follows
            if not meta[1]:
                com = meta[0]
                amount = 1.0
            # presumably valid input
            else:
                com, amount = meta
        # further verify if it's giving as 'X: 10%' format
        if isinstance(amount, str):
            amount = amount.strip()
            amount = amount.replace("%", "")
        # construct the not normalized phase dict
        phase_dict.update({com.strip(): float(amount)})

    # normalize phase ratio for composition dict
    total = sum(phase_dict.values())
    for k, v in phase_dict.items():
        ratio = round(v / total, 2)
        phase_dict[k] = ratio

    # construct composition_dict
    for k, v in phase_dict.items():
        # k is compostring, v is phase ratio
        try:
            el_list, sto_list = composition_analysis(k.strip())
        except ValueError:
            # getx3 parser can't parse it, set default
            el_list, sto_list = ([k], [v])
        for el, sto in zip(el_list, sto_list):
            # sum element
            if el in composition_dict:
                val = composition_dict.get(el)
                val += sto * v
                composition_dict.update({el: val})
            else:
                # otherwise, just update it
                composition_dict.update({el: sto * v})

    # finally, construct composition_str
    for k, v in sorted(composition_dict.items()):
        composition_str += str(k) + str(v)

    return composition_dict, phase_dict, composition_str


pe1c.tiff.stage_sigs.pop(pe1c.proc.reset_filter, None)

#for looking at data from Pilatus detector

def set_Pilatus_parameters(num_images=1, exposure_time=0.1):
    print ('setting number of images per collection to '+str(num_images))
    pilatus1.set_num_images(num_images)
    print ('setting exposure time for a single image to '+str(exposure_time))
    pilatus1.set_exposure_time(exposure_time)
    

def show_me2(my_im, count_low=0, count_high=1, use_colorbar=False, use_cmap='viridis'):
    #my_low = np.percentile(my_im, per_low)
    #my_high = np.percentile(my_im, per_high)
    plt.imshow(my_im, vmin=count_low, vmax=count_high, cmap= use_cmap)
    if use_colorbar:
        plt.colorbar()

def show_me_db2(
    my_id,
    count_low=1,
    count_high=99,
    use_colorbar=False,
    dark_subtract=False,
    return_im=False,
    return_dark=False,
    new_db = True,
    use_cmap='viridis',
    suffix="_image",
):
    my_det_probably = db[my_id].start["detectors"][0] + suffix
    if new_db:
        my_im = (db[my_id].table(fill=True)[my_det_probably][1][0]).astype(float)
    else:
        my_im = (db[my_id].table(fill=True)[my_det_probably][1]).astype(float)

    if len(my_im) == 0:
        print("issue... passing")
        pass
    if dark_subtract:
        if "sc_dk_field_uid" in db[my_id].start.keys():
            my_dark_id = db[my_id].start["sc_dk_field_uid"]
            if new_db:
                dark_im = (db[my_dark_id].table(fill=True)[my_det_probably][1][0]).astype(float)
            else:
                dark_im = (db[my_dark_id].table(fill=True)[my_det_probably][1]).astype(float)
    
            my_im = my_im - dark_im
        else:
            print("this run has no associated dark")
    if return_im:
        return my_im
    if return_dark:
        return dark_im
    
    #if all else fails, plot!
    show_me2(my_im, count_low=count_low, count_high=count_high, use_colorbar=use_colorbar, use_cmap=use_cmap)

