import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import numpy.ma as ma
import os

import importlib
get_HeaderRows = importlib.import_module("kafka_uti").get_HeaderRows
random_color = importlib.import_module("kafka_uti").random_color
color_tuner = importlib.import_module("color_tuner").color_tuner
bin_ndarray = importlib.import_module("kafka_uti").bin_ndarray
# Pilatus_getpdf = importlib.import_module("pilatus_getpdf_v2.2").Pilatus_Int

class open_figures():
    def __init__(self, figure_labels):
        for i in figure_labels:
            plt.figure(num=i, figsize=(8,6))


class plot_pilatus(open_figures):
    
    def __init__(self, sample_name, 
                 figure_labels = ['tiff & Histogram', 'I(Q)', 'S(Q)', 'f(Q)', 'g(r)', ], 
                 color_str = '',
                ):
        self.fig = figure_labels
        # self.uid = metadata_dic['uid']
        self.sample_name = sample_name
        # self.fontsize = 14
        self.labelsize = 14
        self.legend_prop = {'weight':'regular', 'size':14}
        self.title_prop = {'weight':'regular', 'size':12}
        self.xylabel_prop = {'weight':'regular', 'size':16}
        self.color_str = random_color(previous_color=color_str)
        self.spine_width = 2
        # self.date, self.time = _readable_time(metadata_dic['time'])
        super().__init__(figure_labels)


    def plot_tiff(self, img, title=None):
        
        try:
            f = plt.figure(self.fig[0])
        except (IndexError): 
            f = plt.figure(self.fig[-1])

        plt.clf()
        ax = f.gca()

        for spine in ax.spines.values():
            spine.set_linewidth(self.spine_width)

        vmax = np.nanpercentile(img, 98)
        # vmax = 10000
        if vmax==np.nan:
           vmax = 10000

        vmin = np.nanpercentile(img, 10)
        if vmin==np.nan:
           vmin = 0

        im = ax.imshow(img, label=self.sample_name, 
                       vmin=vmin, vmax=vmax)
        f.colorbar(im)

        if title != None:
            ax.set_title(title, prop=self.title_prop)
        else:
            pass

        ax.tick_params(axis='both', labelsize=self.labelsize)
        ax.legend(prop=self.legend_prop)

        f.canvas.manager.show()
        f.canvas.flush_events()



    def plot_tiff2(self, img, mask_img, title=None):
        
        try:
            f = plt.figure(self.fig[0])
        except (IndexError): 
            f = plt.figure(self.fig[-1])

        plt.clf()
        # ax = f.gca()
        ax1 = f.add_subplot(1, 2, 1)
        ax2 = f.add_subplot(1, 2, 2)

        mask_img = np.invert(mask_img.astype(bool))
        masked_img = img * mask_img
        masked_img[masked_img==0] = np.nan

        img_list = [img, masked_img]
        ax = [ax1, ax2]

        for i in range(len(ax)):

            for spine in ax[i].spines.values():
                spine.set_linewidth(self.spine_width)

            vmax = np.nanpercentile(img_list[i], 98)
            # vmax = 10000
            if vmax==np.nan:
                vmax = 10000

            vmin = np.nanpercentile(img_list[i], 10)
            if vmin==np.nan:
                vmin = 0

            im = ax[i].imshow(img_list[i], label=self.sample_name, 
                            vmin=vmin, vmax=vmax)
            

            f.colorbar(im, shrink=0.75)
            # f.colorbar(im2, shrink=0.5)

            if title != None:
                ax[i].set_title(title, prop=self.title_prop)
                # ax2.set_title(title, prop=self.title_prop)
            else:
                pass

            ax[i].tick_params(axis='both', labelsize=self.labelsize)
            ax[i].legend(prop=self.legend_prop)

            # ax2.tick_params(axis='both', labelsize=self.labelsize)
            # ax2.legend(prop=self.legend_prop)

        f.canvas.manager.show()
        f.canvas.flush_events()
        


    def plot_tiff3(self, img, mask_fn, title=None, mask=False, histogram=False, aspect=None):
        
        try:
            f = plt.figure(self.fig[0])
            # f = plt.figure('test')
        except (IndexError): 
            f = plt.figure(self.fig[-1])

        plt.clf()
        # ax = f.gca()

        # for spine in ax.spines.values():
        #     spine.set_linewidth(self.spine_width)

        mask1 = np.load(mask_fn)
        masked_ = ma.masked_array(img, mask=mask1)
        masked_img = masked_.filled(fill_value=np.nan)

        if mask:
            img_tuner = color_tuner(f, masked_img, histogram=histogram, aspect=aspect)
        else:
            img_tuner = color_tuner(f, img, histogram=histogram, aspect=aspect)

        # if title != None:
        #     ax.set_title(title, prop=self.title_prop)
        # else:
        #     pass

        # ax.tick_params(axis='both', labelsize=self.labelsize)
        # ax.legend(prop=self.legend_prop)

        f.canvas.manager.show()
        f.canvas.flush_events()

        return img_tuner




    def plot_tiff4(self, unrolled_array, q_array, title=None, binned=True, aspect='auto'):
        
        try:
            # f = plt.figure(self.fig[0])
            f = plt.figure('Unroll masked pct-filtered tiff', figsize=(8,6))
        except (IndexError): 
            f = plt.figure(self.fig[-1])

        plt.clf()
        # ax = f.gca()

        # for spine in ax.spines.values():
        #     spine.set_linewidth(self.spine_width)

        img = unrolled_array.filled(fill_value=np.nan)

        if binned:
            img = bin_ndarray(img)
        
        img_tuner = color_tuner(f, img, q_array=q_array, histogram=False, aspect=aspect)

        # if title != None:
        #     ax.set_title(title, prop=self.title_prop)
        # else:
        #     pass

        # ax.tick_params(axis='both', labelsize=self.labelsize)
        # ax.legend(prop=self.legend_prop)

        f.canvas.manager.show()
        f.canvas.flush_events()

        return img_tuner




        
    def plot_iq(self, iq_fn, skip_rows, title=None,):
        
        try: 
            f = plt.figure(self.fig[1])
        except (IndexError): 
            f = plt.figure(self.fig[-1])
        
        iq_df = pd.read_csv(iq_fn, names=['q', 'I(q)'], sep=' ', skiprows=skip_rows)

        plt.clf()
        ax = f.gca()

        for spine in ax.spines.values():
            spine.set_linewidth(self.spine_width)
        
        ax.plot(iq_df['q'], iq_df['I(q)'], label=self.sample_name, color=self.color_str)

        if title != None:
            ax.set_title(title, prop=self.title_prop)
        else:
            pass

        ax.set_xlabel('Q (A-1)', fontdict=self.xylabel_prop)
        ax.set_ylabel('I(Q)', fontdict=self.xylabel_prop)
        ax.legend(prop=self.legend_prop)

        f.canvas.manager.show()
        f.canvas.flush_events()
        


    # def plot_gr(self, gr_path, title=None):
        
    #     try: 
    #         f = plt.figure(self.fig[2])
    #     except (IndexError): 
    #         f = plt.figure(self.fig[-1])    # def plot_gr(self, gr_path, title=None):
        
    #     try: 
    #         f = plt.figure(self.fig[2])
    #     except (IndexError): 
    #         f = plt.figure(self.fig[-1])
        
    #     gr_df = pd.read_csv(gr_path, names=['r', 'g(r)'], sep=' ', skiprows=26)


    #     plt.clf()
    #     ax = f.gca()
    #     ax.plot(gr_df['r'], gr_df['g(r)'], label=self.sample_name)

    #     if title != None:
    #         ax.set_title(title, prop=self.title_prop)
    #     else:
    #         pass

    #     ax.set_xlabel('r (A)', fontdict=self.xylabel_prop)
    #     ax.set_ylabel('g(r)', fontdict=self.xylabel_prop)
    #     ax.legend(prop=self.legend_prop)

    #     f.canvas.manager.show()
    #     f.canvas.flush_events()
        
    #     gr_df = pd.read_csv(gr_path, names=['r', 'g(r)'], sep=' ', skiprows=26)


    #     plt.clf()
    #     ax = f.gca()
    #     ax.plot(gr_df['r'], gr_df['g(r)'], label=self.sample_name)

    #     if title != None:
    #         ax.set_title(title, prop=self.title_prop)
    #     else:
    #         pass

    #     ax.set_xlabel('r (A)', fontdict=self.xylabel_prop)
    #     ax.set_ylabel('g(r)', fontdict=self.xylabel_prop)
    #     ax.legend(prop=self.legend_prop)

    #     f.canvas.manager.show()
    #     f.canvas.flush_events()
        
        


    def plot_sqfqgr(self, sqfqgr_path, bkg_scale, bkg_fn, title=None):

        try: 
            f = plt.figure(self.fig[1])
        except (IndexError): 
            f = plt.figure(self.fig[-1])

        bkg_exist = os.path.exists(bkg_fn)
        if bkg_exist:
            rows = get_HeaderRows(bkg_fn, sep=' ', num_data_column=2, 
                        check_range=100, check_float=True)
            bkg_df = pd.read_csv(bkg_fn, names=['x', 'y'], sep=' ', skiprows=rows)
            
            ax = f.gca()
            ax.plot(bkg_df['x'], bkg_df['y']*bkg_scale, label='background', marker='.', color='green')
            ax.legend(prop=self.legend_prop)
        
        keys = ['sq', 'fq', 'gr']
        xlabel = ['q (A-1)', 'q (A-1)', 'r (A)']
        ylabel = ['S(q)', 'f(q)', 'g(r)']

        for i in range(len(sqfqgr_path)):

            try: 
                f = plt.figure(self.fig[i+2])
            except (IndexError): 
                f = plt.figure(self.fig[-1])
        
            rows = get_HeaderRows(sqfqgr_path[keys[i]], sep=' ', num_data_column=2, 
                        check_range=100, check_float=True)

            # df = pd.read_csv(sqfqgr_path[keys[i]], names=['x', 'y'], sep=' ', skiprows=27)
            df = pd.read_csv(sqfqgr_path[keys[i]], names=['x', 'y'], sep=' ', skiprows=rows)


            plt.clf()
            ax = f.gca()

            for spine in ax.spines.values():
                spine.set_linewidth(self.spine_width)
            
            ax.plot(df['x'], df['y'], label=self.sample_name, color=self.color_str)

            if title != None:
                ax.set_title(title, prop=self.title_prop)
            else:
                pass

            ax.set_xlabel(xlabel[i], fontdict=self.xylabel_prop)
            ax.set_ylabel(ylabel[i], fontdict=self.xylabel_prop)
            ax.legend(prop=self.legend_prop)

            f.canvas.manager.show()
            f.canvas.flush_events()
        

        

# class open_subfigures():
#     def __init__(self, rows, columns, figsize, ax_titles):
#         f1, ax1 = plt.subplots(rows, columns, figsize=figsize, constrained_layout=True)
#         ax1 = ax1.flatten()
#         for i in range(len(ax_titles)):
#             ax1[i].set_title(ax_titles[i], fontsize=10)
        
# class multipeak_fitting(open_subfigures):
#     def __init__(self, rows=2, columns=2, figsize = (8, 6), ax_titles=['_1gauss', '_2gauss', '_3gauss', 'r_2']):
#         super().__init__(rows, columns, figsize, ax_titles)
#         self.fig = plt.gcf()
#         self.ax = self.fig.get_axes()
        
#     def plot_fitting(self, x, y, popt_list, single_f, fill_between=True, num_var=3):
#         for i in range(len(popt_list)):
            
#             fitted_y = np.zeros([x.shape[0]])
#             for j in range(i+1):
#                 fitted_y += single_f(x, *popt_list[i][0+num_var*j:num_var+num_var*j])
            
#             self.ax[i].plot(x ,y, 'b+:',label='data')
#             r_2 = da.r_square(x, y, fitted_y, y_low_limit=500)
#             r2 = f'R\u00b2={r_2:.2f}'
#             self.ax[i].plot(x,fitted_y,'r--',label='Total fit\n'+r2)
            
#             if fill_between:
#                 f1 = single_f
#                 for k in range(int(len(popt_list[i])/3)):
#                     pars_k = popt_list[i][0+3*k:3+3*k]
#                     peak_k = f1(x, *pars_k)
#                     self.ax[i].plot(x, peak_k, label=f'peak {k+1}')
#                     self.ax[i].fill_between(x, peak_k.min(), peak_k, alpha=0.3)
            
#             self.ax[i].legend()
            

# def color_idx_map_halides(peak_wavelength, halide_w_range=[400, 520, 660]):
    
#     from matplotlib.colors import LinearSegmentedColormap
#     colors = [
#         # (0.25098039215686274, 0.0, 0.29411764705882354), 
#         (0.4627450980392157, 0.16470588235294117, 0.5137254901960784),
#         (0.3686274509803922, 0.30980392156862746, 0.6352941176470588), 
#         (0.19607843137254902, 0.5333333333333333, 0.7411764705882353), 
#         (0.4, 0.7607843137254902, 0.6470588235294118),
#      # (0.6705882352941176, 0.8666666666666667, 0.6431372549019608),
#      # (0.6509803921568628, 0.8509803921568627, 0.41568627450980394),
#      # (0.10196078431372549, 0.5882352941176471, 0.2549019607843137), 
#              ]
#     BlGn = LinearSegmentedColormap.from_list('BlGn', colors, N=100)


#     import palettable
#     palette2 = palettable.colorbrewer.diverging.RdYlGn_4_r
#     RdYlGn_4_r = palette2.mpl_colormap
    
#     if  peak_wavelength >= halide_w_range[0] and peak_wavelength < halide_w_range[1]:
#         wavelength_range=[halide_w_range[0], halide_w_range[1]]
#         cmap = BlGn
#     elif peak_wavelength >= halide_w_range[1] and peak_wavelength <= halide_w_range[2]:
#         wavelength_range=[halide_w_range[1], halide_w_range[2]]
#         cmap = RdYlGn_4_r
        
#     else:
#         raise ValueError(f'Peak at {peak_wavelength} nm is not in the range of {halide_w_range} nm.')
    
#     w1 = wavelength_range[0]  ## in nm
#     w2 = wavelength_range[1]  ## in nm
#     w_steps = abs(int(2*(w2-w1)))
#     w_array = np.linspace(w1, w2, w_steps)
#     color_array = np.linspace(0, 1, w_steps)
#     idx, _ = da.find_nearest(w_array, peak_wavelength)
#     # ax.plot(x, y, label=label, color=cmap(color_array[idx]))
    
#     color = cmap(color_array[idx])
    
#     return color