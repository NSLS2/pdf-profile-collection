# ==================================================================
# Author: H. Zhong
# Date written: 9-11-2019
# Date last updated: 9-11-2019
# Function: 
# %run -i ~/Documents/hzhong/battery_scan_slew.py 
# 
# ==================================================================


from xpdacq.beamtime import _configure_area_det
from xpdacq.beamtime import open_shutter_stub, close_shutter_stub
from collections import ChainMap, OrderedDict
from pandas import ExcelWriter
from pandas import ExcelFile
import functools


def inner_shutter_control(msg):
    if msg.command == "trigger":
        def inner():
            yield from open_shutter_stub()
            yield msg
        return inner(), None
    elif msg.command == "save":
        return None, close_shutter_stub()
    else:
        return None, None


def dark_take(exp_time):
    yield from _configure_area_det(exp_time)
    yield from take_dark()  

def rock_motor_per_step(detector, motor, step, rock_motor = None, rock_motor_limits =None):
    '''
    rock/swing a motor contineously while taking images
    use 'per_step' function in scan plan to rock the motor
    
    detector: pilatus2M or pilatus300
    motor: this motor is NOT used for measurement. use a motor not related to sample/measurement
    step: this step is NOT useed for measurement. set as 1 for single exposure
    rock_motor: the motor to rock.
    rock_motor_limits: the relative rocking position for rock_motor.  
    '''
    
    devices = detector + [motor]
    rewindable = all_safe_rewind(devices)  # if devices can be re-triggered

    current = rock_motor.position
 
    #define rock to swing rock_motor
    #def rock():
        #yield from mvr(rock_motor, rock_motor_limits)
        #yield from mvr(rock_motor, -rock_motor_limits)
    def rock(current=current):
        yield from mv(rock_motor, current + rock_motor_limits)
        yield from mv(rock_motor, current + -rock_motor_limits)
    
    def inner_rock_and_read():

        #yield from trigger(detector)    
        #status = yield from trigger(detector[0])
        status = detector[0].trigger()
        while not status.done:
            yield from rock()
        yield from mv(rock_motor, current )
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
    #Here is how ot use the rock plan
    #our_scan=list_scan([pilatus2M], srot, [1,1], per_step = functools.partial(rock_motor_per_step, rock_motor=strans2, rock_motor_limits=2) )

def slew_plan(motor,motor_v, exp_time,rock_dist):
    yield from _configure_area_det(exp_time)
    area_det = xpd_configuration['area_det']
#    motor.move(pos)
    pos = motor.position
    yield from mv(motor.velocity, motor_v)
    plan = list_scan([area_det],motor,[pos], per_step=functools.partial(rock_motor_per_step,rock_motor=motor,rock_motor_limits=rock_dist))
    plan = bpp.subs_wrapper(plan, LiveTable([motor]))
    plan = bpp.plan_mutator(plan,inner_shutter_control)
    yield from plan    
      	
def battery_scan_slew(sample_mapping, num_cycle, rock_dist=2.5, exp_pdf=180, exp_xrd=30):
    '''
    battery_scan_slew(sample_mapping, num_cycle, motor)
    sample_mapping= [(samp1,x1,y1), (samp2,x2,y2),(samp3,x3,y3)]
    exp_pdf =180   in sec
    exp_xrd = 10   in sec
    rock_dist = 2.5    #motor rocks from -rock_dist to +rock_dist
    '''
    motor = Grid_X
    current_motor_v=motor.velocity.value
    motor_v=0.5
    det_pdf = 1196.35
    det_xrd = 2156.07

    _sorted_mapping = sorted(sample_mapping, key=lambda x: x[0])
    area_det = xpd_configuration['area_det']
    for cycle in range(num_cycle):
        Det_1_Z.move(det_pdf)
        RE(dark_take(exp_pdf))       
        for s, posx, posy in _sorted_mapping:
            print(s, posx,posy)
            motor.velocity.set(current_motor_v)
            motor.move(posx)
            Grid_Y.move(posy)
            plan = slew_plan(motor, motor_v, exp_pdf, rock_dist)
            xrun(s,plan, folder_tag_list=['sample_name','det_key'],det_key='pdf_data')
            time.sleep(10)
        
        Det_1_Z.move(det_xrd)
        RE(dark_take(exp_xrd))
        for s, posx, posy in _sorted_mapping:
            print( s, posx, posy)
            Grid_Y.move(posy)
            motor.velocity.set(current_motor_v)
            motor.move(posx)
            plan = slew_plan(motor, motor_v, exp_xrd, rock_dist)
            xrun(s,plan, folder_tag_list=['sample_name','det_key'],det_key='xrd_data')
            time.sleep(10)            
     
    motor.velocity.set(current_motor_v)   
  	
def battery_scan_slew_AG(sample_mapping, num_cycle, rock_dist=2.5, exp_pdf=180, exp_xrd=30):
    '''
    battery_scan_slew(sample_mapping, num_cycle, motor)
    sample_mapping= [(samp1,x1,y1), (samp2,x2,y2),(samp3,x3,y3)]
    exp_pdf =180   in sec
    exp_xrd = 10   in sec
    rock_dist = 2.5    #motor rocks from -rock_dist to +rock_dist
    
    '''
    motor = Grid_X
    current_motor_v=motor.velocity.value
    motor_v=0.5
    det_pdf = 1196.35
    det_xrd = 2156.07

    area_det = xpd_configuration['area_det']
    for cycle in range(num_cycle):

        Det_1_Z.move(det_xrd)
        RE(dark_take(exp_xrd))
        for s, posx, posy in sample_mapping:
            print( s, posx, posy)
            Grid_Y.move(posy)
            motor.velocity.set(current_motor_v)
            motor.move(posx)
            plan = slew_plan(motor, motor_v, exp_xrd, rock_dist)
            xrun(s,plan, folder_tag_list=['sample_name','det_key'],det_key='xrd_data')
            print('sleeping for 5 s')
            time.sleep(5)   

        Det_1_Z.move(det_pdf)
        RE(dark_take(exp_pdf))       
        for s, posx, posy in sample_mapping:
            print(s, posx,posy)
            motor.velocity.set(current_motor_v)
            motor.move(posx)
            Grid_Y.move(posy)
            plan = slew_plan(motor, motor_v, exp_pdf, rock_dist)
            xrun(s,plan, folder_tag_list=['sample_name','det_key'],det_key='pdf_data')
            print('sleeping for 30 s')
            time.sleep(30)
        
         
    motor.velocity.set(current_motor_v)           
