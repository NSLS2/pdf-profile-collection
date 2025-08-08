import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import scipy
from scipy import integrate
from scipy.optimize import minimize, NonlinearConstraint



class kafka_log():

    def __init__(self):
        self.colo_str = ''



def random_color(previous_color=None):

    color_list = ['tab:blue', 'tab:orange', 'tab:green', 
                    'tab:red', 'tab:purple', 'tab:brown', 
                    'tab:pink', 'tab:gray', 'tab:olive', 
                    'tab:cyan', 
    ]

    random_int = np.random.randint(len(color_list))
    new_color = color_list[random_int]

    is_str = type(previous_color) is str 
    in_color_list = previous_color in color_list

    if is_str and in_color_list:
        while new_color == previous_color:
            random_int = np.random.randint(len(color_list))
            new_color = color_list[random_int]
        return new_color
        
    return new_color



def get_HeaderRows(fn, sep=' ', num_data_column=2, check_range=100, check_float=True):

    cont_01 = []
    with open(fn, 'r') as f:
        cont = f.readlines()
        f.close()
    
    for line in cont:
        new_line = line.strip('\n').split(sep)
        cont_01.append(new_line)

    i = 0
    while i < len(cont_01):
        c0 = (len(cont_01[i]) == num_data_column)
        c1 = all([len(l)==num_data_column for l in cont_01[i:i+check_range]])
        c2 = (is_float(cont_01[i][0]) and is_float(cont_01[i][1]))

        if check_float:
            if c0 and c1 and c2:
                # print(f'Num of rows of header is {i}.')
                break
        else:
            if c0 and c1:
                # print(f'Num of rows of header is {i}.')
                break
            
        i += 1

    return i



def is_float(s):    
    """
    Checks if a string can be successfully converted to a float.
    
    Args:
    s: The string to check.
    
    Returns:
    True if the string can be converted to a float, False otherwise.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False



class auto_bkg():
    
    def __init__(self):       
        self.data_fn = None
        self.bkg_fn = None
        self.bkg_scale = 1.0
        self.data_df = None
        self.bkg_df = None
        self.bkg_opt = None
        self.min_res = None

    
    def pdload_data(self, data_fn, **kwargs):
        self.data_fn = data_df
        data_df = pd.read_csv(data_fn, **kwargs)
        self.data_df = data_df
        return data_df


    def pdload_bkg(self, bkg_fn, **kwargs):
        self.bkg_fn = bkg_fn
        bkg_df = pd.read_csv(bkg_fn, **kwargs)
        self.bkg_df = bkg_df
        return bkg_df
        

    def data_sub(self, scale):
        return self.data_df.iloc[:,1] - scale*self.bkg_df.iloc[:,1]
    

    def data_sub2(self, scale):
        return self.data_df.iloc[:,1][:3000] - scale*self.bkg_df.iloc[:,1][:3000] - 0.01


    def guess_01(self, update_scale=True):
        bkg_max_val = self.bkg_df.iloc[:,1].max()
        bkg_max_idx = self.bkg_df.iloc[:,1].idxmax()

        data_cor_val = self.data_df.iloc[bkg_max_idx, 1]
        scale_01 = data_cor_val/bkg_max_val

        if update_scale:
            self.bkg_scale = scale_01
        
        return scale_01


    def integral_sub(self, scale):
        # return integrate.simpson(self.data_sub(scale))
        return integrate.simpson(self.data_sub2(scale))


    def min_integral(self):
        # Define a constraint where 0 <= x[0] + x[1] <= 1
        # nlc = NonlinearConstraint(self.data_sub, 0, 50)

        nlc = [{'type': 'ineq', 'fun': self.data_sub2} # 1 - x0^2 - x1 >= 0
              ]
        
        a0 = self.guess_01()
        
        result = minimize(self.integral_sub, 
                          [a0], 
                          method='COBYLA', 
                          constraints=nlc, 
                          tol=1e-7, 
                          # options={'verbose': 3, 
                          #          'barrier_tol':1e-5, 
                          #          'maxiter': 1000, }
                         )
            
        self.min_res = result

        if result.success:
            print('Found the bkg scale to minimize the integral')
            self.bkg_opt = result.x

        else:
            print('Unable to Found the bkg scale')

        return result


    def plot_sub(self):

        fig, ax = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)

        ax[0].plot(self.data_df.iloc[:,0], self.data_df.iloc[:,1], label='data')
        
        try:
            ax[0].plot(self.bkg_df.iloc[:,0], self.bkg_df.iloc[:,1]*self.bkg_opt, 'g.', label='scaled_bkg', )
            ax[1].plot(self.data_df.iloc[:,0], self.data_sub(self.bkg_opt), label='data_sub')
        
        except TypeError:
            ax[0].plot(self.bkg_df.iloc[:,0], self.bkg_df.iloc[:,1]*self.guess_01(), 'r.', label='scaled_bkg', )
            ax[1].plot(self.data_df.iloc[:,0], self.data_sub(self.guess_01()), label='data_sub')

        ax[0].legend()
        ax[1].legend()
        
        

        


    