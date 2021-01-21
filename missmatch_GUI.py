# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 10:13:05 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import numpy as np
import GUI_function_working as gf
import glob
import os

path_behaviour = '//equipe2-nas1/F.LARENO-FACCINI/BACKUP FEDE/Behaviour/Group 14/6402 (CM16-Buz - Male)/Random Delay/P16'
condition = 'No Stim'

wheel_path = glob.glob(os.path.join(path_behaviour, '*.coder'))
wheel_predata = B.load_lickfile(wheel_path[0], wheel=True)
_, wheel_data = gf.wheel_speed(wheel_predata, condition_type=condition)


wheel_data_list = []
for key, value in wheel_data.items():
    wheel_data_list.append(len(value[:,1]))
    
    
