
file_loading_timer.start()

from pdftools.detectors import XSPDetector
from ophyd_async.core import init_devices
from ophyd_async.epics.adcore import ADWriterType
from nslsii.ophyd_async.providers import NSLS2PathProvider


try:
    with init_devices():
        lambda1 = XSPDetector("XF:28ID1-ES{Lambda-Det:1}", NSLS2PathProvider(RE.md), writer_type=ADWriterType.TIFF, name="lambda1")
except Exception as e:
    lambda1 = None
    print(f"Lambda detector not available: {e}")


file_loading_timer.stop()