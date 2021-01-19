# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:43:25 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import numpy as np
import GUI_function_working as gf
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
    if plot_nb >1:
        ax = ax.ravel()
        for subplot in ax:
            subplot.axvspan(0,0.5, facecolor="green", alpha=0.3)
            subplot.axvspan(1.5,2, facecolor="green", alpha=0.3)
            subplot.axvspan(current_reward_time,current_reward_time+0.15, facecolor="red", alpha=0.3)
    else:
        axes.axvspan(0,0.5, facecolor="green", alpha=0.3)
        axes.axvspan(1.5,2, facecolor="green", alpha=0.3)
        axes.axvspan(current_reward_time,current_reward_time+0.15, facecolor="red", alpha=0.3) 

def graphique_fixe(lick_file_path, raster, PSTH, wheel, wheel_path, condition_type):
    
    if condition_type == 'No Stim':
        nb_trials= [1,30]
        nb_trials_use=30
    elif condition_type == 'Stim':
        nb_trials= [31,60]
        nb_trials_use=30
    else:
        nb_trials=[1, 60]
        nb_trials_use=60
        
    if raster or PSTH:
        lick_data_temp = B.load_lickfile(lick_file_path)
        index_list= []
        for i in range(nb_trials[0],nb_trials[1]+1): 
            index = np.where(lick_data_temp[:,0] == i)
            for i in index[0]:
                index_list.append(i)        
        lick_data = np.array([[lick_data_temp[i,0],lick_data_temp[i,1]] for i in index_list])
    else:
        lick_data = None
        
    if wheel:
        wheel_predata = B.load_lickfile(wheel_path, wheel=True)
        wheel_data = gf.wheel_speed(wheel_predata, condition_type)
    else:
        wheel_data = None
    
    title = fr'Mouse nb:{mice_nb}. Number of trials used: {nb_trials_use}'+'\n'+fr'Fixe Delay (500 ms),protocol {protocol_type}, {condition_type}' 
    plot_maker(lick_data, title, 500, raster, PSTH, wheel, wheel_data)
    

def graphique_random(param_file_path, lick_file_path, dic_graph_choice, raster, PSTH, wheel, wheel_path,  mice_nb, protocol_type, condition_type):
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
            
            if condition_type == 'No Stim':
                nb_trials= [1,30]                
            elif condition_type == 'Stim':
                nb_trials= [31,60]
            else:
                nb_trials=[1, 60]
            
            if wheel:
                wheel_data = gf.wheel_speed(wheel_by_delay[cle], condition_type)

            if raster or PSTH:
                lick_data_temp = licks_by_delay[cle]
                
                index_list= []
                for i in range(nb_trials[0],nb_trials[1]+1): 
                    index = np.where(lick_data_temp[:,0] == i)
                    for i in index[0]:
                        index_list.append(i)                                     
                lick_data = np.array([[lick_data_temp[i,0],lick_data_temp[i,1]] for i in index_list])
                
            index_trial_nb_list= []
            for i in range(nb_trials[0],nb_trials[1]+1):
                index_trial_nb = np.where(delays[cle][:,1] ==i)
                for i in index_trial_nb:
                    try:
                        index_trial_nb_list.append(i[0])
                    except: 
                        pass

            nb_trials_use = len(index_trial_nb_list)
            title = fr'Mouse nb:{mice_nb}. Number of trials used: {nb_trials_use}'+'\n'+fr'Random Delay: {cle}, protocol {protocol_type}, {condition_type}'    
            plot_maker(lick_data, title, cle[-3:], raster, PSTH, wheel, wheel_data)

        else:
            pass

        
sg.theme('DarkBlue')	
line_bubbles = b'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'


#column for time frequency plots
column1 = [[sg.Text('Scalogram', justification='center', size=(10, 1))],
            [sg.Checkbox('Amplitude', default=True,key='hm_amplitude')],
            [sg.Checkbox('Power', default=True, key='hm_power')]]      

column2 = [[sg.Text('Ridge line', justification='center', size=(10, 1))],
            [sg.Checkbox('Intensity', default=True, key='rl_intensity')],
            [sg.Checkbox('Frequency', default=True, key='rl_frequency')]]


                    #whole session average
columnA = [[sg.Frame(layout=[[sg.Checkbox('whole session average', default=True,key='ws_average')],
            [sg.Checkbox('whole session instantaneous phase', default=True, key='ws_phase')],[sg.Text('_________Time frequency_________')],
                             [sg.Column(column1),sg.Column(column2)] ], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN,pad=(0,10), tooltip='Whole session and time frequency are plot separetly')]]
                #Time frequency
columnB = [[sg.Frame(layout=[[sg.Radio('Chanel 0','radio_shank', key='Ch_group0', default=False), sg.Radio('Chanel 1','radio_shank',key='Ch_group1', default=False), sg.Radio('Both','radio_shank',key='Ch_groupboth', default=True)]] \
            ,title='Shank selection',title_color='red', relief=sg.RELIEF_SUNKEN, pad=(0,10))],
           [sg.Frame(layout=[
            [sg.Radio('On', 'radio_bandpass', key='on_bandpass', default=False), sg.Radio('Off', 'radio_bandpass', key='off_bandpass', default=True, enable_events=True)],
            [sg.Text('high frequency :'), sg.Spin(values=list(range(0,40000,1)), initial_value=30,key='freq_high', size=(10,1))], 
            [sg.Text('low frequency   :'), sg.Spin(values=list(range(0,40000,1)), initial_value=0,key='freq_low', size=(10,1))],
            [sg.Text('Sample rate      :'), sg.Spin(values=list(range(0,40000,1)), initial_value=20000,key='sample_rate', size=(10,1))]] 
            ,title='Bandpass filter', title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Even if the bandpass filter is off the value is use for de ridge line')]]
  

  

random_section = [[sg.Frame(layout=[      
            [sg.Checkbox('400', default=True, key='400'), sg.Checkbox('400_400', default=True, key='400_400'), \
            sg.Checkbox('900_400', default=True, key='900_400'), sg.Checkbox('400_400_400', default=True, key='400_400_400'), \
            sg.Checkbox('900_400_400', default=True, key='900_400_400')],[sg.Checkbox('900', default=True, key='900'), \
            sg.Checkbox('900_900', default=True, key='900_900'), sg.Checkbox('400_900', default=True, key='400_900'), sg.Checkbox('900_900_900', default=True, key='900_900_900'), \
            sg.Checkbox('400_900_900', default=True, key='400_900_900')]],\
            title='trial to display',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')]]

            #folder searching 
layout= [   [sg.Text('Select data folder     '), sg.InputText('//equipe2-nas1/F.LARENO-FACCINI/BACKUP FEDE', key='main_folder'), sg.FolderBrowse(),sg.Button('Load folder', key='-load-')],
            [sg.Text('Select group       '), sg.InputCombo(values=[], size=(20, 1), key='group_nb', enable_events=True)],            
            [sg.Text('Select mice        '), sg.InputCombo(values=[], size=(20, 1), key='mice_nb', enable_events=True)],            
            #sg.Radio('Training', 'radio_delay', key='training', default=False, enable_events=True),
            [sg.Radio('Random delay', 'radio_delay', key='radio_random', default=True, enable_events=True), sg.Radio('fixe delay', 'radio_delay', key='radio_fixe', enable_events=True)],
            [sg.pin(sg.Column(random_section, key='random_section'))],            
            [sg.Text('Select protocole   '), sg.InputCombo(values=[], size=(20, 1), key='protocole', enable_events=True)],
            [sg.Text('Select condition   '), sg.InputCombo(values=[], size=(20, 1), key='condition', enable_events=True)],
            [sg.Button('Clear plot', key='-clear plot-')],
            #Behaviour
            [sg.Text('_'  * 80)], [sg.Text('Behaviour', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)], 
            [sg.Frame(layout=[      
            [sg.Checkbox('Raster', default=True, key='display_raster'), sg.Checkbox('PSTH', default=True,key='display_PSTH'), \
            sg.Checkbox('Wheel speed', default=True, key='display_wheel')]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN)],
            [sg.Button('Display plot', key='-behaviour plot-')],
            #Electrophy
            [sg.Text('_'  * 80)], [sg.Text('Electrophysiology', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)],
                #whole session average
            [sg.Column(columnA),sg.Column(columnB)], 
            [sg.Button('Display plot' , key='-electrophy plot-')]  
            ]         
            

                                                      
window= sg.Window('', layout, location=(0,0))

#because the chekbox is setup on random delay at the opening of the window
group_nb = ''
mice_nb = ''
expermiment_type = 'Random Delay'
protocol_type = ''
condition_type = ''
while True:
    event, values = window.read()
    
    try:
        if event in (None, 'Close'):	# if user closes window or clicks cancel
            break
        
    #File sorting
        if event == '-load-':
                
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)

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
            window.FindElement('condition').Update(values=condition)
        
        if event == '-clear plot-':
            plt.close('all')
            
        if event == 'group_nb':
            group_nb=values['group_nb']
                    
            mice_nb=''
            window.Element('mice_nb').Update(mice_nb)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
                
            mice = path_dic["list_mice"]
            window.FindElement('mice_nb').Update(values=mice)            
            
        
        if event == 'mice_nb':
            mice_nb=values['mice_nb']
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)

            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
        if event == 'radio_fixe':
            expermiment_type = 'Fixed Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=False)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)

        if event == 'radio_random':
            expermiment_type = 'Random Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=True)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
        """
        if event == 'training':
            expermiment_type = 'Training'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=True)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition_type = 'all'
            window.FindElement('condition').Update(values=condition_type)
        """
        if event == 'protocole':
            protocol_type = values['protocole']
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)

        
        if event == 'condition':
            condition_type = values['condition']
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
        
        if event == 'off_bandpass':
            window.FindElement('freq_high').Update(30)
            window.FindElement('freq_low').Update(0)
            window.FindElement('sample_rate').Update(20000)
            
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
                dic_graph_choice_time = {"400":values['400'],"400_400":values['400_400'],"900_400":values['400_400'],\
                                                "400_400_400":values['400_400_400'],"900_400_400":values['900_400_400'],"900":values['900'],\
                                                "900_900":values['900_900'],"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
                
                graphique_random(param_path, lick_path, dic_graph_choice_time, values['display_raster'],values['display_PSTH'], \
                                 values['display_wheel'], coder_path, mice_nb, protocol_type, condition_type)

  
    
            if values['radio_fixe']:   #if we chose fixe delay
                graphique_fixe(lick_path, values['display_raster'],values['display_PSTH'], values['display_wheel'], coder_path, condition_type)
        
    #electrophy plotting
        if event == '-electrophy plot-':

            bandpass_dic= {'freq_low': values['freq_low'], 'freq_high': values['freq_high'], 'sample_rate': values['sample_rate'], 'on_bandpass':values['on_bandpass']}            
            shank_dic = {'chanel0' : values['Ch_group0'], 'chanel1': values['Ch_group1'], 'both': values['Ch_groupboth']}            
            graph_dic = {'ws_average' : values['ws_average'], 'ws_phase': values['ws_phase'], 'hm_amplitude': values['hm_amplitude'], 'hm_power': values['hm_power'], 'rl_intensity': values['rl_intensity'], 'rl_frequency': values['rl_frequency']}            
            path_ephy_dic = {'protocol_path' : os.path.normpath(path_dic['list_protocol_path_ephy'][0]), 'condition_path' : os.path.normpath(path_dic['list_condition_path_ephy'][0])}
            
            if values['radio_random']:
                dic_time = {"400":values['400'],"400_400":values['400_400'],"900_400":values['400_400'],"400_400_400":values['400_400_400'],"900_400_400":values['900_400_400'],"900":values['900'],"900_900":values['900_900'],"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
                
                lick_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.lick'))
                param_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.param'))
                path_ephy_dic['lick_path'] = os.path.normpath(lick_path[0])
                path_ephy_dic['param_path'] = os.path.normpath(param_path[0])
                
                gf.random_ephy(path_ephy_dic, graph_dic, dic_time, mice_nb, protocol_type, condition_type, bandpass_dic, shank_dic)
            
            if values['radio_fixe']:
                gf.ephy_plot(path_ephy_dic, graph_dic, mice_nb, protocol_type, condition_type, bandpass_dic, shank_dic)

    except:
        pass
    
window.close()

    