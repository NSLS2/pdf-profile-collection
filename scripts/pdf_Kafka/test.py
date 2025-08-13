import importlib
color_tuner = importlib.import_module("color_tuner").color_tuner

import os, glob
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt
from skimage import io
from matplotlib.widgets import RangeSlider

tiff = '/Users/cheng-hunglin/Documents/Data_LDRD/user_data_Bai_316861_1a802ea0_2025-08-08-0910/tiff_base/LDRD_chl/Ni_chl_PDF/average/Ni_chl_PDF_20250807_mean.tiff'
img = io.imread(tiff)
fig = plt.figure(figsize=(12, 6))
img_tuner2 = color_tuner(fig, img, histogram=True, aspect=None)
img_tuner2()
plt.show()


