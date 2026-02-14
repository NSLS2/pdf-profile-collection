from nslsii.detectors.webcam import VideoStreamDet
from nsls2_detector_handlers.webcam import VideoStreamHDF5Handler

db.reg.register_handler("VIDEO_STREAM_HDF5", VideoStreamHDF5Handler, overwrite=True)

webcam_root_dir = "/nsls2/data/pdf/legacy/raw/webcams"

cam_outboard = VideoStreamDet(
    video_stream_url="http://10.66.217.45/mjpg/video.mjpg",
    frame_shape=(1080, 1920),
    root_dir=webcam_root_dir,
    name="cam_outboard",
)
cam_outboard.exposure_time.put(0.05)

cam_downstream = VideoStreamDet(
    video_stream_url="http://10.66.217.46/mjpg/video.mjpg",
    frame_shape=(1080, 1920),
    root_dir=webcam_root_dir,
    name="cam_downstream",
)
cam_downstream.exposure_time.put(0.05)
