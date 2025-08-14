import importlib
# color_tuner = importlib.import_module("color_tuner").color_tuner
subplot_tuner = importlib.import_module("subplot_tuner").subplot_tuner
# pct_integration = importlib.import_module("kafka_uti").pct_integration
bin_ndarray = importlib.import_module("kafka_uti").bin_ndarray

import os, glob
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt
from skimage import io
import pyFAI


def pct_integration(img_array, iq_fn, save=True):

    ## perform azimuthalintegration on one image to retain 2D information
    ## i2d.shape is (self.npt_azim, self.npt_rad) which corresponds the intensity of 2D image cake
    ## q1d.shape is (self.npt_rad, )
    i2d, q1d, chi1d = ai.integrate2d(img, npt_rad, 
                                     unit=UNIT, npt_azim=npt_azim, 
                                     polarization_factor=polarization, 
                                     method=('bbox', 'csr', 'cython'), 
                                     mask=mask0)
    
    ## trasnform mask0 (base mask) to the same coordinate space and cast it as type bool
    intrinsic_mask_unrolled, _, _ = ai.integrate2d(mask0, npt_rad, 
                                                   unit=UNIT, npt_azim=npt_azim, 
                                                   polarization_factor=polarization, 
                                                   mask=mask0)
    
    ## Create an array to hold outlier mask
    outlier_mask_2d = np.zeros_like(i2d)     
    mask1 = np.array(i2d<1)*1
    
    ## Apply percentile filter along radial direction (axis=0)
    for ii, dd in enumerate(i2d.T):
        low_limit, high_limit = np.percentile(dd, (low_limit_pcfilter, up_limit_pcfilter))
        outlier_mask_2d[:,ii] = np.any([dd<low_limit, dd>high_limit, intrinsic_mask_unrolled[:,ii]], axis=0)
    
    mask2 = outlier_mask_2d + mask1
    outlier_mask_2d_masked = ma.masked_array(i2d, mask=mask2)
    
    ## calculate mean values along radial direction (axis=0) to make i1d.shape is (self.npt_rad, )
    i1d = ma.mean(outlier_mask_2d_masked, axis=0)
    
    
    iq_df0 = pd.DataFrame()
    iq_df0['q'] = q1d
    iq_df0['I'] = i1d
    iq_df = iq_df0.dropna()

    if save:
        md = ai.getPyFAI()
        iq_saver(iq_fn, iq_df, md)
        print(f'\n*** {os.path.basename(iq_fn)} saved!! ***\n')

    return iq_df0, i2d, outlier_mask_2d_masked


npt_rad = 4096
npt_azim = 360*10
polarization = 0.99
UNIT = 'q_A^-1'
low_limit_pcfilter = 1
up_limit_pcfilter = 99

tiff = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/Measurement_CHL_MA/Ni_XRD_MA/dark_sub/Ni_XRD_MA_20250807-235014_741ec5_primary-dk_sub_image-00000.tiff'
iq_fn = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/Measurement_CHL_MA/Ni_XRD_MA/integration/Ni_XRD_MA_20250807-235014_741ec5_primary-1_mean_q.chi'
img = io.imread(tiff)

config_dir = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/config_base/'
poni_fn = os.path.join(config_dir, 'pe1c_XRD_MA', 'xpdAcq_calib_info.poni')
mask_fn = os.path.join(config_dir, 'pe1c_XRD_MA', 'Mask.npy')
ai = pyFAI.load(poni_fn)
mask0 = np.load(mask_fn)

iq_df0, i2d, outlier_mask_2d_masked = pct_integration(img, 'xx', save=False)
i2d_m = outlier_mask_2d_masked.filled(fill_value=np.nan)
bb = bin_ndarray(i2d_m)

fig0 = plt.figure(figsize=(12, 6))
# img_tuner0 = subplot_tuner(fig, bb, histogram=True, aspect=None)
img_tuner0 = subplot_tuner(fig0, bb, histogram=True, aspect='auto', data=iq_fn)
img_tuner0()

fig1 = plt.figure(figsize=(12, 6))
img_tuner1 = subplot_tuner(fig1, img, histogram=True, aspect=None, data=None)
img_tuner1()

fig2 = plt.figure(figsize=(12, 6))
img_tuner2 = subplot_tuner(fig2, img, histogram=False, aspect=None, data=iq_fn)
img_tuner2()

plt.show()


