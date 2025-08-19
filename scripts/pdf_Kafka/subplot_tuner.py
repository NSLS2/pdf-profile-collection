import os, glob
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider, Button, TextBox, Slider
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib.gridspec import GridSpec

import importlib
# color_tuner = importlib.import_module("color_tuner").color_tuner
bin_ndarray = importlib.import_module("kafka_uti").bin_ndarray
get_HeaderRows = importlib.import_module("kafka_uti").get_HeaderRows
data_to_numpy = importlib.import_module("kafka_uti").data_to_numpy
find_nearest = importlib.import_module("kafka_uti").find_nearest
circle_coords = importlib.import_module("kafka_uti").circle_coords
q_to_azim = importlib.import_module("kafka_uti").q_to_azim

import pyFAI

class plot_tuner_base():
    
    def __init__(self, fig, img, aspect='auto'):
    
        self.fig = fig
        self.ax = None
        self.ax_ = None
        self.img = img
        self.vmax = np.round(np.nanpercentile(img, 98), decimals=2)
        self.slider_max = self.vmax+500
        self.vmin = np.round(np.nanpercentile(img, 10), decimals=2)
        self.slider_min = self.vmin-500
        self.aspect = aspect

        self.histogram = False

        
        ## Create the RangeSlider
        self.fig.subplots_adjust(bottom=0.1)
        self.slider_ax = plt.axes([0.15, 0.01, 0.65, 0.03])
        self.slider = RangeSlider(self.slider_ax, "color_scale", self.slider_min, self.slider_max)


        ## Creat buttons
        self.axplus = self.fig.add_axes([0.02, 0.9, 0.04, 0.05])
        self.axminus = self.fig.add_axes([0.02, 0.8, 0.04, 0.05])
        self.bplus = Button(self.axplus, 'M+')
        self.bminus = Button(self.axminus, 'M -')

        self.axplus1 = self.fig.add_axes([0.02, 0.7, 0.04, 0.05])
        self.axminus1 = self.fig.add_axes([0.02, 0.6, 0.04, 0.05])
        self.bplus1 = Button(self.axplus1, 'm+')
        self.bminus1 = Button(self.axminus1, 'm -')


        ## Create text boxes
        self.axbox = self.fig.add_axes([0.02+0.01, 0.5, 0.04, 0.05])
        self.axbox1 = self.fig.add_axes([0.02+0.01, 0.4, 0.04, 0.05])
        self.tbox = TextBox(self.axbox, ' VM ')
        self.tbox1 = TextBox(self.axbox1, ' vm ')     


    
    ## Re-add the RangeSlider
    def readd_slider(self):
        self.slider_ax.remove()
        self.slider_ax = plt.axes([0.15, 0.01, 0.65, 0.03])
        self.slider = RangeSlider(self.slider_ax, "color_scale", self.slider_min, self.slider_max)


    ## Re-add vertical lines in histogram
    def readd_vline(self, mpl_line, val):
        self.mpl_line.remove()
        self.mpl_line = self.ax_.axvline(val, color='r')

    
    def update(self, val):
        ## The val passed to a callback by the RangeSlider will
        ## be a tuple of (min, max)
    
        ## Update the image's colormap
        self.im.norm.vmin = val[0]
        self.im.norm.vmax = val[1]

        ## Update the position of the vertical lines
        if self.histogram:
            self.lower_limit_line.set_xdata([val[0], val[0]])
            self.upper_limit_line.set_xdata([val[1], val[1]])
    
        ## Redraw the figure to ensure it updates
        self.fig.canvas.draw_idle()


    def vmax_plus(self, event):
        self.slider_max += 100
        self.im.norm.vmax = self.slider_max
        self.readd_slider()

        val = [self.im.norm.vmin, self.slider_max]
        self.slider.set_val(val)
        ## Update the position of the vertical lines
        if self.histogram:
            self.upper_limit_line.set_xdata([val[1], val[1]])
 
        self.slider.on_changed(self.update)

    
    def vmax_minus(self, event):
        self.slider_max -= 100
        self.im.norm.vmax = self.slider_max
        self.readd_slider()

        val = [self.im.norm.vmin, self.slider_max]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            # self.lower_limit_line.set_xdata([val[0], val[0]])
            self.upper_limit_line.set_xdata([val[1], val[1]])
        
        self.slider.on_changed(self.update)


    def vmin_plus(self, event):
        self.slider_min += 100
        self.im.norm.vmin = self.slider_min
        self.readd_slider()

        val = [self.slider_min, self.im.norm.vmax]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            self.lower_limit_line.set_xdata([val[0], val[0]])
        
        self.slider.on_changed(self.update)

    
    def vmin_minus(self, event):
        self.slider_min -= 100
        self.im.norm.vmin = self.slider_min
        self.readd_slider()

        val = [self.slider_min, self.im.norm.vmax]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            self.lower_limit_line.set_xdata([val[0], val[0]])
        
        self.slider.on_changed(self.update)
        

    def submit_VM(self, expression):
        self.slider_max = float(expression)
        self.im.norm.vmax = self.slider_max
        self.readd_slider()
        
        val = [self.im.norm.vmin, self.slider_max]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            self.upper_limit_line.set_xdata([val[1], val[1]])
        
        self.slider.on_changed(self.update)


    def submit_vm(self, expression):
        self.slider_min = float(expression)
        self.im.norm.vmin = self.slider_min
        self.readd_slider()

        val = [self.slider_min, self.im.norm.vmax]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            self.lower_limit_line.set_xdata([val[0], val[0]])
        
        self.slider.on_changed(self.update)


    def __call__(self):

        self.bplus.on_clicked(self.vmax_plus)
        self.bminus.on_clicked(self.vmax_minus)

        self.bplus1.on_clicked(self.vmin_plus)
        self.bminus1.on_clicked(self.vmin_minus)

        self.tbox.on_submit(self.submit_VM)
        self.tbox.set_val(self.im.norm.vmax)
        self.tbox1.on_submit(self.submit_vm)
        self.tbox1.set_val(self.im.norm.vmin)

        self.slider.on_changed(self.update)


## Transform the x-axis of i2d which was obtained from pyFai 
## into q space and plot it by ax.pcolormesh
def is_q_space(q_array, img, ax, vmax, vmin, aspect):
    if q_array is None:
        im = ax.imshow(img, vmax=vmax, vmin=vmin)

    else:
        x_mesh = np.asarray(q_array)
        y_mesh = np.arange(img.shape[0])
        im = ax.pcolormesh(x_mesh, y_mesh, img, vmax=vmax, vmin=vmin)
        ax.invert_yaxis()

    if aspect is not None:
        ax.set_aspect(aspect)

    ax.set_xticks([])
    ax.set_yticks([])
    
    return im





## Extended class of plot_tuner_base (aka color_tuner). Specifically for subplot
class histogram_tuner(plot_tuner_base):

    def __init__(self, 
                *args, 
                q_array=None, 
                histogram=True, 
                **kwargs):
        
        super().__init__(*args, **kwargs)
        
        if q_array is None:
            self.q_array = q_array
        else:
            self.q_array = np.asarray(q_array)
        
        self.histogram = histogram
        # self.data = data_to_numpy(data, sep=sep)

        gs = GridSpec(nrows=1, ncols=2, width_ratios=[1., 1.])

        if self.histogram:
            gs.set_width_ratios([1.4, 1.])
            self.ax = self.fig.add_subplot(gs[0,0])
            self.im = is_q_space(self.q_array, self.img, self.ax, self.vmax, self.vmin, self.aspect)
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = self.fig.colorbar(self.im, cax=cax, location='top')

            self.ax_ = self.fig.add_subplot(gs[0,1])
            self.ax_.hist(self.img.flatten(), bins=1000, log=True, histtype='stepfilled')
            self.ax_.set_title('Histogram of pixel intensities')
            self.fig.subplots_adjust(left=0.1, right=0.95)

            ## Add vertical lines in histogram
            self.lower_limit_line = self.ax_.axvline(self.slider.val[0], color='r')
            self.upper_limit_line = self.ax_.axvline(self.slider.val[1], color='r')

        else:
            self.ax = self.fig.add_subplot(1,1,1)
            self.im = is_q_space(self.q_array, self.img, self.ax, self.vmax, self.vmin, self.aspect)
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = self.fig.colorbar(self.im, cax=cax, location='top')



    def __call__(self):
        super().__call__()






## Extended class of plot_tuner_base (aka color_tuner). Specifically for subplot
class data_tuner(plot_tuner_base):

    def __init__(self, 
                *args, 
                q_array=None, 
                data=None, 
                sample_name='', 
                color_str='tab:blue', 
                sep=' ', 
                pyfai_split=False, 
                poni_fn = '', 
                **kwargs):
        
        super().__init__(*args, **kwargs)
        
        if q_array is None:
            self.q_array = q_array
        else:
            self.q_array = np.asarray(q_array)
        
        self.data = data_to_numpy(data, sep=sep)
        self.sample_name = sample_name
        self.color_str = color_str
        self.pyfai_split = pyfai_split

        if (not self.pyfai_split) and os.path.exists(poni_fn):
            self.ai = pyFAI.load(poni_fn)
            self.center_y = self.ai.getFit2D()['centerY']
            self.center_x = self.ai.getFit2D()['centerX']


        gs = GridSpec(nrows=1, ncols=2, width_ratios=[1., 1.])

        if (self.data is not None):
            self.histogram = False  ## When there is iq data, no plotting histogram
            gs.set_width_ratios([1.4, 1.])
            ## plot img array
            self.ax = self.fig.add_subplot(gs[0,0])
            self.im = is_q_space(self.q_array, self.img, self.ax, self.vmax, self.vmin, self.aspect)
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = self.fig.colorbar(self.im, cax=cax, location='top')

            ## plot data (iq) in the right column
            self.ax_ = self.fig.add_subplot(gs[0,1])
            self.ax_.plot(self.data[0], self.data[1], label=self.sample_name, color=self.color_str)
            # self.ax_.set_title('Histogram of pixel intensities')
            self.fig.subplots_adjust(left=0.1, right=0.95, )

            ## Add slider
            self.q_binned = bin_ndarray(self.data[0], new_shape=(self.img.shape[1],))
            self.fig.subplots_adjust(bottom=0.15)
            self.slider_ax_ = plt.axes([0.15, 0.05, 0.65, 0.03])
            self.slider_iq = Slider(self.slider_ax_, "q_range", self.q_binned[0]-1, self.q_binned[-1]+1)

            ## Add vertical line in data
            self.q_line_1d = self.ax_.axvline(self.slider_iq.val, color='r')

            ## Add circle in 2d img
            if self.pyfai_split:
                gs.set_width_ratios([2., 1.])
                self.q_line_2d = self.ax.axvline(x=1, color='r')
            else:
                circle = circle_coords(center=[self.center_x, self.center_y], radius=50)
                self.q_line_2d, = self.ax.plot(circle[0], circle[1], color='r')  # The comma unpacks the list

            # self.q_line_2d = self.ax.axvline(self.slider_iq.val, color='r')

            ## Creat buttons
            self.axqplus = self.fig.add_axes([0.9, 0.03, 0.04, 0.05])
            self.axqminus = self.fig.add_axes([0.02, 0.03, 0.04, 0.05])
            self.bqplus = Button(self.axqplus, 'q+')
            self.bqminus = Button(self.axqminus, 'q -')


        else:
            self.ax = self.fig.add_subplot(1,1,1)
            self.im = is_q_space(self.q_array, self.img, self.ax, self.vmax, self.vmin, self.aspect)
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = self.fig.colorbar(self.im, cax=cax, location='top')



    def q_to_r(self):
        azim = q_to_azim(self.slider_iq.val, self.ai.wavelength)
        r = self.ai.dist*np.tan(azim)
        return r/self.ai.pixel1

    
    def update_iq(self, val):
        ## The val passed to a callback by the RangeSlider will
        ## be a tuple of (min, max)
    
        self.q_line_1d.set_xdata([val, val])

        idx, _ = find_nearest(self.q_binned, val)

        if self.pyfai_split:
            self.q_line_2d.set_xdata([idx, idx])
        else:
            circle = circle_coords(center=[self.center_x, self.center_y], radius=self.q_to_r())
            self.q_line_2d.set_data(circle[0], circle[1])
        
        ## Redraw the figure to ensure it updates
        self.fig.canvas.draw_idle()

    
    
    def q_plus(self, event):
        val = self.slider_iq.val + 0.002
        self.slider_iq.set_val(val)

        self.q_line_1d.set_xdata([val, val])

        idx, _ = find_nearest(self.q_binned, val)

        if self.pyfai_split:
            self.q_line_2d.set_xdata([idx, idx])
        else:
            circle = circle_coords(center=[self.center_x, self.center_y], radius=self.q_to_r())
            self.q_line_2d.set_data(circle[0], circle[1])
 
        self.slider_iq.on_changed(self.update_iq)


    def q_minus(self, event):
        val = self.slider_iq.val - 0.002
        self.slider_iq.set_val(val)

        self.q_line_1d.set_xdata([val, val])

        idx, _ = find_nearest(self.q_binned, val)

        if self.pyfai_split:
            self.q_line_2d.set_xdata([idx, idx])
        else:
            circle = circle_coords(center=[self.center_x, self.center_y], radius=self.q_to_r())
            self.q_line_2d.set_data(circle[0], circle[1])
 
        self.slider_iq.on_changed(self.update_iq)



    def __call__(self):
        super().__call__()
        if self.data is not None:
            self.slider_iq.on_changed(self.update_iq)
            self.bqplus.on_clicked(self.q_plus)
            self.bqminus.on_clicked(self.q_minus)


