import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from itertools import cycle
from xpdacq.xpdacq_conf import xpd_configuration, glbl_dict as glbl
from xpdacq.beamtime import open_shutter_stub, close_shutter_stub
from functools import partial 
import numpy as np


"""Instructions for loop-annealing scan plan 

1) Download to the correct startup directory path for the beamline

(change as necessary): /nsls2/xf28id1/.ipython/profile_collection/startup/

2) Define full list from base temp to max temp

looptlist takes three arguments: 

 - base_temp (25 deg celsius)
 - T_interval (25 deg celsius temperature step)
 - T_steps (number of T_intervals)

>>> flst = looptlist(25, 25, 18)

Check the temperature points: >>> print(flst) 

2) Make sure to import the sample inf with an item for the Ni NPs 

3) Pass scanplan to xrun, as below.
   Note: Exposure and wait times at both base and high temps are configurable

>>> plan = bp.list_scan([xpd_configuration['area_det']], eurotherm, flst, 
per_step=partial(conditional_step, expo_high=60, expo_low=3, wait_high=5, wait_low=3))

>>> xrun(sample_index, plan)

Note that a dark will be collected at the start of each scan
and before each temperature point. So, number of darks = T_steps+1 

"""

def inner_expo(exposure):
    """private function to configure pe1c with continuous acquisition mode
    cs studio configuration doesn't propagate to python level
    """
    yield from bps.abs_set(xpd_configuration["area_det"].cam.acquire_time,
                           glbl["frame_acq_time"],wait=True,)
    print('l50')
    # compute number of frames
    acq_time = xpd_configuration["area_det"].cam.acquire_time.get()
    print('l53')
    # _check_mini_expo(exposure, acq_time)
    num_frame = np.ceil(exposure / acq_time)
    print('l56')
    computed_exposure = num_frame * acq_time
    yield from bps.abs_set(
        xpd_configuration["area_det"].images_per_set, num_frame, wait=True
    )
    print('l61')
    # print exposure time
    print(
        "INFO: requested exposure time = {} - > computed exposure time"
        "= {}".format(exposure, computed_exposure)
    )
    print('l67')
    return num_frame, acq_time, computed_exposure
    


def looptlist(base_temp, T_interval, T_steps):
    mtemp = base_temp + T_interval * T_steps
    tlist = []
    for i in range(base_temp, mtemp, T_interval):
        tlist.append(i)
        tlist.append(base_temp)
    return tlist[1:]


def conditional_step(
    detectors,
    motor,
    step,
    expo_high=60, # all in seconds
    expo_low=600,
    wait_high=5,
    wait_low=3,
    base_temp=25,
):
    """ customized step to:
        1. open shutter
        2. take data
        3. close shutter
        4. wait for equilibrium 
    """
    # base case
    expo = expo_low
    wait = wait_low
    print(step, base_temp)
    if abs(step - base_temp) > 1:
        print("High step")
        expo = expo_high
        wait = wait_high
    else:
        print("Low step")
    print(expo, wait)
    yield from inner_expo(expo)
    yield from motor_dark_step(detectors, motor, step)
    yield from bps.sleep(wait)


def motor_dark_step(detectors, motor, step):
    """
    Take darks while moving motors, wait for all to be finished before 
    taking light
    """

    yield from bps.checkpoint()
    print('l120')
    # close the shutter
    #yield from _close_shutter_stub() COMMENTED OUT (dark per light)
    print('l123')
    # move motors don't wait yet. 
    # Note for Soham: use `group=None` to ramp temp after dark collected
    # (Broken and replaced below) yield from bps.abs_set(motor, step, group="dark_motor")
    yield from bps.abs_set(motor, step, group="dark_motor")
    print('l127')
    # take dark (this has an internal wait on the readback) 
    #yield from bps.trigger_and_read(list(detectors), name="dark") COMMENTED OUT (dark per light)
    print('l130')
    # (Broken) now wait for the motors to be done too
    yield from bps.wait(group="dark_motor")
    print('l133')
    # open shutter
    yield from open_shutter_stub()
    print('l136')
    # take data
    yield from bps.trigger_and_read(list(detectors) + [motor])
    print('l139')
