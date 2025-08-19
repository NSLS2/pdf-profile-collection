import os
import numpy as np
import tifffile
from configparser import ConfigParser
from tiled.client import from_profile
tiled_client = from_profile('pdf')



def _readable_time(unix_time):
    from datetime import datetime
    dt = datetime.fromtimestamp(unix_time)
    # print(f'{dt.year}{dt.month:02d}{dt.day:02d},{dt.hour:02d}{dt.minute:02d}{dt.second:02d}')
    return (f'{dt.year}{dt.month:02d}{dt.day:02d}'), (f'{dt.hour:02d}{dt.minute:02d}{dt.second:02d}')



class imgData_config(ConfigParser):
    """The configuration for the server."""

    def __init__(self, config_fn, **kwargs):
        # self.uid = uid
        self.config_fn = config_fn
        super().__init__(**kwargs)


    def read(self, **kwargs):
        return super().read(self.config_fn, **kwargs)
        



class imgData_2D(imgData_config):

    def __init__(self, uid, tiled_client, sandbox_tiled, config_fn, **kwargs):
        self.uid = uid
        super().__init__(config_fn, **kwargs)
        self.read(**kwargs)

        self.tiled_client = tiled_client
        self.sandbox_tiled = sandbox_tiled
        self.run = tiled_client[uid]
        
        self.raw_db = self.get('topics', 'raw_db', fallback='pdf')
        self.an_db = self.get('topics', 'an_db', fallback='pdf-analysis')

        self.full_uid = self.run.start['uid']

        self.sample_name = self.run.start['sample_name']  ## update at start doc
        self.dksub_uid = None   ## update at event doc
        self.stream_name = []  ## update at stop doc

        self.process_img = None


    @property
    def detector(self):
        return self.run.start['detectors'][0]


    @property
    def stream_length(self):
        return len(self.stream_name)

    @property
    def user_data(self):
        fallback = '/nsls2/data/pdf/pdfhack/legacy/processed/xpdacq_data/user_data'
        return self.get('PATH', 'user_data', fallback=fallback)
    
    @property
    def tiff_base(self):
        n = self.get('PATH', 'tiff_base', fallback='tiff_base')
        return os.path.join(self.user_data, n)
    
    @property
    def config_base(self):
        n = self.get('PATH', 'config_base', fallback='config_base')
        return os.path.join(self.user_data, n)     

    @property
    def pilatus_PDF(self):
        n = self.get('PATH', 'pilatus_PDF', fallback='pilatus_PDF')
        return os.path.join(self.config_base, n)
    
    @property
    def pilatus_XRD(self):
        n = self.get('PATH', 'pilatus_XRD', fallback='pilatus_XRD')
        return os.path.join(self.config_base, n)
    

    @property
    def masks_pos_flist(self):
        m1 = self.get('PATH', 'mask_01', fallback='Mask_pos1_ext_BS.npy')
        m2 = self.get('PATH', 'mask_02', fallback='Mask_pos2_ext_BS.npy')
        m3 = self.get('PATH', 'mask_03', fallback='Mask_pos3_ext_BS.npy')
        return [m1, m2, m3]
    
    @property
    def osetx(self):
        return self.getint('SUM', 'osetx', fallback=27)
    
    @property
    def osety(self):
        return self.getint('SUM', 'osety', fallback=27)
    
    @property
    def use_flat_field_pila(self):
        return self.getboolean('SUM', 'use_flat_field_pila', fallback=False)
    
    @property
    def flat_field_pila(self):
        n_folder = self.get('PATH', 'flat_filed', fallback='flat_filed')
        n = self.get('PATH', 'flat_field_pila', fallback='flat_field_pila.tiff')
        return os.path.join(self.config_base, n_folder, n)
    
    @property
    def use_flat_field_pe1c(self):
        return self.getboolean('SUM', 'use_flat_field_pe1c', fallback=False)
    
    @property
    def flat_field_pe1c(self):
        n_folder = self.get('PATH', 'flat_filed', fallback='flat_filed')
        n = self.get('PATH', 'flat_field_pe1c', fallback='flat_field_pe1c.tiff')
        return os.path.join(self.config_base, n_folder, n)
    
    @property
    def T_controller(self):
        return self.get('TEMPERATURE', 'temp_controller', fallback='No_temp_controller')
    
    @property
    def temperature(self):
        try:
            # temp_controller = self.get('TEMPERATURE', 'temp_controller', fallback='No_temp_controller')
            T = self.run.start['more_info'][self.T_controller]

        except (KeyError, IndexError, TypeError):
            T = 'None'

        return T


    @property
    def readable_time(self):
        t = _readable_time(self.run.start['time'])
        return f'{t[0]}-{t[1]}'
    
    @property
    def file_name_prefix(self):
        T = self.temperature

        if type(T) is float:
            return f'{self.sample_name}_{self.readable_time}_{self.full_uid:6.6}_{T}_K'

        else:
            return f'{self.sample_name}_{self.readable_time}_{self.full_uid:6.6}'


    @property
    def data_dir(self):
        return os.path.join(self.tiff_base, self.sample_name)


    @property
    def process_dir(self):
        if 'pilatus' in self.detector:
            return os.path.join(self.data_dir, f'{self.detector}')

        elif 'pe1c' in self.detector:
            return os.path.join(self.data_dir, f'{self.detectors}')

        elif 'pe2c' in self.detector:
            return os.path.join(self.data_dir, f'{self.detectors}')

        else:
            return os.path.join(self.data_dir, 'unkown_det')
        
    

    def acq_mode(self, PDF_limit=0.4, SAXS_limit=2.0, ):

        try:
            distance = self.run.start['calibration_md']['Distance']
            acq_mode = ''

            if distance < PDF_limit:
                acq_mode = 'PDF'

            elif (distance > PDF_limit) and (distance < SAXS_limit):
                acq_mode = 'XRD'

            elif distance > SAXS_limit:
                acq_mode = 'SAXS'

            else:
                acq_mode = 'Unknown'

        except KeyError:
            print('\nCannot find distance in metadata in start doc\n')
            acq_mode = 'NoDistance'

        return acq_mode


    def sum_pilatus(self):
        """ Assuming im2 offset by -osetx, -osety, and im3 offset by +osetx, +osety """
        
        # run = tiled_client[uid]
        my_im3 = getattr(self.run, self.stream_name[0]).read()['pilatus1_image'].to_numpy()[0][0]
        my_im2 = getattr(self.run, self.stream_name[1]).read()['pilatus1_image'].to_numpy()[0][0]
        my_im1 = getattr(self.run, self.stream_name[2]).read()['pilatus1_image'].to_numpy()[0][0]

        if self.use_flat_field_pila:
            flat_field = tifffile.imread(self.flat_field_pila)
            my_im3 = my_im3 / flat_field
            my_im2 = my_im2 / flat_field
            my_im1 = my_im1 / flat_field

        if self.acq_mode() == 'PDF':
            mask_dir = self.pilatus_PDF

        elif self.acq_mode() == 'XRD':
            mask_dir = self.pilatus_XRD

        else:
            mask_dir = self.pilatus_PDF

        # masks_pos_fn = ['Mask_pos1_ext_BS.npy', 'Mask_pos2_ext_BS.npy', 'Mask_pos3_ext_BS.npy']
        m1_path = os.path.join(mask_dir, self.masks_pos_flist[0])
        m2_path = os.path.join(mask_dir, self.masks_pos_flist[1])
        m3_path = os.path.join(mask_dir, self.masks_pos_flist[2])
        use_mask_1= np.load(m1_path)  # This is mask we are applying befor mergin images
        use_mask_2 = np.load(m2_path) # This is mask we are applying befor mergin images
        use_mask_3 = np.load(m3_path) # This is mask we are applying befor mergin images

        my_imsum = np.ones((my_im1.shape[0]+int(2*self.osetx), my_im2.shape[1]+int(2*self.osety),3))*np.nan

        my_imsum[self.osetx:-self.osetx,self.osety:-self.osety,0] = my_im1
        my_imsum[self.osetx:-self.osetx,self.osety:-self.osety,0][use_mask_1==1] = np.nan

        my_imsum[:-int(2*self.osetx),:-int(2*self.osety):,1] = my_im2
        my_imsum[:-int(2*self.osetx),:-int(2*self.osety):,1][use_mask_2==1] = np.nan

        my_imsum[int(2*self.osetx):,int(2*self.osety):,2] = my_im3
        my_imsum[int(2*self.osetx):,int(2*self.osety):,2][use_mask_3==1] = np.nan
        
        return np.nanmean(my_imsum, axis=2, dtype=np.float32)



    def save_img_pilatus(self):

        self.process_img = self.sum_pilatus()
        
        os.makedirs(self.process_dir, exist_ok=True)  # Create process_dir directory if it doesn't exis

        tiff_fn = os.path.join(self.process_dir, f'{self.file_name_prefix}_sum.tiff')
        tifffile.imsave(tiff_fn, self.process_img)
        print(f'\n*** {os.path.basename(tiff_fn)} saved!! ***\n')

        return self.process_img
    

    def save_img_perkin(self):

        self.process_img = self.sandbox_tiled[self.dksub_uid].read()
        
        if self.use_flat_field_pe1c or self.use_flat_field_pe2c:
            flat_field = tifffile.imread(self.flat_field_pe1c)
            self.process_img = self.process_img / flat_field

        os.makedirs(self.process_dir, exist_ok=True)  # Create process_dir directory if it doesn't exis
        
        if (self.use_flat_field_pe1c) and ('pe1c' in self.detector):
            tiff_fn = os.path.join(self.process_dir, f'{self.file_name_prefix}_flat.tiff')
        
        elif (self.use_flat_field_pe2c) and ('pe2c' in self.detector):
            tiff_fn = os.path.join(self.process_dir, f'{self.file_name_prefix}_flat.tiff')
        
        else:
            tiff_fn = os.path.join(self.process_dir, f'{self.file_name_prefix}_sub.tiff')
        
        tifffile.imsave(tiff_fn, self.process_img)
        print(f'\n*** {os.path.basename(tiff_fn)} saved!! ***\n')

        return self.process_img

        
