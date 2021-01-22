# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 16:52:55 2021

@author: Master5.INCI-NSN
"""


import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import numpy as np
import GUI_function as gf
import glob
import os

def list_file(path_ephy, path_behaviour, condition, compare_param = False):
   
    path_ephy_nostim = f'{path_ephy}/No Stim'
    list_time_ephy_nostim = duration_trial(path_ephy_nostim)  
    list_name_behaviour = [os.path.basename(i) for i in glob.glob(path_behaviour+'/*param')]
    list_name1 = list_name_behaviour[0].split('.')[0].split('_')
    list_name1 = [list_name1[-3], list_name1[-2], list_name1[-1]]
    list_time_behaviour = int(list_name1[0])*3600+int(list_name1[1])*60+int(list_name1[2])
    time_dif = list_time_ephy_nostim[0]-list_time_behaviour
    path_ephy = f'{path_ephy}/{condition}'
    list_time_ephy= [os.path.basename(i) for i in glob.glob(path_ephy+'/*rbf')]
    
    param_path= f'{path_behaviour}/{list_name_behaviour[0]}'
    random_delay=B.extract_random_delay(param_path)
    nb_behav_trial = len(random_delay)+1

    
    return len(list_time_ephy), time_dif, nb_behav_trial

   
def duration_trial(path, trial_duration=False):
    list_name = [os.path.basename(i) for i in glob.glob(path+'/*rbf')]
    
    list_name1 = [i.split('T')[1].split('M')[0] for i in list_name]
    list_time = [int(i.split('-')[0])*3600+int(i.split('-')[1])*60+int(i.split('-')[2]) for i in list_name1]
    if trial_duration:
        list_time = [list_time[i+1] - time for i, time in enumerate(list_time) if i < len(list_time)-1]
    
        list_weard = []
        for i, value in enumerate(list_time):
            if value != 10:
                list_weard.append([list_name[i], value])
            
    return list_time
    
def plot_maker(graph_dic, path_ephy, path_behaviour, condition):
    
    
    plot_nb = int(graph_dic['trial_duration'])+int(graph_dic['wheel_data'])+int(graph_dic['wheel_speed'])
    fig, ax = plt.subplots(plot_nb, 1, sharex=True)
    fig.suptitle('files anormalities',weight='bold') #main figure title
    plot_position = 0
    if plot_nb==1:
        axes=ax
    elif plot_nb>1:
        axes=ax[plot_position]

    if graph_dic['trial_duration']:
        list_time = duration_trial(path_ephy, trial_duration=True)
        time_plot = list(range(1, len(list_time)+1,1))
        axes.plot(time_plot, list_time)
        axes.set_ylabel('duration of the trial (sec') #PSTH title
        axes.set_title('Trial duration') #PSTH y label
        
        plot_position +=1
    
    if graph_dic['wheel_data']:
        wheel_path = glob.glob(os.path.join(path_behaviour, '*.coder'))
        wheel_predata = B.load_lickfile(wheel_path[0], wheel=True)
        _, wheel_data = gf.wheel_speed(wheel_predata, condition_type=condition)
        
        wheel_data_list = []
        for key, value in wheel_data.items():
            wheel_data_list.append(len(value[:,1]))
        
        time_plot = list(range(1, len(wheel_data_list)+1,1))
        
        if plot_nb >1:
            axes=ax[plot_position]
            
        axes.plot(time_plot, wheel_data_list)
        axes.set_ylabel('nb of wheel data') #PSTH title
        axes.set_title('nb of wheel data') #PSTH y label
        
        plot_position +=1
    
    if graph_dic['wheel_speed']:
        wheel_path = glob.glob(os.path.join(path_behaviour, '*.coder'))
        wheel_predata = B.load_lickfile(wheel_path[0], wheel=True)
        _, wheel_data = gf.wheel_speed(wheel_predata, condition_type=condition)
        
        wheel_speed_list = []
        for key, value in wheel_data.items():
            wheel_speed_list.append(np.mean(value[:,1]))
        
        time_plot = list(range(1, len(wheel_speed_list)+1,1))
        
        if plot_nb >1:
            axes=ax[plot_position]
            
        axes.plot(time_plot, wheel_speed_list)
        axes.set_ylabel('mean of the \ninstantenious speed (cm/s)') #PSTH title
        axes.set_title('mean wheel speed per trial') #PSTH y label
       
    axes.set_xlabel('trial nb') #PSTH x label







    
sg.theme('DarkBlue')	


            #folder searching 
layout= [   [sg.Text('Select data folder     '), sg.InputText('//equipe2-nas1/F.LARENO-FACCINI/BACKUP FEDE', key='main_folder'), sg.FolderBrowse(),sg.Button('Load folder', key='-load-')],
            [sg.Text('Select group       '), sg.InputCombo(values=[], size=(20, 1), key='group_nb', enable_events=True)],
            [sg.Text('Select mice        '), sg.InputCombo(values=[], size=(20, 1), key='mice_nb', enable_events=True)],            
            #sg.Radio('Training', 'radio_delay', key='training', default=False, enable_events=True),
            [sg.Radio('Random delay', 'radio_delay', key='radio_random', default=True, enable_events=True), sg.Radio('Fixe delay', 'radio_delay', key='radio_fixe', enable_events=True), sg.Radio('Training', 'radio_delay', key='radio_training', enable_events=True)],
            [sg.Text('Select protocole   '), sg.InputCombo(values=[], size=(20, 1), key='protocole', enable_events=True), sg.Text('Time dif:'), sg.InputText('', key='time_dif', size=(3,1)), sg.Text('sec')],
            [sg.Text('Select condition   '), sg.InputCombo(values=[], size=(20, 1), key='condition', enable_events=True), sg.Text('Nb of Ephy files:'), sg.InputText('', key='nb_files', size=(5,1)),sg.Text('Nb behav trial:'), sg.InputText('', key='nb_behav_trial', size=(5,1))],
            [sg.Button('Clear plot', key='-clear plot-')],
            #Behaviour
            [sg.Text('_'  * 80)], 
            [sg.Frame(layout=[      
            [sg.Checkbox('trial duration', default=True, key='trial_duration'), sg.Checkbox('nb of wheel data', default=True,key='wheel_data'), \
            sg.Checkbox('Wheel speed', default=True, key='wheel_speed')]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN)],
            [sg.Button('Display plot', key='-plot-')] 
            ]         
            

                                                      
window= sg.Window('', layout, location=(0,0))

#because the chekbox is setup on random delay at the opening of the window
group_nb = ''
mice_nb = ''
expermiment_type = 'Random Delay'
protocol_type = ''
condition_type = ''
list_condition = ['No Stim', 'Stim']

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
                     
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)
        
        if event == '-clear plot-':
            plt.close('all')
            
        if event == 'group_nb':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            group_nb=values['group_nb']
                    
            mice_nb=''
            window.Element('mice_nb').Update(mice_nb)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
                
            mice = path_dic["list_mice"]
            window.FindElement('mice_nb').Update(values=mice)            
            
        
        if event == 'mice_nb':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            mice_nb=values['mice_nb']
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)

            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
        if event == 'radio_fixe':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            expermiment_type = 'Fixed Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)

        if event == 'radio_random':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            expermiment_type = 'Random Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)
    
        if event == 'radio_training':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            expermiment_type = 'Training'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update('')
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = ['No Stim']
            window.FindElement('condition').Update(values=condition)
            
        
        if event == 'protocole':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            condition_type = ''
            window.Element('condition').Update(condition_type)
            protocol_type = values['protocole']
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)

        
        if event == 'condition':
            window.Element('nb_files').Update('')
            window.Element('time_dif').Update('')
            window.Element('nb_behav_trial').Update('')
            
            
            condition_type = values['condition']
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
            
            if values['radio_training'] or values['protocole']=='NB' or values['protocole']=='P0':
                compare_param = True
            else:
                compare_param = False
                
            nb_files_found, time_dif_found, nb_behav_trial = list_file(path_dic['list_protocol_path_ephy'][0], path_dic['list_protocol_path_behaviour'][0], values['condition'], compare_param)
            window.Element('nb_files').Update(nb_files_found)
            window.Element('time_dif').Update(time_dif_found)
            window.Element('nb_behav_trial').Update(nb_behav_trial)


        
        if event == 'off_bandpass':
            window.FindElement('freq_high').Update(30)
            window.FindElement('freq_low').Update(0)
            window.FindElement('sample_rate').Update(20000)
        
        if event == '-plot-':
            if values['radio_training'] or values['protocole']=='NB' or values['protocole']=='P0':
                condition_type = 'all'
            else:
                condition_type = values['condition']
                
            graph_dic = {'trial_duration' : values['trial_duration'], 'wheel_data': values["wheel_data"], 'wheel_speed': values['wheel_speed'] }
            plot_maker(graph_dic, path_dic['list_condition_path_ephy'][0], path_dic['list_protocol_path_behaviour'][0],condition_type)
            
            
    except:
        pass
    
window.close()