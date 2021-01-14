# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:43:25 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import numpy as np
import GUI_function as gf
import glob
import os

def plot_maker(lick_data, title, reward_time, raster, PSTH, wheel, wheel_data):
    
    plot_nb = int(raster)+int(PSTH)+int(wheel)
    """
    I didn't manage to find a way to properly display only one graphe, plot_nb = 2 alow to at least display 
    the graph even if a second empty graph is created
    """
    fig, ax = plt.subplots(plot_nb, 1, sharex=True)
    fig.suptitle(title,weight='bold') #main figure title
    plot_position = 0
    if plot_nb==1:
        axes=ax
    elif plot_nb>1:
        axes=ax[plot_position]

    if raster:
        #first subplot (Raster)
        B.scatter_lick(lick_data, axes, x_label=None)
        axes.set_title('RASTER') #Raster subplot title
        plot_position +=1
    
    
    if PSTH:
        #second subplot (PSTH)
        if plot_nb >1:
            axes=ax[plot_position]
    
        #second subplot (PSTH)
        B.psth_lick(lick_data, axes) #PSTH graph 
        axes.set_ylabel('nb of occurence') #PSTH title
        axes.set_title('PSTH') #PSTH y label
        plot_position +=1
    
    if wheel:
        #second subplot (PSTH)
        if plot_nb >1:
            axes=ax[plot_position]
        #third subplot (wheel speed)
        axes.plot(wheel_data[:,0], wheel_data[:,1])
        axes.set_ylabel('Wheel speed (cm/s)') #PSTH title
        axes.set_title('Wheel speed') #PSTH y label
        
    
    axes.set_xlabel('Time (s)') #PSTH x label 
        
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
        wheel_data = gf.wheel_speed(wheel_predata)
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
                wheel_data = gf.wheel_speed(wheel_by_delay[cle])

            if raster or PSTH:
                lick_data = licks_by_delay[cle]
                
            plot_maker(lick_data, cle, cle[-3:], raster, PSTH, wheel, wheel_data)

        else:
            pass

        
sg.theme('DarkBlue')	


#column for time frequency plots
column1 = [[sg.Text('Chanel 0', justification='center', size=(10, 1))],          
            [sg.Checkbox('Amplitude', default=True,key='Ch_group0_amplitude')],
            [sg.Checkbox('Power', default=True, key='Ch_group0_power')]]      

column2 = [[sg.Text('Chanel 1', justification='center', size=(10, 1))],      
            [sg.Checkbox('Amplitude', default=True,key='Ch_group1_amplitude')],
            [sg.Checkbox('Power', default=True, key='Ch_group1_power')]]  



            #folder searching 
layout= [   [sg.Text('Select data folder     '), sg.InputText(), sg.FolderBrowse(key='main_folder'),sg.Button('Load folder', key='-load-')],
            [sg.Text('Select group       '), sg.InputCombo(values=[], size=(20, 1), key='group_nb', enable_events=True)],            
            [sg.Text('Select mice        '), sg.InputCombo(values=[], size=(20, 1), key='mice_nb', enable_events=True)],            
            [sg.Radio('Random delay', 'radio_delay', key='radio_random', default=True, enable_events=True), sg.Radio('fixe delay', 'radio_delay', key='radio_fixe', enable_events=True)],            
            [sg.Text('Select protocole   '), sg.InputCombo(values=[], size=(20, 1), key='protocole', enable_events=True)],
            [sg.Text('Select condition   '), sg.InputCombo(values=[], size=(20, 1), key='condition', enable_events=True)],
            #Behaviour
            [sg.Text('_'  * 80)], [sg.Text('Behaviour', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)], 
            [sg.Frame(layout=[      
            [sg.Checkbox('400', default=True, key='400'), sg.Checkbox('400_400', default=True, key='400_400'), \
            sg.Checkbox('900_400', default=True, key='900_400'), sg.Checkbox('400_400_400', default=True, key='400_400_400'), \
            sg.Checkbox('900_400_400', default=True, key='900_400_400')],[sg.Checkbox('900', default=True, key='900'), \
            sg.Checkbox('900_900', default=True, key='900_900'), sg.Checkbox('400_900', default=True, key='400_900'), sg.Checkbox('900_900_900', default=True, key='900_900_900'), \
            sg.Checkbox('400_900_900', default=True, key='400_900_900')]], title='trial to display (random delay only)',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')],  
            [sg.Frame(layout=[      
            [sg.Checkbox('Raster', default=True, key='display_raster'), sg.Checkbox('PSTH', default=True,key='display_PSTH'), \
            sg.Checkbox('Wheel speed', default=True, key='display_wheel')]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN)],
            [sg.Button('Display plot', key='-behaviour plot-')],
            #Electrophy
            [sg.Text('_'  * 80)], [sg.Text('Electrophysiology', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)],
                #whole session average
            [sg.Frame(layout=[[sg.Checkbox('Chanel 0', default=True, key='Ch_group0'), sg.Checkbox('Chanel 1', default=True,key='Ch_group1')]] \
            ,title='Whole session average (by shank)',title_color='red', relief=sg.RELIEF_SUNKEN),\
                #Time frequency
            sg.Frame(layout=[[sg.Column(column1),sg.Column(column2)]], title='Time Frequency (by shank)',title_color='red', relief=sg.RELIEF_SUNKEN)],
            [sg.Button('Display plot', key='-electrophy plot-')]  
            ]          
            

                                                      
window= sg.Window('', layout, location=(0,0))

#because the chekbox is setup on random delay at the opening of the window
group_nb = ''
mice_nb = ''
expermiment_type = 'Random Delay'
protocol_type = ''
conditon_type = ''
while True:
    event, values = window.read()

    try:
        if event in (None, 'Close'):	# if user closes window or clicks cancel
            break
    
    #File sorting
        if event == '-load-':
                
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)

            group = path_dic["list_group"]
            #group.insert(0, 'all')
            window.FindElement('group_nb').Update(values=group)
            
            mice = path_dic["list_mice"]
            #mice.insert(0, 'all')
            window.FindElement('mice_nb').Update(values=mice)
            
            protocol = path_dic["list_protocol"]
            #protocol.insert(0, 'all')
            window.FindElement('protocole').Update(values=protocol)
            
            condition = path_dic["list_condition"]
            #mice.insert(0, 'all')
            window.FindElement('condition').Update(values=condition)
            
        if event == 'group_nb':
            group_nb=values['group_nb']
            #if group_nb == 'all':
                #group_nb=''
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)
                
            mice = path_dic["list_mice"]
            #mice.insert(0, 'all')
            window.FindElement('mice_nb').Update(values=mice)
            
            #if the previously selected mouse is not in the current select group the mice's input combo is cleared
            if not values['mice_nb'] in mice:
                window.Element('mice_nb').Update('')
            
            #implement the real protocol list in the path_finder function
            #protocol = path_dic["list_protocol"]
            #mice.insert(0, 'all')
            #window.FindElement('protocole').Update(values=protocol)
            
        
        if event == 'mice_nb':
            mice_nb=values['mice_nb']
            #if mice_nb == 'all':
                #mice_nb=''
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)
        
        if event == 'radio_fixe':
            expermiment_type = 'Fixed Delay'
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)
        
        if event == 'radio_random':
            expermiment_type = 'Random Delay'
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)
        
        if event == 'protocole':
            protocol_type = values['protocole']
            #if protocol_type == 'all':
                #protocol_type=''
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type)
            
    #behaviour plotting
        if event == '-behaviour plot-':
            if len(path_dic['list_protocol_path_behaviour'])==1:
                behaviour_path=path_dic['list_protocol_path_behaviour'][0]
                
            lick_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.lick'))
            param_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.param'))
            coder_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.coder'))
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
            
            if values['radio_random']:   #If we chose to random delay
                dic_graph_choice = {"400":values['400'],"400_400":values['400_400'],"900_400":values['400_400'],\
                                                "400_400_400":values['400_400_400'],"900_400_400":values['900_400_400'],"900":values['900'],\
                                                "900_900":values['900_900'],"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
                graphique_random(param_path, lick_path, dic_graph_choice, \
                                 values['display_raster'],values['display_PSTH'], values['display_wheel'], coder_path)

  
    
            if values['radio_fixe']:   #if we chose fixe delay
                graphique_fixe(lick_path, values['display_raster'],values['display_PSTH'], values['display_wheel'], coder_path)
        
    #electrophy plotting
        if event == '-electrophy plot-':
            gf.ephy_plot(path_dic['list_condition_path_ephy'][0],values['Ch_group0'], values['Ch_group1']\
                         ,values['Ch_group0_power'], values['Ch_group1_power'], values['Ch_group0_amplitude'], values['Ch_group1_amplitude'])
    
    except:
        pass
    
window.close()

    