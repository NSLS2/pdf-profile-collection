import numpy as np

import xpdacq.xpdacq
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp


def no_dark(plan):
    def plan_with_shutter():
        yield from xpdacq.xpdacq.open_shutter_stub()
        return (yield from plan)

    return (
        yield from bpp.finalize_wrapper(
            plan_with_shutter(), xpdacq.xpdacq.close_shutter_stub()
        )
    )


def _inject_qualified_dark_frame_uid(msg):
    """Inject the dark frame uid in start."""
    if msg.command == "open_run" and msg.kwargs.get("dark_frame") is not True:
        dark_uid = xpdacq.xpdacq._validate_dark(xpdacq.xpdacq.glbl["dk_window"])
        if dark_uid is not None:
            msg.kwargs["sc_dk_field_uid"] = dark_uid
    return msg


xpdacq.xpdacq._inject_qualified_dark_frame_uid = _inject_qualified_dark_frame_uid


def configure_area_det2(det, exposure: float):
    '''Configure an area detector in "continuous mode"'''
    manufaturer = yield from bps.rd(det.cam.manufacturer, default_value="Unknown")
    if manufaturer == "Perkin Elmer":
        return (yield from _configure_PE(det, exposure))
    else:
        yield from bps.mv(
            det.cam.acquire_time, exposure, det.cam.acquire_period, exposure
        )
        return 1, exposure, exposure


def _configure_PE(det, exposure: float):
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
    acq_time = yield from bps.rd(det.cam.acquire_time, default_value=1)

    _check_mini_expo(exposure, acq_time)

    num_frame = np.ceil(exposure / acq_time)
    yield from bps.mov(det.images_per_set, num_frame)
    computed_exposure = num_frame * acq_time

    # print exposure time
    print(
        "INFO: requested exposure time = {} - > computed exposure time"
        "= {}".format(exposure, computed_exposure)
    )
    return num_frame, acq_time, computed_exposure


def _stateful_configure_ad(exposure: float):
    return (
        yield from configure_area_det2(
            xpdacq.xpdacq.xpd_configuration["area_det"], exposure
        )
    )


xpdacq.beamtime._configure_area_det = _stateful_configure_ad
