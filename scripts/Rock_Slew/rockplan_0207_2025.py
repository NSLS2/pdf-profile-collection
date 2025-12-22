def rock_plan(exp_time,  num=1, delay_num=0, rock_motor=sample_y, rock_motor_limits=2, det=[ion_chamber],md=None):

    def rock_motor_per_shot(detector):

        devices = detector
        rewindable = all_safe_rewind(devices)  # if devices can be re-triggered
        current = rock_motor.position
        def rock(current=current):
            yield from bps.mv(rock_motor, current + rock_motor_limits)
            yield from bps.mv(rock_motor, current + -rock_motor_limits)

        def inner_rock_and_read():

            # yield from trigger(detector)
            # status = yield from trigger(detector[0])
            status = detector[0].trigger()
            while not status.done:
                yield from rock()
            yield from bps.mv(rock_motor, current)
            yield from create('primary')

            ret = {}  # collect and return readings to give plan access to them
            for obj in devices:
                reading = (yield from read(obj))
                if reading is not None:
                    ret.update(reading)
            yield from save()
            return ret

        from bluesky.preprocessors import rewindable_wrapper
        return (yield from rewindable_wrapper(inner_rock_and_read(), rewindable))

    
    (num_frame, acq_time, computed_exposure) = yield from _configure_area_det(exp_time)
    _md = {
   
            "sp_time_per_frame": acq_time,
            "sp_num_frames": num_frame,
            "sp_requested_exposure": exp_time,
            "sp_computed_exposure": computed_exposure,     
    }
    _md.update(md or {})

    if ion_chamber in det:
        #yield from bps.mv(ecal_x, 60, ecal_y, -6)
        if ion_chamber.period.get()!= acq_time:
            yield from bps.mv(ion_chamber.period, acq_time)
        ion_chamber.trigs_to_average = num_frame 
    delay_num1 = delay_num + exp_time
    area_det = xpd_configuration['area_det']
    dets = [area_det] + det  # record the desired det posiitons in md (including temperature controller and motors)
    #at current position, per_step to oscilate rock_motor back and forth with rock_dist, md to update the calib info
    plan = bp.count(dets, per_shot=rock_motor_per_shot, num=num, delay=delay_num1, md=_md)
    plan = bpp.subs_wrapper(plan, LiveTable(det))
    plan = bpp.plan_mutator(plan, inner_shutter_control)
    yield from plan


def xpd_mscan_rock(sample_list, posx_list, exp_time, posy_list=None,  num=1, delay_num=0, delay=0, smpl_h=None, flt_h=None, flt_l=None,
                motorx=sample_x, motory=sample_y, rock_motor=sample_y, rock_motor_limits=2, dets=[ion_chamber], md=None):
    """ Perform multi-sample scans by moving samples to predefined x and y positions, applying filters,
    and executing a scan plan.

    Example:

        >>> samples = [1, 2, 3]
        >>> x_positions = [10, 20, 30]
        >>> y_positions = [5, 15, 25]
        >>> scan_plan = 0
        >>> special_samples = [1, 3]
        >>> special_filter = [1, 0, 0, 0]
        >>> default_filter = [0, 0, 0, 0]
        >>> xpd_m2dscan(samples, x_positions, y_positions, scan_plan, delay=2, smpl_h=special_samples, flt_h=special_filter, flt_l=default_filter)
        if all samples use the same filter set which has been set manually
        >>>   multi-sample scan plan, parameters:
        sample_list (list): list of all samples in the sample holder
        posx_lis, posy_list: list of sample x and y positions, sample_list, posx_list, posy_list should be match
        motorx, motory: motors which moves sample holder, default is sample_x and sample_y
        exp_time : total exposure time for each sample, in seconds
        num: number of data at each time
        delay_num : sleep time in between each data if multiple data are taken at each time
        delay: delay time in between each sample
        smpl_h: list of samples which needs special filter set flt_h
        flt_h: filter set for samples in smpl_h
        flt_l: filter set for rest of the samples
    """
    # Input validation
    
    if len(sample_list) != len(posx_list):
        raise ValueError("sample_list, posx_list must have the same length")
    if posy_list and (len(posx_list) != len(posy_list)):
        raise ValueError("posxlist and posylist must have the same length if posylist is provided")

    # Ensure that if smpl_h is provided, both flt_h and flt_l are provided
    if smpl_h is not None and (flt_h is None or flt_l is None):
        raise ValueError("If smpl_h is provided, both flt_h and flt_l must also be provided.")

    if smpl_h is None:
        smpl_h = []
    if dets is None:
        dets = []

    if posy_list is not None:
        dets = dets + [motorx, motory]
    else:
        dets = dets + [motorx]

    length = len(sample_list)
    print('Total sample numbers:', length)

    def move_to_position(posx, posy=None):
        """Helper to move motors to the specified position."""
        motorx.move(posx)
        if posy is not None:
            motory.move(posy)

    for sample, posx, posy in zip(sample_list, posx_list, posy_list or [None] * len(posx_list)):
        print(f'Move sample {sample} to position ({posx}, {posy})')
        move_to_position(posx, posy)

        if sample in smpl_h:
            if flt_h is not None:
                xpd_flt_set(flt_h)
        else:
            if flt_l is not None:
                xpd_flt_set(flt_l)
        # Delay between samples
        time.sleep(delay)
        #run the scan plan
        print(f'Running scan plan for sample {sample}')
        plan = rock_plan(exp_time,  num=num, delay_num=delay_num, rock_motor=rock_motor, rock_motor_limits=rock_motor_limits, det=dets,md=md)
        xrun(sample, plan)    

    print('Multi-sample scan complete.')

