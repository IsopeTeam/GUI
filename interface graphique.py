# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:43:25 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import numpy as np
import wheel_speed as ws
import glob
import os

def plot_maker(lick_data, title, reward_time, raster, PSTH, wheel, wheel_data):
    
    plot_nb = int(raster)+int(PSTH)+int(wheel)
    """
    I didn't manage to find a way to properly display only one graphe, plot_nb = 2 alow to at least display 
    the graph even if a second empty graph is created
    """
    if plot_nb == 1:
        plot_nb=2
    fig, ax = plt.subplots(plot_nb, 1, sharex=True)
    fig.suptitle(title,weight='bold') #main figure title
    plot_position = 0

    if raster:
        #first subplot (Raster)
        B.scatter_lick(lick_data, ax[plot_position], x_label=None)
        ax[plot_position].set_title('RASTER') #Raster subplot title
        plot_position +=1
    
    if PSTH:
        #second subplot (PSTH)
        B.psth_lick(lick_data, ax[plot_position]) #PSTH graph 
        ax[plot_position].set_ylabel('nb of occurence') #PSTH title
        ax[plot_position].set_title('PSTH') #PSTH y label
        plot_position +=1
    
    if wheel:
        #third subplot (wheel speed)
        ax[plot_position].plot(wheel_data[:,0], wheel_data[:,1])
        ax[plot_position].set_ylabel('Wheel speed (cm/s)') #PSTH title
        ax[plot_position].set_title('Wheel speed') #PSTH y label
        
    
    ax[plot_nb-1].set_xlabel('Time (s)') #PSTH x label 
        
    current_reward_time=2.05+(float(reward_time)/1000) #determine when the reward happen depending of the keys of the dictionary
    ax = ax.ravel()
    for subplot in ax:
        subplot.axvspan(0,0.5, facecolor="green", alpha=0.3)
        subplot.axvspan(1.5,2, facecolor="green", alpha=0.3)
        subplot.axvspan(current_reward_time,current_reward_time+0.15, facecolor="red", alpha=0.3)

def graphique_fixe(lick_file_path, raster, PSTH, wheel, wheel_path):
    if raster or PSTH:
        lick_data = B.load_lickfile(lick_file_path)
    else:
        lick_data = None
    if wheel:
        wheel_predata = B.load_lickfile(wheel_path, wheel=True)
        wheel_data = ws.wheel_speed(wheel_predata)
    else:
        wheel_data = None
    plot_maker(lick_data, 'Fixe delay', 500, raster, PSTH, wheel, wheel_data)

def graphique_random(param_file_path, lick_file_path, dic_graph_choice, raster, PSTH, wheel, wheel_path):
        
    random_delay=B.extract_random_delay(param_file_path)
    
    if wheel:
        wheel_predata = B.load_lickfile(wheel_path, wheel=True)
        delays, wheel_by_delay = B.separate_by_delay(random_delay, wheel_predata)
    else:
        wheel_data=None

    if raster or PSTH:
        lick = B.load_lickfile(lick_file_path)
        delays, licks_by_delay = B.separate_by_delay(random_delay, lick)
    else:
        lick_data = None
        
    for cle in delays.keys():
        if dic_graph_choice[cle]:     
            
            if wheel:
                wheel_data = ws.wheel_speed(wheel_by_delay[cle])

            if raster or PSTH:
                lick_data = licks_by_delay[cle]
                
            plot_maker(lick_data, cle, cle[-3:], raster, PSTH, wheel, wheel_data)

        else:
            pass

        
sg.theme('DarkBlue')	

layout= [  [sg.Text('Enter .lick File name     '), sg.InputText(), sg.FolderBrowse()],[sg.Button('Load folder', key='-load-')],
            [sg.Radio('Random delay', 'radio_delay', key='radio_random', default=True), sg.Radio('fixe delay', 'radio_delay', key='radio_fixe')],
            [sg.Frame(layout=[      
            [sg.Checkbox('400', default=True, key='400'), sg.Checkbox('400_400', default=True, key='400_400'), \
            sg.Checkbox('900_400', default=True, key='900_400'), sg.Checkbox('400_400_400', default=True, key='400_400_400'), \
            sg.Checkbox('900_400_400', default=True, key='900_400_400')],[sg.Checkbox('900', default=True, key='900'), \
            sg.Checkbox('900_900', default=True, key='900_900'), sg.Checkbox('400_900', default=True, key='400_900'), sg.Checkbox('900_900_900', default=True, key='900_900_900'), \
            sg.Checkbox('400_900_900', default=True, key='400_900_900')]], title='trial to display',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')],  
            [sg.Frame(layout=[      
            [sg.Checkbox('Raster', default=True, key='display_raster'), sg.Checkbox('PSTH', default=True,key='display_PSTH'), \
            sg.Checkbox('Wheel speed', default=True, key='display_wheel')]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')],
            [sg.Button('Display plot', key='-plot-')]]

                                                      
window= sg.Window('Load files', layout, location=(0,0))

while True:
    event, values = window.read()

    try:
        if event in (None, 'Close'):	# if user closes window or clicks cancel
            break
        if event == '-load-':
            lick_path=glob.glob(os.path.join(values[0], '*.lick'))
            param_path=glob.glob(os.path.join(values[0], '*.param'))
            coder_path=glob.glob(os.path.join(values[0], '*.coder'))
            if len(lick_path)==0:
                sg.popup_error('no .lick file found')
            if len(lick_path)>1:
                sg.popup_error('more than one .lick file found')
                
            if len(param_path)==0:
                sg.popup_error('no .param file found')
            if len(param_path)>1:
                sg.popup_error('more than one .param file found')
                
            if len(coder_path)==0:
                sg.popup_error('no .coder file found')
            if len(coder_path)>1:
                sg.popup_error('more than one .coder file found')
            
            lick_path = os.path.normpath(lick_path[0])
            param_path = os.path.normpath(param_path[0])
            coder_path = os.path.normpath(coder_path[0])

            
        if event == '-plot-': 
            if values['radio_random']:   #If we chose to random delay
                dic_graph_choice = {"400":values['400'],"400_400":values['400_400'],"900_400":values['400_400'],\
                                                "400_400_400":values['400_400_400'],"900_400_400":values['900_400_400'],"900":values['900'],\
                                                "900_900":values['900_900'],"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
                graphique_random(param_path, lick_path, dic_graph_choice, \
                                 values['display_raster'],values['display_PSTH'], values['display_wheel'], coder_path)

  
    
            if values['radio_fixe']:   #if we chose fixe delay
                graphique_fixe(lick_path, values['display_raster'],values['display_PSTH'], values['display_wheel'], coder_path)
                 
        
    except:
        pass
    
window.close()

    