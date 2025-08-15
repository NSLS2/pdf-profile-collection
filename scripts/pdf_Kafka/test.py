import importlib
# color_tuner = importlib.import_module("color_tuner").color_tuner
histogram_tuner = importlib.import_module("subplot_tuner").histogram_tuner
data_tuner = importlib.import_module("subplot_tuner").data_tuner
# pct_integration = importlib.import_module("kafka_uti").pct_integration
bin_ndarray = importlib.import_module("kafka_uti").bin_ndarray

import os, glob
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt
from skimage import io
import pyFAI

import matplotlib
matplotlib.use('Qt5Agg') # Or 'TkAgg', 'notebook', etc.

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

tiff = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/LDRD_chl/Ni_chl_XRD/dark_sub/Ni_chl_XRD_20250807-180133_03bef8_primary-dk_sub_image-00000.tiff'
iq_fn = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/LDRD_chl/Ni_chl_XRD/Ni_chl_XRD_20250807-180133_03bef8_q.csv'
img = io.imread(tiff)
df = pd.read_csv(iq_fn, sep=';', names=['q', 'iq'], skiprows=1)

# tiff = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/LDRD_chl/Cs4PbBr6_No3_PDF/average/Cs4PbBr6_No3_PDF_20250807_mean.tiff'
# iq_fn = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/LDRD_chl/Cs4PbBr6_No3_PDF/average/Cs4PbBr6_No3_PDF_20250807_mean.iq'
# img = io.imread(tiff)

config_dir = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/config_base/'
poni_fn = os.path.join(config_dir, 'pe1c_XRD_chl', 'Ni_chl_XRD.poni')
mask_fn = os.path.join(config_dir, 'pe1c_XRD_chl', 'Mask2.npy')
# poni_fn = os.path.join(config_dir, 'pe1c_PDF_chl', 'xpdAcq_calib_info.poni')
# mask_fn = os.path.join(config_dir, 'pe1c_PDF_chl', 'Mask.npy')
ai = pyFAI.load(poni_fn)
mask0 = np.load(mask_fn)

iq_df0, i2d, outlier_mask_2d_masked = pct_integration(img, 'xx', save=False)
i2d_m = outlier_mask_2d_masked.filled(fill_value=np.nan)
bb = bin_ndarray(i2d_m)
sep=';'

fig0 = plt.figure(figsize=(12, 6))
# img_tuner0 = subplot_tuner(fig, bb, histogram=True, aspect=None)
img_tuner0 = histogram_tuner(fig0, bb, histogram=True, aspect='auto')
img_tuner0()

fig1 = plt.figure(figsize=(12, 6))
img_tuner1 = data_tuner(fig1, img, aspect=None, data=iq_df0, poni_fn=poni_fn)
img_tuner1()

fig2 = plt.figure(figsize=(12, 6))
img_tuner2 = data_tuner(fig2, bb, aspect='auto', data=iq_df0, poni_fn=poni_fn, pyfai_split=True)
img_tuner2()

# fig3 = plt.figure(figsize=(12, 6))
# img_tuner3 = data_tuner(fig3, bb, aspect='auto', pyfai_split=True)
# img_tuner3()

plt.show()


