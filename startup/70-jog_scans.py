from functools import partial

from bluesky.utils import short_uid
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp


def future_count(detectors, num=1, delay=None, *, per_shot=None, md=None):
    """
    Take one or more readings from detectors.
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    num : integer, optional
        number of readings to take; default is 1
        If None, capture data until canceled
    delay : iterable or scalar, optional
        Time delay in seconds between successive readings; default is 0.
    per_shot : callable, optional
        hook for customizing action of inner loop (messages per step)
        Expected signature ::
           def f(detectors: Iterable[OphydObj]) -> Generator[Msg]:
               ...
    md : dict, optional
        metadata
    Notes
    -----
    If ``delay`` is an iterable, it must have at least ``num - 1`` entries or
    the plan will raise a ``ValueError`` during iteration.
    """
    if num is None:
        num_intervals = None
    else:
        num_intervals = num - 1
    _md = {
        "detectors": [det.name for det in detectors],
        "num_points": num,
        "num_intervals": num_intervals,
        "plan_args": {"detectors": list(map(repr, detectors)), "num": num},
        "plan_name": "count",
        "hints": {},
    }
    _md.update(md or {})
    _md["hints"].setdefault("dimensions", [(("time",), "primary")])

    if per_shot is None:
        per_shot = bps.one_shot

    @bpp.stage_decorator(detectors)
    @bpp.run_decorator(md=_md)
    def inner_count():
        return (
            yield from bps.repeat(partial(per_shot, detectors), num=num, delay=delay)
        )

    return (yield from inner_count())


def _xpd_pre_plan(dets, exposure):
    """Handle detector exposure time + xpdan required metadata"""

    # setting up area_detector
    for ad in (d for d in dets if hasattr(d, "cam")):
        (num_frame, acq_time, computed_exposure) = yield from configure_area_det2(
            ad, exposure
        )
    else:
        acq_time = 0
        computed_exposure = exposure
        num_frame = 0

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

    return _md


def rocking_ct(dets, exposure, motor, start, stop, *, num=1, md=None):
    """Take a count while "rocking" the y-position"""
    _md = md or {}
    sp_md = yield from _xpd_pre_plan(dets, exposure)
    _md.update(sp_md)
    _md["plan_name"] = "jog"
    _md["jog_md"] = {"start": start, "stop": stop, "motor": motor.name}

    @bpp.reset_positions_decorator([motor.velocity])
    def per_shot(dets):
        nonlocal start, stop
        yield from bps.mv(motor, start)  # got to initial position
        yield from bps.mv(motor.velocity, abs(stop - start) / exposure, timeout=1)  # set velocity
        gp = short_uid("rocker")
        yield from bps.abs_set(motor, stop, group=gp)  # set motor to move towards end
        yield from bps.trigger_and_read(dets)  # collect off detector
        yield from bps.wait(group=gp)
        start, stop = stop, start

    return (yield from future_count(dets, md=_md, 
                                    per_shot=per_shot if start != stop else bps.trigger_and_read, 
                                    num=num))


def jog(dets, exposure_s, motor, start, stop, md=None):
    """pass total exposure time (in seconds), motor name (i.e. Grid_Y), start and stop positions for the motor."""
    # yield from rocking_ct([pilatus], exposure_s, motor, start, stop)
    yield from rocking_ct(dets, exposure_s, motor, start, stop, md=md)



## The following plans desgiend for pilatus jogging by CHLin on 2025/08/27 
def repeat_count(detectors, num=1, delay=None, *, per_shot=None, md=None):
    """
    Take one or more readings from detectors.
    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    num : integer, optional
        number of readings to take; default is 1
        If None, capture data until canceled
    delay : iterable or scalar, optional
        Time delay in seconds between successive readings; default is 0.
    per_shot : callable, optional
        hook for customizing action of inner loop (messages per step)
        Expected signature ::
           def f(detectors: Iterable[OphydObj]) -> Generator[Msg]:
               ...
    md : dict, optional
        metadata
    Notes
    -----
    If ``delay`` is an iterable, it must have at least ``num - 1`` entries or
    the plan will raise a ``ValueError`` during iteration.
    """
    if num is None:
        num_intervals = None
    else:
        num_intervals = num - 1
    _md = {
        "detectors": [det.name for det in detectors],
        "num_points": num,
        "num_intervals": num_intervals,
        "plan_args": {"detectors": list(map(repr, detectors)), "num": num},
        "hints": {},
    }
    _md.update(md or {})
    _md["hints"].setdefault("dimensions", [(("time",), "primary")])

    if per_shot is None:
        per_shot = bps.one_shot

    @bpp.stage_decorator(detectors)
    @bpp.run_decorator(md=_md)
    def inner_count():
        return (
            yield from bps.repeat(partial(per_shot, detectors), num=num, delay=delay)
        )

    return (yield from inner_count())



def _pila_pre_plan(dets, exposure):
    """Handle detector exposure time + xpdan required metadata"""

    if 'pilatus1' not in dets[0].name:
        raise ValueError('This plan is for pilatus but not pilatus in dets')

    # setting up area_detector
    for ad in (d for d in dets if hasattr(d, "cam")):
        (num_frame, acq_time, computed_exposure) = yield from configure_area_det2(
            ad, exposure
        )
    else:
        acq_time = 0
        computed_exposure = exposure
        num_frame = 0

    sp = {
        "time_per_frame": acq_time,
        "num_frames": num_frame,
        "requested_exposure": exposure,
        "computed_exposure": computed_exposure,
        "type": "trigger_and_read",
        "uid": str(uuid.uuid4()),
        "plan_name": "jog_pila_3pos",
    }

    _md = ChainMap(
        {
            "sp_time_per_frame": acq_time,
            "sp_num_frames": num_frame,
            "sp_requested_exposure": exposure,
            "sp_computed_exposure": computed_exposure,
            "sp_type": "bps.trigger",
            "sp_uid": str(uuid.uuid4()),
            "sp_plan_name": "pila_jog",
            "sp_detector": dets[0].name, 
            "detectors": [area_det.name for area_det in dets],
            # "data_keys": "pe1c_image", 
        },
    )

    # update md
    _md.update({"sp": sp, **{f"sp_{k}": v for k, v in sp.items()}})

    return _md




## revised from pila_3pos (pdf_RE4) for putting into jog
def pre_pila_3pos(dets, exposure, extra_md={}):

    #det_x_pos = [40.644, 31.356, 36] - MA detector mounting is different 07/04/2025
    det_x_pos = [20.644, 11.356, 16]
    det_y_pos = [-3.356, -12.644, -8]

    if 'det_x_pos' in extra_md.keys():
        det_x_pos = extra_md['det_x_pos']

    if 'det_y_pos' in extra_md.keys():
        det_y_pos = extra_md['det_y_pos'] 

    ## since jog already has the below 2 decorators so skipped here by CHL on 2025/08/25
    # @bpp.stage_decorator([area_det]+motors)
    # @bpp.run_decorator(md=_md)
    def inner_scan(dets, det_x_pos=det_x_pos, det_y_pos=det_y_pos):            
        for i in range(len(det_x_pos)):
            # yield from bps.mv(Grid_X, det_x_pos[i], Grid_Y, det_y_pos[i])
            yield from periodic_dark(trigger_and_read(dets, name=f"PDF_{dets[0].name}_{i}"))
                    
                
    yield from inner_scan(dets, det_x_pos=det_x_pos, det_y_pos=det_y_pos)




## Revise jog for pilatus 3-position scan
def jog_pila(dets, exposure, motor, start, stop, *, num=1, md=None):
    """Take a count while "rocking" the y-position"""
    _md = md or {}
    sp_md = yield from _pila_pre_plan(dets, exposure)
    _md.update(sp_md)
    _md["plan_name"] = "jog_pila_3pos"
    _md["jog_md"] = {"start": start, "stop": stop, "motor": motor.name}

    @bpp.reset_positions_decorator([motor.velocity])
    def per_shot(dets):
        nonlocal start, stop
        yield from bps.mv(motor, start)  # got to initial position
        yield from bps.mv(motor.velocity, abs(stop - start) / exposure, timeout=1)  # set velocity
        gp = short_uid("rocker")
        yield from bps.abs_set(motor, stop, group=gp)  # set motor to move towards end
        # yield from bps.trigger_and_read(dets)  # collect off detector
        yield from pre_pila_3pos(dets, exposure)
        yield from bps.wait(group=gp)
        start, stop = stop, start

    return (yield from repeat_count(dets, md=_md, 
                                    per_shot=per_shot if start != stop else bps.trigger_and_read, 
                                    num=num))


# def jog_pila(dets, exposure_s, motor, start, stop, md=None):
#     """pass total exposure time (in seconds), motor name (i.e. Grid_Y), start and stop positions for the motor."""
#     # yield from rocking_ct([pilatus], exposure_s, motor, start, stop)
#     yield from rocking_pila_3pos(dets, exposure_s, motor, start, stop, md=md)



