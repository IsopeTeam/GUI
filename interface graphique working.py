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

    if raster or PSTH:
        lick_data_temp = B.load_lickfile(lick_file_path)
        if condition_type == 'No Stim':
            nb_trials= [1,30]     
        elif condition_type == 'Stim':
            nb_trials= [31,60]
        else:
            nb_trials=[1, 60]
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
    title = fr'Mouse nb:{mice_nb}, Fixe Delay (500 ms),protocol {protocol_type}, {condition_type}' 
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
            
            if wheel:
                wheel_data = gf.wheel_speed(wheel_by_delay[cle], condition_type)

            if raster or PSTH:
                lick_data_temp = licks_by_delay[cle]
                if condition_type == 'No Stim':
                    nb_trials= [1,30]                
                elif condition_type == 'Stim':
                    nb_trials= [31,60]
                else:
                    nb_trials=[1, 60]
                
                index_list= []
                for i in range(nb_trials[0],nb_trials[1]+1): 
                    index = np.where(lick_data_temp[:,0] == i)
                    for i in index[0]:
                        index_list.append(i)
                
                lick_data = np.array([[lick_data_temp[i,0],lick_data_temp[i,1]] for i in index_list])
                
            title = fr'Mouse nb:{mice_nb}, Random Delay: {cle}, protocol {protocol_type}, {condition_type}'    
            plot_maker(lick_data, title, cle[-3:], raster, PSTH, wheel, wheel_data)

        else:
            pass

        
sg.theme('DarkBlue')	

#column for time frequency plots
column1 = [[sg.Text('Heat map', justification='center', size=(10, 1))],
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
            [sg.Radio('On', 'radio_bandpass', key='on_bandpass', default=True), sg.Radio('Off', 'radio_bandpass', key='off_bandpass', default=False)],
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
            [sg.Button('Display plot', key='-electrophy plot-')]  
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

    