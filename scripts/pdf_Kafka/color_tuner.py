import os, glob
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider, Button, TextBox
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


class color_tuner():
    
    def __init__(self, fig, img, aspect='auto', q_array=None, histogram=True):
    
        self.fig = fig
        # self.ax = fig.gca()
        # self.ax = self.fig.add_axes([0.1, 0.1, 0.7, 0.8])
        self.img = img
        self.vmax = np.round(np.nanpercentile(img, 98), decimals=2)
        self.slider_max = self.vmax+500
        self.vmin = np.round(np.nanpercentile(img, 10), decimals=2)
        self.slider_min = self.vmin-500
        self.histogram = histogram
        self.aspect = aspect

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


        if self.histogram:
            self.ax = self.fig.add_subplot(1,2,1)
            self.im = is_q_space(q_array, img, self.ax, self.vmax, self.vmin, self.aspect)
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = fig.colorbar(self.im, cax=cax, location='top')
            vm_button_left = 0.02

            self.ax_ = self.fig.add_subplot(1,2,2)
            self.ax_.hist(img.flatten(), bins=1000, log=True, histtype='stepfilled')
            self.ax_.set_title('Histogram of pixel intensities')
            self.fig.subplots_adjust(left=0.1, right=0.95)

        else:
            self.ax = self.fig.add_subplot(1,1,1)
            # self.ax = fig.gca()
            self.im = is_q_space(q_array, img, self.ax, self.vmax, self.vmin, self.aspect)
            # self.cbar = fig.colorbar(self.im, location='top')
            ax_divider = make_axes_locatable(self.ax)
            cax = ax_divider.append_axes("top", size="5%", pad="3%")
            self.cbar = fig.colorbar(self.im, cax=cax, location='top')
            vm_button_left = 0.02
        
        ## Create the RangeSlider
        self.fig.subplots_adjust(bottom=0.1)
        self.slider_ax = plt.axes([0.15, 0.01, 0.65, 0.03])
        self.slider = RangeSlider(self.slider_ax, "color_scale", self.slider_min, self.slider_max)


        ## Add vertical lines in histogram
        if self.histogram:
            self.lower_limit_line = self.ax_.axvline(self.slider.val[0], color='r')
            self.upper_limit_line = self.ax_.axvline(self.slider.val[1], color='r')


        ## Creat buttons
        self.axplus = self.fig.add_axes([vm_button_left, 0.9, 0.04, 0.05])
        self.axminus = self.fig.add_axes([vm_button_left, 0.8, 0.04, 0.05])
        self.bplus = Button(self.axplus, 'M+')
        self.bminus = Button(self.axminus, 'M -')

        self.axplus1 = self.fig.add_axes([vm_button_left, 0.7, 0.04, 0.05])
        self.axminus1 = self.fig.add_axes([vm_button_left, 0.6, 0.04, 0.05])
        self.bplus1 = Button(self.axplus1, 'm+')
        self.bminus1 = Button(self.axminus1, 'm -')


        ## Create text boxes
        self.axbox = self.fig.add_axes([vm_button_left+0.01, 0.5, 0.04, 0.05])
        self.axbox1 = self.fig.add_axes([vm_button_left+0.01, 0.4, 0.04, 0.05])
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
            # self.lower_limit_line.set_xdata([val[0], val[0]])
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
            # self.upper_limit_line.set_xdata([val[1], val[1]])
        
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
            # self.upper_limit_line.set_xdata([val[1], val[1]])
        
        self.slider.on_changed(self.update)
        

    def submit_VM(self, expression):
        self.slider_max = float(expression)
        self.im.norm.vmax = self.slider_max
        self.readd_slider()
        
        val = [self.im.norm.vmin, self.slider_max]
        self.slider.set_val(val)

        ## Update the position of the vertical lines
        if self.histogram:
            # self.lower_limit_line.set_xdata([val[0], val[0]])
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
            # self.upper_limit_line.set_xdata([val[1], val[1]])
        
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


        