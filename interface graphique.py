# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:43:25 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import extrapy.Behaviour as B
import extrapy.Organize as og
import numpy as np
import GUI_function_working as gf
import glob
import os
import pickle

def plot_maker(lick_data, title, reward_time, graph_choice_behav_dic, wheel_data, new_fig):

    plot_nb = int(graph_choice_behav_dic['raster'])+int(graph_choice_behav_dic['PSTH'])+int(graph_choice_behav_dic['wheel'])
    if new_fig:
        fig_new = plt.figure(title)
        ax = fig_new.subplots(plot_nb, 1, sharex=True)
        fig_new.suptitle(title,weight='bold')
    else:
        plt.figure(0)
        ax = fig.subplots(plot_nb, 1, sharex=True)
        fig.suptitle(title,weight='bold') #main figure title
    
    plot_position = 0
    if plot_nb==1:
        axes=ax
    elif plot_nb>1:
        axes=ax[plot_position]
    if graph_choice_behav_dic['raster']:
        #first subplot (Raster)
        B.scatter_lick(lick_data, axes, x_label=None)
        axes.set_title('RASTER') #Raster subplot title
        plot_position +=1
    
    if graph_choice_behav_dic['PSTH']:
        #second subplot (PSTH)
        if plot_nb >1:
            axes=ax[plot_position]
    
        #second subplot (PSTH)
        B.psth_lick(lick_data, axes) #PSTH graph 
        axes.set_ylabel('nb of occurence') #PSTH title
        axes.set_title('PSTH') #PSTH y label
        plot_position +=1
    
    if graph_choice_behav_dic['wheel']:
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
    
    plt.draw()
    

def graphique_behav(graph_choice_behav_dic, path_behav_dic, trial_dic, new_fig, current_time_displayed):
    
    if graph_choice_behav_dic['ws_average']:
        trial_dic_choice= trial_dic[current_time_displayed]['trial_dic_choice']
        trial_data = trial_dic[current_time_displayed]['trial_data']
        
        nb_trials_use=0
        for value in trial_dic_choice.values():
            if value:
                nb_trials_use +=1   
        title = fr'Mouse nb:{mice_nb}. Number of trials used: {nb_trials_use}'+'\n'+fr'{experiment_type}({current_time_displayed} ms),protocol {protocol_type}, {condition_type}' 

    else:
        current_trial = list_trial[trial_displayed]
        trial_dic_choice={current_trial: trial_dic[current_time_displayed]['trial_dic_choice'][current_trial]}
        trial_data = {i:v for i, v in trial_dic[current_time_displayed]['trial_data'].items() if i== current_trial}
        
        title = fr'Mouse nb:{mice_nb}. Trials nb {current_trial}'+'\n'+fr'{experiment_type}({current_time_displayed} ms),protocol {protocol_type}, {condition_type}' 

    
    
    reward_time = current_time_displayed[-3:]
            
    if graph_choice_behav_dic['raster'] or graph_choice_behav_dic['PSTH']:
        lick_data = np.empty((1,2))
        for i, value in trial_data.items():
            if trial_dic_choice[i]:
                if lick_data.shape[0] == 1:
                    lick_data = value
                else:
                    lick_data = np.vstack((lick_data, value))                   
    else:
        lick_data = None
        
    if graph_choice_behav_dic['wheel']:
        wheel_predata = B.load_lickfile(path_behav_dic['wheel'], wheel=True)
        wheel_data, _ = gf.wheel_speed(wheel_predata, trial_dic_choice)
    else:
        wheel_data = None
        

    plot_maker(lick_data, title, reward_time, graph_choice_behav_dic, wheel_data, new_fig)
    
def plot_master(new_fig=False, choice_temp=None):
    global fig
    global list_trial
    
    current_time_displayed = trial_dic['list_time_display'][graph_displayed]
    list_trial = trial_dic[trial_dic['list_time_display'][graph_displayed]]['list_trial_display']
    
    if not new_fig:
        if plt.fignum_exists(fig.number):
            plt.figure(0)
            plt.clf()
        
        else: 
            fig = plt.figure(0)
            fig.canvas.set_window_title('Main Figure')
            
        
    
    if choice == 'behav' or choice_temp == 'behav': 
        graphique_behav(graph_choice_behav_dic, path_behav_dic, trial_dic, new_fig, current_time_displayed)
    

    elif choice == 'ephy_raw'or choice_temp == 'ephy_raw' or choice == 'ephy_time_frequency' or choice_temp == 'ephy_time_frequency':
    
        
        if graph_dic['ws_average']:
            ephy_data = gf.list_file_ephy_maker(trial_dic, condition_type, ephy_path, bandpass_dic, current_time_displayed)
            info_exp_dic = {'trial_use': len(ephy_data.keys()), 'mice_nb':mice_nb, 'experiment_type': experiment_type, 'current_time' : current_time_displayed, 'protocol_type':protocol_type, 'condition_type':condition_type}
            
        else:
            current_trial = list_trial[trial_displayed]
            info_exp_dic = {'trial_use': current_trial, 'mice_nb':mice_nb, 'experiment_type': experiment_type, 'current_time' : current_time_displayed, 'protocol_type':protocol_type, 'condition_type':condition_type}
            
            if condition_type== 'Stim':
                file_nb = int(current_trial)-31 
            else:
                file_nb = int(current_trial)-1 #-1 beacause the list start at 0
            
            ephy_names = og.file_list(ephy_path,True,'.rbf')
            file_name = ephy_names[file_nb]
            file= [(current_trial, os.path.normpath(fr'{ephy_path}/{file_name}.rbf'))]
            
            ephy_data = gf.data_ephy_calc(file, bandpass_dic)
            ephy_data = ephy_data[current_trial]
            
        if choice == 'ephy_raw' or choice_temp == 'ephy_raw':
            gf.graph_ephy_raw(ephy_data, graph_dic, shank_dic, phase_frequency, fig, info_exp_dic, new_fig)
        
        elif choice == 'ephy_time_frequency' or choice_temp == 'ephy_time_frequency':
            gf.graph_ephy_time_frequency(ephy_data, graph_dic, shank_dic, rl_dic, fig, info_exp_dic, new_fig)

    
    
def trial_list_maker (path_behav_dic , condition_type, dic_graph_choice_time):
    lick_data_temp = B.load_lickfile(path_behav_dic['lick'])

    if condition_type == 'No Stim':
        nb_trials= [1,30]
    elif condition_type == 'Stim':
        nb_trials= [31,60]
    else:
        last_trial_nb = lick_data_temp[:,0]
        nb_trials=[1, int(last_trial_nb[-1])]
        
    if experiment_type == 'Fixed Delay': 
        trial_dic ={}
        trial_data ={}
        for i in range(nb_trials[0],nb_trials[1]+1):
            index = np.where(lick_data_temp[:,0] == i)
            if index[0].size > 0:
                trial_data[i]= np.array([[lick_data_temp[i,0],lick_data_temp[i,1]] for i in index[0]])
        trial_dic_choice = {i: True for i in trial_data.keys()}
        list_trial_display = [cle for cle, v in trial_dic_choice.items() if v]
        trial_dic['500']= {'trial_data':trial_data, 'trial_dic_choice':trial_dic_choice, 'list_trial_display': list_trial_display}
        trial_dic['list_time_display']=['500']
    
    elif experiment_type=='Random Delay' or experiment_type == 'Training':
        random_delay=B.extract_random_delay(path_behav_dic['param'])
        delays, licks_by_delay = B.separate_by_delay(random_delay, lick_data_temp)
        
        trial_dic = {}
        for cle in delays.keys():
            if dic_graph_choice_time[cle]:
                trial_data ={}
                for i in range(nb_trials[0],nb_trials[1]+1):
                    index = np.where(licks_by_delay[cle][:,0] == i)
                    if index[0].size > 0:
                        trial_data[i]= np.array([[licks_by_delay[cle][i,0],licks_by_delay[cle][i,1]] for i in index[0]])
                 
                trial_dic_choice = {i: True for i in trial_data.keys()}
                list_trial_display = [cle for cle, v in trial_dic_choice.items() if v]
                trial_dic[cle]= {'trial_data':trial_data, 'trial_dic_choice':trial_dic_choice, 'list_trial_display':list_trial_display}
        
        list_time_display = [cle for cle in trial_dic.keys()]
        trial_dic['list_time_display']=list_time_display
             
    return trial_dic

    
def window_cbox_list(location=(650,0)): 
    
    current_time_displayed = trial_dic['list_time_display'][graph_displayed]
    
    cbox_list =[]
    for i, value in trial_dic[current_time_displayed]['trial_dic_choice'].items():
        cbox_list.append([sg.Checkbox(f'Trial nb: {i}', default=value, enable_events=True, key=i)])
    
    layout = [[sg.Column(cbox_list, size=(195, 500), scrollable=True,  vertical_scroll_only=True)], 
              [sg.Button('Update', key= 'update'), sg.Button('Select all', key='select_all'), sg.Button('Deselect all', key='deselect_all')]] 
    
    return sg.Window(fr'{current_time_displayed}ms', layout, location = location, finalize=True)

def window_trial_by_trial(location=(650,0)):
    
    treedata = sg.TreeData()
    if experiment_type != 'Fixed Delay':
        time_list= [i for i in trial_dic['list_time_display']]
    else:
        time_list=['500']
    
    for idx, time in enumerate(time_list):
        treedata.insert('', key=idx,text=time, values=[])
        for trial in enumerate(trial_dic[time]['list_trial_display']):
           treedata.insert(idx, key=(idx,trial[0]),text=fr'Trial {trial[1]}', values=[])
    
    layout = [[sg.Tree(data=treedata, headings=[], auto_size_columns=True, num_rows=15, col0_width=25, row_height=25, key='-TREE-', show_expanded=False, enable_events=True)],
          [sg.Button('Go to trial', key='go_trial')]]    
    return sg.Window('Trial selection', layout, location = location, finalize=True)

def window_trial_update(average):
    global trial_selection_window
    if trial_selection_window:
        location = trial_selection_window.CurrentLocation()
        trial_selection_window.close()
        if average:
            trial_selection_window = window_cbox_list(location)
        else:
            trial_selection_window = window_trial_by_trial(location)


def window_tag_list_maker(location=(650,0)):
    os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))

    treedata = sg.TreeData()
    if os.path.exists('taged_trials.txt'):
        with open ('taged_trials.txt', 'rb') as tag_trials_file:
            my_depickler = pickle.Unpickler(tag_trials_file)
            tag_trials_dic = my_depickler.load()
            
        for time, trial_list in tag_trials_dic.items():
            treedata.insert('', key=time, text=time, values=[])
            for trial in trial_list:
               treedata.insert(time, key=(time, trial),text=fr'Trial {trial}', values=[])
    
    layout = [[sg.Tree(data=treedata, headings=[], auto_size_columns=True, num_rows=15, col0_width=25, row_height=25, key='-TREE-', show_expanded=False, enable_events=True)],
          [sg.Button('Go to trial', key='go_tag')]]    
    return sg.Window('Tag trials', layout, location = location, finalize=True)

def window_tag_update():
    global window_tag_list
    if window_tag_list:
        location = window_tag_list.CurrentLocation()
        window_tag_list.close()
        window_tag_list = window_tag_list_maker(location)

def main_window():
    
    rd_column1=[[sg.Checkbox('Raw data', default=True,key='raw_data')],[sg.Checkbox('Instantaneous phase', default=True, key='phase')]]
    
    rd_column2=[[sg.Frame(layout=[
                [sg.Text('phase frequency (Hz):'), sg.Spin(values=list(range(0,40000,1)), initial_value=10, key='phase_freq', size=(5,1))]]
                ,title='Phase parameters', title_color='red', relief=sg.RELIEF_SUNKEN)]]
    
    #raw data
    tab1 = [[sg.Column(rd_column1),sg.Column(rd_column2)],
            [sg.Button('Display plot' , key='-Raw data plot-'), sg.Button('Display plot on a new figure', key='-Raw data plot new fig-')]]
    
    
    #column for time frequency plots
    tf_column1 = [[sg.Text('Scalogram', justification='center', size=(10, 1))],
                [sg.Checkbox('Amplitude', default=True,key='hm_amplitude')],
                [sg.Checkbox('Power', default=True, key='hm_power')]]      
    
    tf_column2 = [[sg.Text('Ridge line', justification='center', size=(10, 1))],
                [sg.Checkbox('Intensity', default=True, key='rl_intensity')],
                [sg.Checkbox('Frequency', default=True, key='rl_frequency')]]
    
    tf_column3=[[sg.Frame(layout=[
                [sg.Text('high (Hz):'), sg.Spin(values=list(range(0,40000,1)), initial_value=30,key='rl_freq_high', size=(5,1))], [sg.Text('low  (Hz):'), sg.Spin(values=list(range(0,40000,1)), initial_value=0,key='rl_freq_low', size=(5,1))]]
                ,title='Ridge parameters', title_color='red', relief=sg.RELIEF_SUNKEN)]]
    
    #time frequency
    tab2 = [[sg.Column(tf_column1),sg.Column(tf_column2),sg.Column(tf_column3)], [sg.Button('Display plot' , key='-time frequency plot-'), sg.Button('Display plot on a new figure', key='-time frequency plot new fig-')]]
    
    
      
    
    random_section = [[sg.Frame(layout=[      
                [sg.Checkbox('400', default=True, key='400', enable_events=True), sg.Checkbox('400_400', default=False, key='400_400', enable_events=True), \
                sg.Checkbox('900_400', default=False, key='900_400', enable_events=True), sg.Checkbox('400_400_400', default=False, key='400_400_400', enable_events=True), \
                sg.Checkbox('900_400_400', default=False, key='900_400_400', enable_events=True)],[sg.Checkbox('900', default=True, key='900', enable_events=True), \
                sg.Checkbox('900_900', default=False, key='900_900', enable_events=True), sg.Checkbox('400_900', default=False, key='400_900', enable_events=True), sg.Checkbox('900_900_900', default=False, key='900_900_900', enable_events=True), \
                sg.Checkbox('400_900_900', default=False, key='400_900_900', enable_events=True)]],\
                title='trial to display',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')]]
    
                #folder searching 
    layout= [   [sg.Text('Select data folder     '), sg.InputText('//equipe2-nas1/F.LARENO-FACCINI/BACKUP FEDE', key='main_folder'), sg.FolderBrowse(),sg.Button('Load folder', key='-load-')],
                [sg.Text('Select group       '), sg.InputCombo(values=[], size=(20, 1), key='group_nb', enable_events=True)],
                [sg.Text('Select mice        '), sg.InputCombo(values=[], size=(20, 1), key='mice_nb', enable_events=True)],            
                #sg.Radio('Training', 'radio_delay', key='training', default=False, enable_events=True),
                [sg.Radio('Random delay', 'radio_delay', key='radio_random', default=True, enable_events=True), sg.Radio('Fixe delay', 'radio_delay', key='radio_fixe', enable_events=True), sg.Radio('Training', 'radio_delay', key='radio_training', enable_events=True)],
                [sg.pin(sg.Column(random_section, key='random_section'))],            
                [sg.Text('Select protocole   '), sg.InputCombo(values=[], size=(20, 1), key='protocole', enable_events=True)],
                [sg.Text('Select condition   '), sg.InputCombo(values=[], size=(20, 1), key='condition', enable_events=True)],
                [ sg.Button('Tag list', key='-tag list-'), sg.Button('Trial list', key='-trial list-'), sg.Radio('All session average', 'radio_session', key='ws_average', default=True, enable_events=True), sg.Radio('Trial by trial','radio_session',key='trial_by_trial', default=False, enable_events=True)],
                [sg.Button('previous trace',  key='previous'), sg.Button('next trace', key= 'next'), sg.Button('Tag',  key='tag'), sg.Button('Untag', key= 'untag')],
                [sg.Button('Clear plot', key='-clear plot-', button_color=('red','white'))],
                #Behaviour
                [sg.Text('_'  * 80)], [sg.Text('Behaviour', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)], 
                [sg.Frame(layout=[      
                [sg.Checkbox('Raster', default=True, key='display_raster'), sg.Checkbox('PSTH', default=True,key='display_PSTH'), \
                sg.Checkbox('Wheel speed', default=True, key='display_wheel')]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN)],
                [sg.Button('Display plot', key='-behaviour plot-'),sg.Button('Display plot on a new figure', key='-behaviour plot new fig-')],
                #Electrophy
                [sg.Text('_'  * 80)], [sg.Text('Electrophysiology', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)],
                #truc
                [sg.Frame(layout=[[sg.Radio('Chanel 0','radio_shank', key='Ch_group0', default=False), sg.Radio('Chanel 1','radio_shank',key='Ch_group1', default=False), sg.Radio('Both','radio_shank',key='Ch_groupboth', default=True)]] \
                ,title='Shank selection',title_color='red', relief=sg.RELIEF_SUNKEN, pad=(0,10)),sg.Frame(layout=[
                [sg.Text('low (Hz):'), sg.Spin(values=list(range(0,40000,1)), initial_value=0,key='bp_freq_low', size=(5,1)), sg.Text('high (Hz):'), sg.Spin(values=list(range(0,40000,1)), initial_value=4000,key='bp_freq_high', size=(5,1))]] 
                ,title='Bandpass filter', title_color='red', relief=sg.RELIEF_SUNKEN)],    
                #whole session average
                [sg.TabGroup([[sg.Tab('Raw data', tab1), sg.Tab('Time frequency', tab2)]])]] 
    return sg.Window('', layout, location=(0,0), finalize=True)
     
            

fig = plt.figure(0)
fig.canvas.set_window_title('Main Figure')
fig.subplots(1)
group_nb = ''
mice_nb = ''

#because the chekbox is setup on random delay at the opening of the window
experiment_type = 'Random Delay'
protocol_type = ''
condition_type = ''
list_condition = ['No Stim', 'Stim']
dic_graph_choice_time = {"400":True,"400_400":False,"900_400":False,"400_400_400":False,"900_400_400":False,"900":True,"900_900":False,"400_900":False,"900_900_900":False,"400_900_900":False}
sg.theme('DarkBlue')

main_window, trial_selection_window,  window_tag_list = main_window(), None, None        # start off with 1 window open

while True:
    window, event, values = sg.read_all_windows()
    
    try:
        if event == sg.WIN_CLOSED:	# if user closes window or clicks cancel
            window.close()
            if window == trial_selection_window:
                trial_selection_window = None
            elif window == window_tag_list:
                window_tag_list = None
            elif window == main_window:
                break
        
    #File sorting
        if event == '-load-':
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)

            group = path_dic["list_group"]
            #group.insert(0, 'all')
            window.FindElement('group_nb').Update(values=group)
            
            mice = path_dic["list_mice"]
            #mice.insert(0, 'all')
            window.FindElement('mice_nb').Update(values=mice)
                     
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)
        
        if event == '-clear plot-':
            plt.clf() 
            ax = fig.subplots(1)
            plt.draw()
            if 'choice' in globals():
                del choice
            
        if event == 'group_nb':
            group_nb=values['group_nb']
                    
            mice_nb=''
            window.Element('mice_nb').Update(mice_nb)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
                
            mice = path_dic["list_mice"]
            window.FindElement('mice_nb').Update(values=mice)            
            
        
        if event == 'mice_nb':
            mice_nb=values['mice_nb']
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)

            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
        if event == 'radio_fixe':
            experiment_type = 'Fixed Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=False)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)

        if event == 'radio_random':
            experiment_type = 'Random Delay'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=True)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = list_condition
            window.FindElement('condition').Update(values=condition)
    
        if event == 'radio_training':
            experiment_type = 'Training'
            protocol_type = ''
            window.Element('protocole').Update(protocol_type)
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            window['random_section'].update(visible=True)
            
            protocol = path_dic["list_protocol"]
            window.FindElement('protocole').Update(values=protocol)
            
            condition = ['No Stim']
            window.FindElement('condition').Update(values=condition)
                        
        
        if event == 'protocole':
            condition_type = ''
            window.Element('condition').Update(condition_type)
            
            protocol_type = values['protocole']
            
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            
            if protocol_type == 'NB' or protocol_type == 'P0' or experiment_type == 'Training':
                condition = ['No Stim']
                window.FindElement('condition').Update(values=condition)
            
            else:
                condition = list_condition
                window.FindElement('condition').Update(values=condition)

        # all the experiment paramaters are fill so we can load and pretreate the data
        if event == 'condition':
            condition_type = values['condition']
            path_dic = gf.path_finder(values['main_folder'], group_nb, mice_nb, experiment_type, protocol_type, condition_type)
            
            lick_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.lick'))
            param_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.param'))
            coder_path=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.coder'))

            lick_path = os.path.normpath(lick_path[0])
            param_path = os.path.normpath(param_path[0])
            coder_path = os.path.normpath(coder_path[0])

            
            path_behav_dic= {'lick': lick_path, 'param': param_path, 'wheel': coder_path}
            if values['radio_training'] or values['protocole']== 'NB' or values['protocole']== 'P0':
                    condition_type= 'all'
                    
            graph_displayed = 0 #we start by displaying the first time delay
            trial_displayed = 0 #we start by displaying the first trail
            trial_dic = trial_list_maker (path_behav_dic, condition_type, dic_graph_choice_time)
            list_trial = trial_dic[trial_dic['list_time_display'][graph_displayed]]['list_trial_display']
            
            
            window_trial_update(values['ws_average'])
        
        if event == '400' or event == '400_400' or event == '900_400' or event == '900_400' or event == '400_400_400' or event == '900_400_400' or event == '900'or event == '900_900'or event == '400_900'or event == '900_900_900'or event == '400_900_900':
            dic_graph_choice_time = {"400":values['400'],"400_400":values['400_400'],"900_400":values['900_400'],"400_400_400":values['400_400_400'],
                         "900_400_400":values['900_400_400'],"900":values['900'],"900_900":values['900_900']
                         ,"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
            
            if condition_type !='':
                trial_dic = trial_list_maker (path_behav_dic, condition_type, dic_graph_choice_time)
                window_trial_update(values['ws_average'])
        
        if event =='ws_average' or event == 'trial_by_trial':
            window_trial_update(values['ws_average'])

        if event=='next': 
            if values['trial_by_trial']:
                if trial_displayed+1 < len(list_trial):
                    trial_displayed +=1
                    plot_master()
                
                else:
                    trial_displayed =0
                    if graph_displayed+1 < len(trial_dic['list_time_display']):                       
                        graph_displayed +=1
                        plot_master()
                    
            else:
                if graph_displayed+1 < len(trial_dic['list_time_display']):                
                    graph_displayed +=1
                    plot_master()
            
                window_trial_update(values['ws_average'])
                
        
        if event=='previous':
            if values['trial_by_trial']:
                if trial_displayed > 0:
                    trial_displayed -=1
                    plot_master()     
                else:
                    trial_displayed =0
                    if graph_displayed > 0:
                        graph_displayed -=1
                        plot_master()
            else:
                if graph_displayed > 0:
                    graph_displayed -=1
                    plot_master()
                
                window_trial_update(values['ws_average'])
        
        if event=='tag':
            if values['trial_by_trial']:
                if 'choice' in globals():
                    os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))
                    if os.path.exists('taged_trials.txt'):
                        with open ('taged_trials.txt', 'rb') as tag_trials_file:
                            my_depickler = pickle.Unpickler(tag_trials_file)
                            tag_trials_dic = my_depickler.load()
                    else:
                        tag_trials_dic = {}
                    
                    if trial_dic['list_time_display'][graph_displayed] not in tag_trials_dic:
                        tag_trials_dic[trial_dic['list_time_display'][graph_displayed]]=[]
                    tag_trials_dic[trial_dic['list_time_display'][graph_displayed]].append(list_trial[trial_displayed])
                    
                    with open ('taged_trials.txt', 'wb') as tag_trials_file:
                        my_pickler = pickle.Pickler(tag_trials_file)
                        my_pickler.dump(tag_trials_dic)
                    
                    window_tag_update()

    # trial_dic['list_time_display'][graph_displayed] = curent time display (i dont want it to be global)
    # list_trial[trial_displayed] = current trial display  (i dont want it to be global)  

        if event=='untag':
            if values['trial_by_trial']:
                if 'choice' in globals():
                    os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))
                    if os.path.exists('taged_trials.txt'):
                        with open ('taged_trials.txt', 'rb') as tag_trials_file:
                            my_depickler = pickle.Unpickler(tag_trials_file)
                            tag_trials_dic = my_depickler.load()
                        
                        if trial_dic['list_time_display'][graph_displayed] in tag_trials_dic:
                            if list_trial[trial_displayed] in tag_trials_dic[trial_dic['list_time_display'][graph_displayed]]:
                                tag_trials_dic[trial_dic['list_time_display'][graph_displayed]].remove(list_trial[trial_displayed])
                            
                            if len(tag_trials_dic[trial_dic['list_time_display'][graph_displayed]])==0:
                                del tag_trials_dic[trial_dic['list_time_display'][graph_displayed]]
                        
                        with open ('taged_trials.txt', 'wb') as tag_trials_file:
                            my_pickler = pickle.Pickler(tag_trials_file)
                            my_pickler.dump(tag_trials_dic)
                    
                        window_tag_update()
                                
                    else:
                        pass
        
        if event == '-tag list-':
            window_tag_list = window_tag_list_maker()
        
        if event == 'go_tag':
            graph_displayed = trial_dic['list_time_display'].index(values['-TREE-'][0][0])
            trial_displayed = trial_dic[trial_dic['list_time_display'][graph_displayed]]['list_trial_display'].index(values['-TREE-'][0][1])
            if not 'choice' in globals():
                choice = 'behav'
                graph_choice_behav_dic = {'raster': True, 'PSTH': True, 'wheel': True, 'ws_average': False}
                main_window.FindElement('trial_by_trial').Update(True)
            plot_master()
                
    #trial_selection_window
        if event == '-trial list-' and not trial_selection_window:
            if values['trial_by_trial']:
                trial_selection_window = window_trial_by_trial()
            else:
                trial_selection_window = window_cbox_list()
            
        if event == 'update':
            trial_dic[trial_dic['list_time_display'][graph_displayed]]['trial_dic_choice'] = values
            trial_dic[trial_dic['list_time_display'][graph_displayed]]['list_trial_display'] = [cle for cle, v in values.items() if v]
            if 'choice' in globals():
                plot_master()
        
        if event=='select_all':
            for i in values.keys():
                trial_selection_window.FindElement(i).Update(True)
                        
        if event=='deselect_all':
            for i in values.keys():
                trial_selection_window.FindElement(i).Update(False)
        
        if event=='go_trial':            
            trial_displayed = values['-TREE-'][0][1]
            graph_displayed = values['-TREE-'][0][0]
            if not 'choice' in globals():
                choice = 'behav'
                graph_choice_behav_dic = {'raster': True, 'PSTH': True, 'wheel': True, 'ws_average': False}
                main_window.FindElement('trial_by_trial').Update(True)
            plot_master()
                
    #behaviour plotting
        if event == '-behaviour plot-' or event == '-behaviour plot new fig-':
            window_trial_update(values['ws_average'])
                
            graph_choice_behav_dic = {'raster': values['display_raster'], 'PSTH':values['display_PSTH'], 'wheel': values['display_wheel'], 'ws_average': values['ws_average']}
            
            if event == '-behaviour plot-':
                choice = 'behav'
                plot_master()
            else:
                plot_master(new_fig=True, choice_temp='behav')

                
    #electrophy plotting
        if event == '-Raw data plot-' or event =='-time frequency plot-' or event == '-Raw data plot new fig-' or event == '-time frequency plot new fig-':            
            window_trial_update(values['ws_average'])
                    
            bandpass_dic = {'low': values['bp_freq_low'], 'high': values['bp_freq_high']}
            shank_dic = {'chanel0' : values['Ch_group0'], 'chanel1': values['Ch_group1'], 'both': values['Ch_groupboth']}
            ephy_path = os.path.normpath(path_dic['list_condition_path_ephy'][0])
            
            
            if event == '-Raw data plot-' or event == '-Raw data plot new fig-': #if we want to display raw data
                choice= 'ephy_raw'
                graph_dic = {'raw_data' : values['raw_data'], 'phase': values['phase'], 'ws_average': values['ws_average']}
                phase_frequency = values['phase_freq']
            else: #if we want to display time frequeny
                choice= 'ephy_time_frequency'
                graph_dic = {'hm_amplitude': values['hm_amplitude'], 'hm_power': values['hm_power'], 'rl_intensity': values['rl_intensity'], 'rl_frequency': values['rl_frequency'], 'ws_average': values['ws_average']}            
                rl_dic = {'low': values['rl_freq_low'], 'high': values['rl_freq_high']}
            
            if event == '-Raw data plot-' or event =='-time frequency plot-': #if we want to displayed it on the main fig window
                plot_master()
            
            elif event == '-Raw data plot new fig-': #if we want it on a new window
                plot_master(new_fig=True, choice_temp='ephy_raw')
            
            elif event == '-time frequency plot new fig-': #if we want it on a new window
                plot_master(new_fig=True, choice_temp='ephy_time_frequency')        
    
    except:
        pass
    
window.close()

    
