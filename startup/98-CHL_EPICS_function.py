import ophyd
from ophyd import (Device, Component as Cpt,
                   EpicsSignal, EpicsSignalRO, EpicsMotor)
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV, AreaDetector
from ophyd.status import SubscriptionStatus
import skimage


import datetime
import os

def auto_name_file(filename_prefix, file_extension, directory=None):
    """
    Generates a filename with the current date and time, and saves the file.

    Args:
        filename_prefix: The beginning of the fiEpicsSignallename (e.g., "data").
        file_extension: The file extension (e.g., ".txt", ".csv").
        directory: (Optional) The directory to save the file in. 
                   If None, saves to the current working directory.

    Returns:
        The full path to the created file.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    if filename_prefix == '':
        new_filename = f"{timestamp}{file_extension}"
    else:
        new_filename = f"{filename_prefix}_{timestamp}{file_extension}"

    if directory:
        os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
        filepath = os.path.join(directory, new_filename)
    else:
        filepath = new_filename
    
    # Create an empty file (or overwrite if it exists)
    with open(filepath, 'w') as f:
        pass

    return filepath

# # Example usage:
# file_path = auto_name_file("my_data", ".txt", "my_files")
# print(f"File created at: {file_path}")

# file_path2 = auto_name_file("report", ".csv") # saves in current directory
# print(f"File created at: {file_path2}")


class Cam(AreaDetector):
    # pass

    acquire = Cpt(EpicsSignal, 'cam1:Acquire')
    expousre_time = Cpt(EpicsSignal, 'cam1:AcquireTime', kind = 'config')
    acquire_period = Cpt(EpicsSignal, 'cam1:AcquirePeriod', kind = 'config')
    num_exposure = Cpt(EpicsSignal, 'cam1:NumExposures', kind = 'config')
    ArrayData = Cpt(EpicsSignal, 'image1:ArrayData', kind = 'normal')
    # ArraySize1 = Cpt(EpicsSignalRO, 'image1:ArraySize1_RBV', kind = 'config')
    # ArraySize2 = Cpt(EpicsSignalRO, 'image1:ArraySize2_RBV', kind = 'config')
    ArraySize0 = Cpt(EpicsSignalRO, 'TIFF1:ArraySize0_RBV', kind = 'config')
    ArraySize1 = Cpt(EpicsSignalRO, 'TIFF1:ArraySize1_RBV', kind = 'config')
    ArraySize2 = Cpt(EpicsSignalRO, 'TIFF1:ArraySize2_RBV', kind = 'config')
    
    # image = Cpt(ImagePlugin, 'image1:', kind = 'normal')
    # tiff = Cpt(TIFFPlugin, 'TIFF1:',
    #         write_path_template='/nsls2/data/pdf/legacy/raw/cam1/%Y/%m/%d/',
    #         root='/nsls2/data/pdf/legacy/raw')

    def grab_frame(self):

        def is_done(value, old_value, **kwargs):
            if old_value == 1 and value ==0:
                return True
            return False

        status = SubscriptionStatus(self.acquire, run=False, callback=is_done)

        self.acquire.put(1)
        return status
    
    def trigger(self):
        #self.grab_frame().wait()
        # return self.grab_frame()
        # return (yield from self.grab_frame2())
        return self.grab_frame()



Cam1 = Cam('XF:28ID1-BI{Cam:1}', name='Cam1')


def save_Cam1_tiff(is_plot=True, is_save=True):
    new_shape = (Cam1.ArraySize2.get(), Cam1.ArraySize1.get(), Cam1.ArraySize0.get())
    data = np.reshape(Cam1.ArrayData.get(), new_shape)
    
    if is_plot:
        plt.figure()
        plt.imshow(data.mean(axis=2, dtype=np.float32))
    
    if is_save:
        fn_path = '/home/xf28id1/Documents/raw/cam1'
        fn_name = auto_name_file('', '.tiff', fn_path)
        skimage.io.imsave(fn_name, data.mean(axis=2, dtype=np.float32))



class PDFCam1(AreaDetector):
    image = Cpt(ImagePlugin, 'image1:')
    _default_configuration_attrs = (
        AreaDetector._default_configuration_attrs +
        ('images_per_set', 'number_of_sets'))

    tiff = Cpt(XPDTIFFPlugin, 'TIFF1:', #- MA
             #write_path_template='Z:/data/pe1_data/%Y/%m/%d', #- DO
             #write_path_template='J:\\%Y\\%m\\%d\\', #- DO
             #write_path_template='Z:/img/%Y/%m/%d/', #- MA
             write_path_template='/home/xf28id1/Documents/raw/cam1/temp/', 
             #read_path_template='/SHARE/img/%Y/%m/%d/', #- MA
             #read_path_template='/nsls2/data/pdf/legacy/raw/cam1/%Y/%m/%d/', #- DO
             read_path_template='/home/xf28id1/Documents/raw/cam1/temp/', 
             #root='/nsls2/data/pdf/legacy/raw/cam1/', #-DO
             #root='/SHARE/img/', #-MA
             root='/home/xf28id1/Documents/raw/cam1/temp/', 
             cam_name='cam',  # used to configure "tiff squashing" #-MA
             proc_name='proc',  # ditto #-MA
             read_attrs=[]) #- MA  
    # hdf5 = C(XPDHDF5Plugin, 'HDF1:',
    #          write_path_template='G:/pe1_data/%Y/%m/%d/',
    #          read_path_template='/direct/XF28ID2/pe1_data/%Y/%m/%d/',
    #          root='/direct/XF28ID2/', reg=db.reg)

    proc = Cpt(ProcessPlugin, 'Proc1:')

    # These attributes together replace `num_images`. They control
    # summing images before they are stored by the detector (a.k.a. "tiff
    # squashing").
    detector_type = Cpt(Signal, value='Perkin', kind='config')
    images_per_set = Cpt(Signal, value=1, add_prefix=())
    number_of_sets = Cpt(Signal, value=1, add_prefix=())

    stats1 = Cpt(StatsPluginV33, 'Stats1:')
    stats2 = Cpt(StatsPluginV33, 'Stats2:')
    stats3 = Cpt(StatsPluginV33, 'Stats3:')
    stats4 = Cpt(StatsPluginV33, 'Stats4:')
    stats5 = Cpt(StatsPluginV33, 'Stats5:')

    roi1 = Cpt(ROIPlugin, 'ROI1:')
    roi2 = Cpt(ROIPlugin, 'ROI2:')
    roi3 = Cpt(ROIPlugin, 'ROI3:')
    roi4 = Cpt(ROIPlugin, 'ROI4:')

    # dark_image = C(SavedImageSignal, None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update([(self.cam.trigger_mode, 'Internal'),
                               ])



class Cam_2(ContinuousAcquisitionTrigger, PDFCam1):
    pass


Cam2 = Cam_2('XF:28ID1-BI{Cam:1}', name='Cam2', read_attrs=['tiff', 'stats1.total'],
            plugin_name='tiff')


from ophyd.areadetector.trigger_mixins import SingleTrigger
from ophyd.areadetector.detectors import PvcamDetector, AreaDetector

class MyDetector(SingleTrigger, Cam):
    pass

prefix = 'XF:28ID1-BI{Cam:1}'
CamS = MyDetector(prefix, name='CamS')


def cam_BS_scan(det, md=None):
    # det = Cam1
    _md = {}
    _md.update(md or {})
    
    @bpp.stage_decorator([det])
    @bpp.run_decorator(md=_md)
    def trigger_detector():  # TODO: rename appropriately
        ret = {}
        yield from bps.trigger(det, wait=True)
        yield from bps.create(name="Cam1_RE")
        reading = (yield from bps.read(det))
        # print(f"reading = {reading}")
        ret.update(reading)
        yield from bps.save()
    yield from trigger_detector()


# data = np.reshape(Cam1.ArrayData.get(), (Cam1.ArraySize2.get(), Cam1.ArraySize1.get(), Cam1.ArraySize0.get())
# data = np.reshape(Cam1.ArrayData.get(), (Cam1.ArraySize2.get(), Cam1.ArraySize1.get(),3)
# Cam1_TIFF1 = EpicsSignal('XF:28ID1-BI{Cam:1}TIFF1', name='Cam1_TIFF1', kind='normal')




# XF:28ID1-BI{Cam:1}ROI1:MinX
# XF:28ID1-BI{Cam:1}ROI1:MinY
# XF:28ID1-BI{Cam:1}ROI1:SizeX
# XF:28ID1-BI{Cam:1}ROI1:SizeY
# XF:28ID1-BI{Cam:1}ROI2:MinX
# XF:28ID1-BI{Cam:1}ROI2:MinY
# XF:28ID1-BI{Cam:1}ROI2:SizeX
# XF:28ID1-BI{Cam:1}ROI2:SizeY
# XF:28ID1-BI{Cam:1}ROI3:MinX
# XF:28ID1-BI{Cam:1}ROI3:MinY
# XF:28ID1-BI{Cam:1}ROI3:SizeX
# XF:28ID1-BI{Cam:1}ROI3:SizeY
# XF:28ID1-BI{Cam:1}ROI4:MinX
# XF:28ID1-BI{Cam:1}ROI4:MinY
# XF:28ID1-BI{Cam:1}ROI4:SizeX
# XF:28ID1-BI{Cam:1}ROI4:SizeY
# XF:28ID1-BI{Cam:1}Stats1:ComputeHistogram
# XF:28ID1-BI{Cam:1}Stats1:HistSize_RBV
# XF:28ID1-BI{Cam:1}Stats1:Histogram_RBV
# XF:28ID1-BI{Cam:1}Stats1:MaxValue_RBV
# XF:28ID1-BI{Cam:1}Stats1:MeanValue_RBV
# XF:28ID1-BI{Cam:1}Stats1:MinValue_RBV
# XF:28ID1-BI{Cam:1}Stats1:Sigma_RBV
# XF:28ID1-BI{Cam:1}Stats1:Total_RBV
# XF:28ID1-BI{Cam:1}Stats2:Total_RBV
# XF:28ID1-BI{Cam:1}Stats3:Total_RBV
# XF:28ID1-BI{Cam:1}Stats4:Total_RBV
# XF:28ID1-BI{Cam:1}Stats5:Total_RBV
# XF:28ID1-BI{Cam:1}cam1:Acquire
# XF:28ID1-BI{Cam:1}cam1:AcquirePeriod
# XF:28ID1-BI{Cam:1}cam1:AcquirePeriod_RBV
# XF:28ID1-BI{Cam:1}cam1:AcquireTime
# XF:28ID1-BI{Cam:1}cam1:AcquireTime_RBV
# XF:28ID1-BI{Cam:1}cam1:ArrayCounter
# XF:28ID1-BI{Cam:1}cam1:ArrayCounter_RBV
# XF:28ID1-BI{Cam:1}cam1:ArrayRate_RBV
# XF:28ID1-BI{Cam:1}cam1:AsynIO.CNCT
# XF:28ID1-BI{Cam:1}cam1:DetectorState_RBV
# XF:28ID1-BI{Cam:1}cam1:ImageMode
# XF:28ID1-BI{Cam:1}cam1:ImageMode_RBV
# XF:28ID1-BI{Cam:1}cam1:NumExposures
# XF:28ID1-BI{Cam:1}cam1:NumExposures_RBV
# XF:28ID1-BI{Cam:1}cam1:NumImages
# XF:28ID1-BI{Cam:1}cam1:NumImagesCounter_RBV
# XF:28ID1-BI{Cam:1}cam1:NumImages_RBV
# XF:28ID1-BI{Cam:1}cam1:TriggerMode
# XF:28ID1-BI{Cam:1}cam1:TriggerMode_RBV
# XF:28ID1-BI{Cam:1}image1:ArrayData
# XF:28ID1-BI{Cam:1}image1:ArraySize1_RBV
# XF:28ID1-BI{Cam:1}image1:ArraySize2_RBV
# XF:28ID1-CT{IOC:Cam1}:SysReset




# XF:28ID1-BI{Cam:1}TIFF1:ADCoreVersion_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArrayCallbacks
# XF:28ID1-BI{Cam:1}TIFF1:ArrayCallbacks_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArrayCounter
# XF:28ID1-BI{Cam:1}TIFF1:ArrayCounter_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArrayRate_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArraySize0_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArraySize1_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ArraySize2_RBV
# XF:28ID1-BI{Cam:1}TIFF1:AutoIncrement
# XF:28ID1-BI{Cam:1}TIFF1:AutoIncrement_RBV
# XF:28ID1-BI{Cam:1}TIFF1:AutoSave
# XF:28ID1-BI{Cam:1}TIFF1:AutoSave_RBV
# XF:28ID1-BI{Cam:1}TIFF1:Capturecam1:AcquirePeriod
# XF:28ID1-BI{Cam:1}TIFF1:Capture_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ColorMode_RBV
# XF:28ID1-BI{Cam:1}TIFF1:CreateDirectory
# XF:28ID1-BI{Cam:1}TIFF1:CreateDirectory_RBV
# XF:28ID1-BI{Cam:1}TIFF1:DataType_RBV
# XF:28ID1-BI{Cam:1}TIFF1:DeleteDriverFile
# XF:28ID1-BI{Cam:1}TIFF1:DeleteDriverFile_RBV
# XF:28ID1-BI{Cam:1}TIFF1:DriverVersion_RBV
# XF:28ID1-BI{Cam:1}TIFF1:DroppedArrays
# XF:28ID1-BI{Cam:1}TIFF1:DroppedArrays_RBV
# XF:28ID1-BI{Cam:1}TIFF1:EnableCallbacks
# XF:28ID1-BI{Cam:1}TIFF1:EnableCallbacks_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ExecutionTime_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FileName
# XF:28ID1-BI{Cam:1}TIFF1:FileName_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FileNumber
# XF:28ID1-BI{Cam:1}TIFF1:FileNumber_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FilePath
# XF:28ID1-BI{Cam:1}TIFF1:FilePathExists_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FilePath_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FileTemplate
# XF:28ID1-BI{Cam:1}TIFF1:FileTemplate_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FileWriteMode
# XF:28ID1-BI{Cam:1}TIFF1:FileWriteMode_RBV
# XF:28ID1-BI{Cam:1}TIFF1:FullFileName_RBV
# XF:28ID1-BI{Cam:1}TIFF1:LazyOpen
# XF:28ID1-BI{Cam:1}TIFF1:LazyOpen_RBV
# XF:28ID1-BI{Cam:1}TIFF1:MinCallbackTime
# XF:28ID1-BI{Cam:1}TIFF1:MinCallbackTime_RBV
# XF:28ID1-BI{Cam:1}TIFF1:NDArrayAddress
# XF:28ID1-BI{Cam:1}TIFF1:NDArrayAddress_RBV
# XF:28ID1-BI{Cam:1}TIFF1:NDArrayPort
# XF:28ID1-BI{Cam:1}TIFF1:NDArrayPort_RBV
# XF:28ID1-BI{Cam:1}TIFF1:NDimensions_RBV
# XF:28ID1-BI{Cam:1}TIFF1:NumCapture
# XF:28ID1-BI{Cam:1}TIFF1:NumCapture_RBV
# XF:28ID1-BI{Cam:1}TIFF1:NumCaptured_RBV
# XF:28ID1-BI{Cam:1}TIFF1:PluginType_RBV
# XF:28ID1-BI{Cam:1}TIFF1:PortName_RBV
# XF:28ID1-BI{Cam:1}TIFF1:ProcessPlugin
# XF:28ID1-BI{Cam:1}TIFF1:QueueFree
# XF:28ID1-BI{Cam:1}TIFF1:QueueSize
# XF:28ID1-BI{Cam:1}TIFF1:ReadFile
# XF:28ID1-BI{Cam:1}TIFF1:ReadFile_RBV
# XF:28ID1-BI{Cam:1}TIFF1:TempSuffix
# XF:28ID1-BI{Cam:1}TIFF1:TempSuffix_RBV
# XF:28ID1-BI{Cam:1}TIFF1:TimeStamp_RBV
# XF:28ID1-BI{Cam:1}TIFF1:UniqueId_RBV
# XF:28ID1-BI{Cam:1}TIFF1:WriteFile
# XF:28ID1-BI{Cam:1}TIFF1:WriteFile_RBV
# XF:28ID1-BI{Cam:1}TIFF1:WriteMessage
# XF:28ID1-BI{Cam:1}TIFF1:WriteStatus




# loc://DID_56AutoScale
# loc://DID_56AutoScale(2.0)
# loc://DID_56DispROI1
# loc://DID_56DispROI2
# loc://DID_56DispROI3
# loc://DID_56DispROI4
# loc://DID_56DispStats1
# loc://DID_56DispStats1(0)
# loc://DID_56DispStats2
# loc://DID_56DispStats2(0)
# loc://DID_56DispStats3
# loc://DID_56DispStats3(0)
# loc://DID_56DispStats4
# loc://DID_56DispStats4(0)
# loc://DID_56DispStats5
# loc://DID_56DispStats5(1)
# loc://DID_56Max
# loc://DID_56Max(65536)
# loc://DID_56Min
# loc://DID_56Min(0.0)
# loc://DID_56NSigma
# loc://DID_56NSigma(1.0)
# loc://DID_56hpx
# loc://DID_56hpy
# loc://DID_56vpx
# loc://DID_56vpy