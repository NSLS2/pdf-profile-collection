def multi_rock(smplist, posxlist, exp_list, motorx=ss_stg2_x, per_shot=rock_motor_per_shot):
    for smpl, posx, exp_time in zip(smplist, posxlist, exp_list):
        motorx.move(posx)
        plan = rock_plan(exp_time, per_shot=per_shot)
        xrun(smpl, plan)
        
def multi_rock_map(smplist, posxlist, posylist, exp_list, motorx=ss_stg2_x, motory=ss_stg2_y, per_shot=rock_2motor_per_shot):
    for smpl, posx, posy, exp_time in zip(smplist, posxlist, posylist, exp_list):
        motorx.move(posx)
        motory.move(posy)
        plan = rock_plan(exp_time, per_shot=per_shot, num=3)
        xrun(smpl, plan)        

def rock_motor_per_shot(detector):
    '''
    need to define inside the plan
    rock_motor: the motor to rock.
    rock_motor_limits: the relative rocking position for rock_motor.


    '''

    devices = detector
    rewindable = all_safe_rewind(devices)  # if devices can be re-triggered
    
    rock_motor = ss_stg2_x  #sample_x
    #rock_motor = sample_y
    rock_motor_limits =3.0
    current = rock_motor.position
    
    # define rock to swing rock_motor
    # def rock():
    # yield from mvr(rock_motor, rock_motor_limits)
    # yield from mvr(rock_motor, -rock_motor_limits)
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


def rock_plan(exp_time, md=None, per_shot=rock_motor_per_shot, num=1, det=[]):
    (num_frame, acq_time, computed_exposure) = yield from _configure_area_det(exp_time)
    _md = {
   
            "sp_time_per_frame": acq_time,
            "sp_num_frames": num_frame,
            "sp_requested_exposure": exp_time,
            "sp_computed_exposure": computed_exposure,     
    }
    _md.update(md or {})

    area_det = xpd_configuration['area_det']
    dets = [area_det] + det  # record the desired det posiitons in md (including temperature controller and motors)
    #at current position, per_step to oscilate rock_motor back and forth with rock_dist, md to update the calib info
    plan = bp.count(dets, per_shot=per_shot, num=num, md=_md)
    plan = bpp.subs_wrapper(plan, LiveTable(det))
    plan = bpp.plan_mutator(plan, inner_shutter_control)
    yield from plan


def rock_2motor_per_shot(detector):
    '''
    rock_motor: the motor to rock.
    rock_motor_limits: the relative rocking position for rock_motor.
    '''
    
    devices = detector
    rewindable = all_safe_rewind(devices)  # if devices can be re-triggered

    rock_motor1 = ss_stg2_x #sample_x
    rock_motor2 = ss_stg2_y #sample_y
    rock_motor1_limits =1
    rock_motor2_limits =1
    rock_motor2_steps =0.2


    current1 = rock_motor1.position
    current2 = rock_motor2.position 

    npoints=int(abs(2*rock_motor2_limits/rock_motor2_steps))+1
    #define rock to swing rock_motor
    #def rock():
        #yield from mvr(rock_motor, rock_motor_limits)
        #yield from mvr(rock_motor, -rock_motor_limits)
    def rock(current1=current1, current2=current2):
        yield from bps.mv(rock_motor2, current2 + rock_motor2_limits)
        for i in range(npoints):
            if (i % 2) == 0:
                yield from bps.mv(rock_motor1, current1 + rock_motor1_limits)
                yield from bps.mvr(rock_motor2, -rock_motor2_steps)
            else:
                yield from bps.mv(rock_motor1, current1 + -rock_motor1_limits)
                yield from bps.mvr(rock_motor2, -rock_motor2_steps)
    
    def inner_rock_and_read():

        #yield from trigger(detector)    
        #status = yield from trigger(detector[0])
        status = detector[0].trigger()
        while not status.done:
            yield from rock()
        yield from mv(rock_motor1, current1 )
        yield from mv(rock_motor2, current2)
        yield from create('primary')

        ret = {}  # collect and return readings to give plan access to them
        for obj in devices:
            reading = (yield from read(obj))
            if reading is not None:
                ret.update(reading)
        yield from save()
        return ret

    from bluesky.preprocessors import rewindable_wrapper
    return (yield from rewindable_wrapper(inner_rock_and_read(),rewindable))

def slew_plan_2d(motorx, posx, motory, posy, exp_time):
    yield from _configure_area_det(exp_time)
    area_det = xpd_configuration['area_det']

    yield from mv(motorx, posx)
    yield from mv(motory, posy)


    plan = bp.count([area_det],per_shot=rock_2motor_per_shot)
    plan = bpp.subs_wrapper(plan, LiveTable([motorx, motory]))
    plan = bpp.plan_mutator(plan,inner_shutter_control)
    yield from plan