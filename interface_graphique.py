# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 15:43:25 2021

@author: Master5.INCI-NSN
"""
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.gridspec import GridSpec
import extrapy.Behaviour as B
import extrapy.Organize as og
import numpy as np
import pandas as pd
import GUI_function_working as gf
import glob
import os
import pickle
import re

def title_maker(info_exp_dic, average):
    if average:
        title = f"Mouse nb:{info_exp_dic['mice_nb']}. Number of trials used: {info_exp_dic['trial_use']}"+'\n'+\
                f"{info_exp_dic['experiment_type']}({info_exp_dic['current_time_displayed']} ms), protocol {info_exp_dic['protocol_type']}, {info_exp_dic['condition_type']}"
    else:
        title = f"Mouse nb:{info_exp_dic['mice_nb']}. Trials nb {info_exp_dic['trial_use']}"+'\n'+\
                f"{info_exp_dic['experiment_type']}({info_exp_dic['current_time_displayed']} ms), protocol {info_exp_dic['protocol_type']}, {info_exp_dic['condition_type']}"
    return title

def key_finder(key_part):
    """return the list of keys containing le value key_part"""
    return [key for key in data['raw_data'].keys() if str(key_part) in key]

def plot_maker(data, new_fig):
    
    plot_nb = 0
    for plot_choice in data['graph_dic'].values():
        if plot_choice:
            plot_nb +=1
    
    if data['shank_dic']['both']:
        chanel=[0,1]
        column=2
    elif data['shank_dic']['chanel0']:
        column=1
        chanel=[0]
    elif data['shank_dic']['chanel1']:
        column=1
        chanel=[1]
    elif data['shank_dic']['electrode']:
        if data['shank_dic']['electrode_nb'] == 'all':
            column = 4
            plot_nb = int(data['graph_dic']['raster']) + int(data['graph_dic']['PSTH']) + int(data['graph_dic']['wheel']) + 4
            chanel = [14, 9, 12, 11, 10, 13, 8, 15, 7, 0, 5, 2, 3, 4, 1, 6]         
        else:
            column=1
            chanel=[data['shank_dic']['electrode_nb']]
    
    title = title_maker(data['info_exp_dic'], data['average'])
    if new_fig:
        fig_new = plt.figure(title, constrained_layout=True)
        fig_list = [fig_new]

    else:   
        plt.figure(0, constrained_layout=True)
        fig_list = [fig]
    
    fig_list[0].suptitle(title,weight='bold')
    gs = GridSpec(plot_nb, column, figure=fig_list[0])
    ax = []
    ax_nb = 0
    for key, plot_choice in data['graph_dic'].items():
        if plot_choice:
            if key == 'raster' or key == 'PSTH' or key == 'wheel':
                if ax_nb == 0: #this is done for sharing x with the first ax
                    ax.append(fig_list[0].add_subplot(gs[ax_nb,:]))
                else:
                    ax.append(fig_list[0].add_subplot(gs[ax_nb, :], sharex=ax[0]))
                ax_nb +=1
                
    if data['shank_dic']['electrode_nb'] == 'all':
        for column_all in range(4):
            for row_all in range(ax_nb, 4+ax_nb):
                if column_all == 0 and row_all == ax_nb:
                    if ax_nb == 0:
                        ax.append(fig_list[0].add_subplot(gs[row_all, column_all]))
                    else:
                        ax.append(fig_list[0].add_subplot(gs[row_all, column_all], sharex=ax[0]))
                else:
                    ax.append(fig_list[0].add_subplot(gs[row_all, column_all], sharex=ax[0], sharey=ax[ax_nb]))

    else:
        for ax_chanel_nb in chanel:
            ax_chanel = ax_nb
            for key, plot_choice in data['graph_dic'].items(): #the two seperate loop is done to be sure the behaviour data are plot first and electrophy after
                if plot_choice:
                    if key != 'raster' and key != 'PSTH' and key != 'wheel':
                        if data['shank_dic']['both']:
                            if ax_nb == 0 and ax_chanel_nb == chanel[0]:
                               ax.append(fig_list[0].add_subplot(gs[ax_chanel, ax_chanel_nb]))
                            else:
                                ax.append(fig_list[0].add_subplot(gs[ax_chanel, ax_chanel_nb], sharex=ax[0]))
                        else:
                            if ax_nb == 0:
                                ax.append(fig_list[0].add_subplot(gs[ax_chanel, :]))
                            else:
                                ax.append(fig_list[0].add_subplot(gs[ax_chanel, :], sharex=ax[0]))
                        ax_chanel +=1
    
    plot_position = 0
    axes=ax[plot_position]
    if data['graph_dic']['raster']:
        #first subplot (Raster)
        B.scatter_lick(data['lick_data'], axes, x_label=None)
        axes.set_title('RASTER') #Raster subplot title
        trial_list = list(range(int(data['lick_data'][:,0][0]),int( data['lick_data'][:,0][-1])))
        missing_trial_list = [trial for trial in trial_list if not trial in data['lick_data'][:,0]]
        if len(missing_trial_list)>0:
            axes.scatter(([0.01]*len(missing_trial_list)), missing_trial_list, marker='o', color='red')
        plot_position +=1
    
    if data['graph_dic']['PSTH']:
        #second subplot (PSTH)
        axes=ax[plot_position]
    
        #second subplot (PSTH)
        B.psth_lick(data['lick_data'], axes) #PSTH graph 
        axes.set_ylabel('nb of occurence') #PSTH title
        axes.set_title('PSTH') #PSTH y label
        plot_position +=1
    
    if data['graph_dic']['wheel']:
        #second subplot (PSTH)
        axes=ax[plot_position]
        #third subplot (wheel speed)
        axes.plot(data['wheel_data'][:,0], data['wheel_data'][:,1])
        axes.set_ylabel('Wheel speed (cm/s)') #PSTH title
        axes.set_title('Wheel speed') #PSTH y label
        plot_position +=1
    
    for chanel_nb in chanel:
        if data['graph_dic']['raw_data']:
            axes=ax[plot_position]
            current_chanel=key_finder(chanel_nb)[0]
            gf.ephy_plot_raw_data(axes, data['raw_data'], current_chanel, data['shank_dic'])
            plot_position +=1
        
        if data['shank_dic']['electrode_nb'] != 'all':
            if data['graph_dic']['phase']:
                axes=ax[plot_position]
                current_chanel=key_finder(chanel_nb)[0]
                gf.ephy_plot_phase(axes, data['phase_data'], current_chanel, data['shank_dic'], data['phase_parameters'])
                plot_position +=1
                
            if data['graph_dic']['amplitude']:
                axes=ax[plot_position]
                current_chanel=key_finder(chanel_nb)[0]
                gf.ephy_plot_amplitude(axes, data['complex_data'][current_chanel]['amplitude_map'], 
                                       data['complex_data'][current_chanel]['extent'], current_chanel, data['shank_dic'])
                plot_position +=1
                
            if data['graph_dic']['power']:
                axes=ax[plot_position]
                current_chanel=key_finder(chanel_nb)[0]
                gf.ephy_plot_power(axes, data['complex_data'][current_chanel]['power_map'], 
                                   data['complex_data'][current_chanel]['extent'], current_chanel, data['shank_dic'])
                plot_position +=1
                
            if data['graph_dic']['intensity']:
                axes=ax[plot_position]
                current_chanel=key_finder(chanel_nb)[0]
                gf.ephy_plot_intensity(axes, data['data_ridge_line'][current_chanel]['map_times'][:-1], 
                                       data['data_ridge_line'][current_chanel]['ridge'], current_chanel, data['shank_dic'])
                plot_position +=1
                
            if data['graph_dic']['frequency']:
                axes=ax[plot_position]
                current_chanel=key_finder(chanel_nb)[0]
                gf.ephy_plot_frequency(axes, data['data_ridge_line'][current_chanel]['map_times'][:-1], 
                                       data['data_ridge_line'][current_chanel]['y'], current_chanel, data['shank_dic'])
                plot_position +=1
    
    axes.set_xlabel('Time (s)') #PSTH x label 
    
    reward_time = data['info_exp_dic']['current_time_displayed'][-3:]
    current_reward_time=2.05+(float(reward_time)/1000) #determine when the reward happen depending of the keys of the dictionary
    if plot_nb >1 or data['shank_dic']['both']:
        for subplot in ax:
            subplot.axvspan(0,0.5, facecolor="green", alpha=0.3)
            subplot.axvspan(1.5,2, facecolor="green", alpha=0.3)
            subplot.axvspan(current_reward_time,current_reward_time+0.15, facecolor="red", alpha=0.3)
            subplot.set_xlim([data['axis_scale']['xmin'], data['axis_scale']['xmax']])
    else:
        axes.axvspan(0,0.5, facecolor="green", alpha=0.3)
        axes.axvspan(1.5,2, facecolor="green", alpha=0.3)
        axes.axvspan(current_reward_time,current_reward_time+0.15, facecolor="red", alpha=0.3)
        axes.set_xlim([data['axis_scale']['xmin'], data['axis_scale']['xmax']])    
    
    fig_list[0].subplots_adjust(hspace=.5)
    plt.draw()
                                                #########################
                                                #######PLOT MASTER#######
                                                #########################     
def plot_master(data, trial_dic, new_fig=False):
    global fig
    
    if not new_fig:
        if plt.fignum_exists(fig.number):
            plt.figure(0)
            plt.clf()
        
        else: 
            fig = plt.figure(0)
            fig.canvas.set_window_title('Main Figure')
    
    data['info_exp_dic']['current_time_displayed'] = trial_dic['list_time_display'][trial_dic['time_displayed']]
    data['axis_scale'] = {'xmin':0, 'xmax':9}
        
    if data['average']:
        data['info_exp_dic']['trial_use'] = len(trial_dic[data['info_exp_dic']['current_time_displayed']]['list_trial_display'])
    else:
        data['info_exp_dic']['trial_use'] = trial_dic[data['info_exp_dic']['current_time_displayed']]['list_trial_display'][trial_dic['trial_displayed']]
    
    
    if data['graph_dic']['raster'] or data['graph_dic']['PSTH']:
        #function that calculate evrything we need to plot for lick_file
        data['lick_data'] = gf.lick_data_calc(trial_dic, data['info_exp_dic']['trial_use'], data['info_exp_dic']['current_time_displayed'], data['average'])

    if data['graph_dic']['wheel']:
        #function that calculate evryting we need to plot wheel speed
        data['wheel_data'],_=gf.wheel_speed(data['path_dic']['coder_path'], trial_dic[data['info_exp_dic']['current_time_displayed']]['trial_dic_choice'])
    
    if data['graph_dic']['raw_data'] or data['graph_dic']['phase'] or data['graph_dic']['amplitude'] or data['graph_dic']['power'] or data['graph_dic']['intensity'] or data['graph_dic']['frequency']:
        #function that calculate evryting we need to plot raw data
        data['ephy_data'], data['raw_data']=gf.ephy_data_calc(data, trial_dic, data['info_exp_dic']['current_time_displayed'])
    
    if data['graph_dic']['phase'] or data['graph_dic']['amplitude'] or data['graph_dic']['power'] or data['graph_dic']['intensity'] or data['graph_dic']['frequency']:
        data['complex_data']=gf.calc_complex(data['ephy_data'], data['average'], data['time_frequency_parameters'])
        
    if data['graph_dic']['phase']:
        #function that calculate evryting we need to plot instantanious phase
        data['phase_data']=gf.calc_phase(data['complex_data'], data['phase_parameters'])
        
    if data['graph_dic']['intensity'] or data['graph_dic']['frequency']:
        data['data_ridge_line'] = gf.ridge_line_calc(data['complex_data'], data['time_frequency_parameters'], data['graph_dic']['power'])       
        
    plot_maker(data, new_fig)
    
    return data    
                                              ######################
                                              ###TRIAL LIST MAKER###
                                              ######################
def trial_list_maker (data, trial_dic):
    try:
        lick_data_temp = og.remove_empty_trials(data['path_dic']['lick_path'])
    except:
        window.FindElement('protocole').Update('')
        window.FindElement('condition').Update('')
        sg.popup_error('Lick file is empty')
    
    else:
        if data['info_exp_dic']['condition_type'] == 'No Stim':
            nb_trials= [1,30]
        elif data['info_exp_dic']['condition_type'] == 'Stim':
            nb_trials= [31,60]
        else:
            last_trial_nb = lick_data_temp[:,0]
            nb_trials=[1, int(last_trial_nb[-1])]
            
        if data['info_exp_dic']['experiment_type'] == 'Fixed Delay': 
            trial_data ={}
            for i in range(nb_trials[0],nb_trials[1]+1):
                index = np.where(lick_data_temp[:,0] == i)
                if index[0].size > 0:
                    trial_data[i]= np.array([[lick_data_temp[i,0],lick_data_temp[i,1]] for i in index[0]])
            trial_dic_choice = {i: True for i in trial_data.keys()}
            list_trial_display = [cle for cle, v in trial_dic_choice.items() if v]
            trial_dic['500']= {'trial_data':trial_data, 'trial_dic_choice':trial_dic_choice, 'list_trial_display': list_trial_display}
            trial_dic['list_time_display']=['500']
        
        elif data['info_exp_dic']['experiment_type'] == 'Random Delay' or data['info_exp_dic']['experiment_type'] == 'Training':
            random_delay=B.extract_random_delay(data['path_dic']['param_path'])
            delays, licks_by_delay = B.separate_by_delay(random_delay, lick_data_temp)
            
            for cle in delays.keys():
                if data['dic_graph_choice_time'][cle]:
                    trial_data ={}
                    for i in range(nb_trials[0],nb_trials[1]+1):
                        index = np.where(licks_by_delay[cle][:,0] == i)
                        if index[0].size > 0:
                            trial_data[i]= np.array([[licks_by_delay[cle][i,0],licks_by_delay[cle][i,1]] for i in index[0]])
                     
                        trial_dic_choice = {i: True for i in trial_data.keys()}
                        list_trial_display = [cle for cle, v in trial_dic_choice.items() if v]
                        trial_dic[cle]= {'trial_data':trial_data, 'trial_dic_choice':trial_dic_choice, 'list_trial_display':list_trial_display}
            
            trial_dic['list_time_display']= [cle for cle, value in data['dic_graph_choice_time'].items() if value]
                 
        return trial_dic

                                                    ###############################
                                                    ######TRIAL LIST WINDOWS#######
                                                    ###############################
def window_cbox_list(trial_dic, location=(650,0)): 
    
    current_time_displayed = trial_dic['list_time_display'][trial_dic['time_displayed']]
    
    cbox_list =[]
    for i, value in trial_dic[current_time_displayed]['trial_dic_choice'].items():
        cbox_list.append([sg.Checkbox(f'Trial nb: {i}', default=value, enable_events=True, key=i)])
    
    layout = [[sg.Column(cbox_list, size=(285, 500), scrollable=True,  vertical_scroll_only=True)], 
              [sg.Button('Update', key= 'update'), sg.Button('Select all', key='select_all'), sg.Button('Deselect all', key='deselect_all')],
              [sg.Button('Select taged trials', key= 'select_taged_update'),sg.Button('Deselect taged trials', key= 'deselect_taged_update')]] 
    
    return sg.Window(fr'{current_time_displayed}ms', layout, location = location, finalize=True)

def window_trial_by_trial(data, location=(650,0)):
    
    treedata = sg.TreeData()
    if data['info_exp_dic']['experiment_type'] != 'Fixed Delay':
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

def window_trial_update(data, trial_dic, average):
    global trial_selection_window
    if trial_selection_window:
        location = trial_selection_window.CurrentLocation()
        trial_selection_window.close()
        if average:
            trial_selection_window = window_cbox_list(trial_dic, location)
        else:
            trial_selection_window = window_trial_by_trial(data, location)

                                                    #########################
                                                    #####TAG LIST WINDOW#####
                                                    #########################
def window_tag_list_maker(location=(650,0)):
    #os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))
    os.chdir(os.path.dirname('C:\\Users\\Master5.INCI-NSN\\Desktop\\Pierre\\data'))
    
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

                                                ##############################
                                                ######SELECTION TOOLBOX#######
                                                ##############################
def window_selection_toolbox_maker(location=(650,0)):
    layout = [[sg.Button('Enable selection', key='enable_selection'), sg.Text('X1:'), sg.InputText('', key='x1', size=(6,1)), sg.Text('X2:'), sg.InputText('', key='x2', size=(6,1))],
              [sg.Button('Disable selection', key='disable_selection'), sg.Text('Y1:'), sg.InputText('', key='y1', size=(6,1)), sg.Text('Y2:'), sg.InputText('', key='y2', size=(6,1))],
              [sg.Button('Go to selection', key='go_to_selection'), sg.Button('Save power map', key='save_power_map')]]
    return sg.Window('Selection toolbox', layout, location = location, finalize=True)

def round_float(number, nb_decimal = 1):
    """ this function remouve the numbers after the first relevent number
        for exemple: round_float(5.16784) --> 5.2, round_float(5.16784,nb_decimal=2) --> 5.17
                     round_float(0.0004875468) -->0.00049
    """
    return float('{:0.1e}'.format(number)) 

def coordinate_master(x1, y1, x2, y2, ax):
    global current_coordinate
    
    title = re.match(r".*'(.*)'.*", str(ax.title))[1]
    current_coordinate = {'title': title, 'ax':ax}
    
    window_selection_toolbox.FindElement('x1').Update(x1)
    window_selection_toolbox.FindElement('y1').Update(y1)
    window_selection_toolbox.FindElement('x2').Update(x2)
    window_selection_toolbox.FindElement('y2').Update(y2)

def line_select_callback(eclick, erelease):

    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    coordinate_master(round_float(x1), round_float(y1), round_float(x2), round_float(y2), eclick.inaxes)

def selection_master(enable=True):
    global interactive_selection
    
    if enable:
        interactive_selection = []
        for ax in fig.axes:
            interactive_selection.append(RectangleSelector(ax, line_select_callback,
                                                           drawtype='box', useblit=False,
                                                           button=[1, 3],  # don't use middle button
                                                           minspanx=5, minspany=5,
                                                           spancoords='pixels',
                                                           interactive=True))  
    else:
        #this is use to remove the current rectangle selector from the graph (same thing as press escape button)
        for rectangle in interactive_selection:
            for artist in rectangle.artists:
                artist.set_visible(False)
            rectangle.update()       
        #interactive_selection is deletate to disable the abiliti to trace new rectangle selector
        del interactive_selection
        
        # all the selected coordinate are remove from the gui
        window_selection_toolbox.FindElement('x1').Update('')
        window_selection_toolbox.FindElement('y1').Update('')
        window_selection_toolbox.FindElement('x2').Update('')
        window_selection_toolbox.FindElement('y2').Update('')
 
def selection_plot(data):
    plt.clf()
    
    if 'current_coordinate' in globals():
        if 'Power' in current_coordinate['title'] or 'Amplitude' in current_coordinate['title']: 
            data['complex_data'] = gf.ephy_data_selection(data['complex_data'], current_coordinate)
        else:
             data['complex_data'] = gf.ephy_data_selection(data['complex_data'], current_coordinate)
                
        data['axis_scale'] = {'xmin':current_coordinate['x1'], 'xmax':current_coordinate['x2']}                       
        plot_maker(data, new_fig=False)

        return data
def selection_save(path_save_selection, data):
    w = pd.ExcelWriter(fr'{path_save_selection}.xlsx')
    if 'complex_data' in data:
        for shank in data['complex_data']:
            columns_name = np.arange(data['complex_data'][shank]['freqs'][0], data['complex_data'][shank]['freqs'][-1]+data['complex_data'][shank]['delta_freq'], data['complex_data'][shank]['delta_freq'])
            power_to_excel = pd.DataFrame(data['complex_data'][shank]['power_map'], index=data['complex_data'][shank]['map_times'], columns=columns_name)
            power_to_excel.to_excel(w, sheet_name=f"Median,{shank},{data['info_exp_dic']['current_time_displayed']}".replace(' ','_'))
            if 'power_MAD' in data['complex_data'][shank].keys():
                MAD_power_to_excel = pd.DataFrame(data['complex_data'][shank]['power_MAD'], index=data['complex_data'][shank]['map_times'], columns=columns_name)
                MAD_power_to_excel.to_excel(w, sheet_name=f"MAD,{shank},{data['info_exp_dic']['current_time_displayed']}".replace(' ','_'))
        w.save()
    else:
         sg.popup_error('No power map found')
                                                ###################
                                                #####MAIN GUI######
                                                ###################
def main_window():
    rd_column1=[[sg.Checkbox('Raw data', default=False, key='raw_data', enable_events=True)],[sg.Checkbox('Instantaneous phase', default=False, key='phase', enable_events=True)]]
    
    rd_column2=[[sg.Frame(layout=[
                [sg.Text('phase frequency (Hz):'), sg.Input(4, key='phase_freq', size=(5,1), enable_events=True)]]
                ,title='Phase parameters', title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='minimun and maximum frequency available is defined by the time frequency parameters')]]
    
    #raw data
    tab1 = [[sg.Column(rd_column1),sg.Column(rd_column2)]]
    
    
    #column for time frequency plots
    tf_column1 = [[sg.Text('Scalogram', justification='center', size=(10, 1))],
                [sg.Checkbox('Amplitude', default=False, key='hm_amplitude', enable_events=True)],
                [sg.Checkbox('Power', default=False, key='hm_power', enable_events=True)]]      
    
    tf_column2 = [[sg.Text('Ridge line', justification='center', size=(10, 1))],
                [sg.Checkbox('Intensity', default=False, key='rl_intensity', enable_events=True)],
                [sg.Checkbox('Frequency', default=False, key='rl_frequency', enable_events=True)]]
    
    tf_column3=[[sg.Frame(layout=[
                [sg.Text('high (Hz):'), sg.Input(30,key='tf_freq_high', size=(5,1), enable_events=True)], [sg.Text('low  (Hz):'), sg.Input(0,key='tf_freq_low', size=(5,1), enable_events=True)]]
                ,title='Frequency parameters', title_color='red', relief=sg.RELIEF_SUNKEN)]]
    
    #time frequency
    tab2 = [[sg.Column(tf_column1),sg.Column(tf_column2),sg.Column(tf_column3)]]   
    
    random_section = [[sg.Frame(layout=[      
                [sg.Checkbox('400', default=True, key='400', enable_events=True), sg.Checkbox('400_400', default=False, key='400_400', enable_events=True), \
                sg.Checkbox('900_400', default=False, key='900_400', enable_events=True), sg.Checkbox('400_400_400', default=False, key='400_400_400', enable_events=True), \
                sg.Checkbox('900_400_400', default=False, key='900_400_400', enable_events=True)],[sg.Checkbox('900', default=True, key='900', enable_events=True), \
                sg.Checkbox('900_900', default=False, key='900_900', enable_events=True), sg.Checkbox('400_900', default=False, key='400_900', enable_events=True), sg.Checkbox('900_900_900', default=False, key='900_900_900', enable_events=True), \
                sg.Checkbox('400_900_900', default=False, key='400_900_900', enable_events=True)]],\
                title='trial to display',title_color='red', relief=sg.RELIEF_SUNKEN, tooltip='Last number is the current reward time')]]
    
    shank_selection_section = [[sg.Frame(layout=[[sg.Radio('Chanel 0','radio_shank', key='Ch_group0', default=False, enable_events=True), sg.Radio('Chanel 1','radio_shank',key='Ch_group1', default=False, enable_events=True), sg.Radio('Both','radio_shank',key='Ch_groupboth', default=True, enable_events=True)]]
                                         ,title='Shank selection',title_color='red', relief=sg.RELIEF_SUNKEN, pad=(0,10))]]
    
    electrode_list = ['All electrodes', 'Shank 1: 14','Shank 1: 9','Shank 1: 12','Shank 1: 11','Shank 1: 10','Shank 1: 13','Shank 1: 8','Shank 1: 15',
                     'Shank 2: 7','Shank 2: 0','Shank 2: 5','Shank 2: 2','Shank 2: 3', 'Shank 2: 4','Shank 2: 1','Shank 2: 6']
    
    electrode_selection_section = [[sg.Frame(layout=[[sg.InputCombo(values=electrode_list, default_value=electrode_list[0], size=(15, 1), key='electrode_nb', enable_events=True)]]
                                         ,title='Electrode selection',title_color='red', relief=sg.RELIEF_SUNKEN, pad=(0,10))]]
                
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
                [sg.Button('Clear plot', key='-clear plot-', button_color=('red','white')), sg.Button('Selection toolbox',  key='Selection_toolbox')],
                #Behaviour
                [sg.Text('_'  * 80)], [sg.Text('Behaviour', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE)], 
                [sg.Frame(layout=[      
                [sg.Checkbox('Raster', default=False, key='display_raster', enable_events=True), sg.Checkbox('PSTH', default=False, key='display_PSTH', enable_events=True), \
                sg.Checkbox('Wheel speed', default=False, key='display_wheel', enable_events=True)]], title='Graph to display',title_color='red', relief=sg.RELIEF_SUNKEN)],
                #Electrophy
                [sg.Text('_'  * 80)], 
                [sg.Text('Electrophysiology', size=(30, 1), justification='center', font=("Helvetica", 13), relief=sg.RELIEF_RIDGE), 
                 sg.Radio('By shank', 'radio_electrode', key='radio_by_shank', default=True, enable_events=True), sg.Radio('By electrode', 'radio_electrode', key='radio_by_electrode', default=False, enable_events=True)],
                #truc
                [sg.Frame(layout=[
                [sg.Text('low (Hz):'), sg.Input(0,key='bp_freq_low', size=(5,1), enable_events=True), sg.Text('high (Hz):'), sg.Input(4000,key='bp_freq_high', size=(5,1), enable_events=True)]] 
                ,title='Bandpass filter', title_color='red', relief=sg.RELIEF_SUNKEN), sg.Text(''), sg.pin(sg.Column(shank_selection_section, key='shank_selection_section')), sg.pin(sg.Column(electrode_selection_section, key='electrode_selection_section', visible=False))],    
                #whole session average
                [sg.TabGroup([[sg.Tab('Raw data', tab1), sg.Tab('Time frequency', tab2)]])],
                [sg.Button('Display plot', key='-plot-'),sg.Button('Display plot on a new figure', key='-plot new fig-')]]
    return sg.Window('', layout, location=(0,0), finalize=True)
     
            

fig = plt.figure(0)
fig.canvas.set_window_title('Main Figure')
fig.subplots(1)
data = {'graph_dic':{'raster':False, 'PSTH':False, 'wheel':False, 'raw_data':False, 'phase':False, 'amplitude':False, 'power':False, 'intensity':False, 'frequency':False},
        'info_exp_dic':{'group_nb':'', 'mice_nb':'', 'experiment_type':'Random Delay', 'protocol_type':'', 'condition_type':''},
        'dic_graph_choice_time':{"400":True,"400_400":False,"900_400":False,"400_400_400":False,"900_400_400":False,"900":True,"900_900":False,"400_900":False,"900_900_900":False,"400_900_900":False},
        'shank_dic': {'chanel0':False, 'chanel1':False, 'both':True, 'electrode': False, 'electrode_nb': None},
        'path_dic': {'ephy_path':'', 'lick_path':'', 'param_path':'', 'coder_path':''},
        'bandpass_dic': {'low':0, 'high':4000},
        'phase_parameters': 4,
        'time_frequency_parameters': {'low':0, 'high': 30},
        'average':True
        }                  
list_condition = ['No Stim', 'Stim']


sg.theme('DarkBlue')

main_window, trial_selection_window,  window_tag_list, window_selection_toolbox = main_window(), None, None, None        # start off with 1 window open

while True:
    window, event, values = sg.read_all_windows()
    
    try:
        if event == sg.WIN_CLOSED:	# if user closes window or clicks cancel
            window.close()
            if window == trial_selection_window:
                trial_selection_window = None
            elif window == window_tag_list:
                window_tag_list = None
            elif window == window_selection_toolbox:
                selection_master(enable=False)
                window_selection_toolbox = None
            elif window == main_window:
                break
        
    #File sorting
        if event == '-load-':
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])

            window.FindElement('group_nb').Update(values=path_dic["list_group"])
            
            window.FindElement('mice_nb').Update(values=path_dic["list_mice"])
                     
            window.FindElement('condition').Update(values=list_condition)
        
        if event == '-clear plot-':
            plt.clf() 
            ax = fig.subplots(1)
            plt.draw()
            
        if event == 'group_nb':
            data['info_exp_dic']['group_nb']=values['group_nb']
                    
            data['info_exp_dic']['mice_nb']=''
            window.Element('mice_nb').Update(data['info_exp_dic']['mice_nb'])
            
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
                
            window.FindElement('mice_nb').Update(values=path_dic["list_mice"])            
            
        
        if event == 'mice_nb':
            data['info_exp_dic']['mice_nb']=values['mice_nb']
            data['info_exp_dic']['protocol_type'] = ''
            window.Element('protocole').Update(data['info_exp_dic']['protocol_type'])
            data['info_exp_dic']['condition_type'] = ''
            window.Element('condition').Update(data['info_exp_dic']['condition_type'])

            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            
            window.FindElement('protocole').Update(values=path_dic["list_protocol"])
            
        if event == 'radio_fixe':
            data['info_exp_dic']['experiment_type'] = 'Fixed Delay'
            data['info_exp_dic']['protocol_type'] = ''
            window.Element('protocole').Update(data['info_exp_dic']['protocol_type'])
            data['info_exp_dic']['condition_type'] = ''
            window.Element('condition').Update(data['info_exp_dic']['condition_type'])
            
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            window['random_section'].update(visible=False)
            
            window.FindElement('protocole').Update(values=path_dic["list_protocol"])
            
            window.FindElement('condition').Update(values=list_condition)

        if event == 'radio_random':
            data['info_exp_dic']['experiment_type'] = 'Random Delay'
            data['info_exp_dic']['protocol_type'] = ''
            window.Element('protocole').Update(data['info_exp_dic']['protocol_type'])
            data['info_exp_dic']['condition_type'] = ''
            window.Element('condition').Update(data['info_exp_dic']['condition_type'])
            
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            window['random_section'].update(visible=True)
            
            window.FindElement('protocole').Update(values=path_dic["list_protocol"])
            
            window.FindElement('condition').Update(values=list_condition)
    
        if event == 'radio_training':
            data['info_exp_dic']['experiment_type'] = 'Training'
            data['info_exp_dic']['protocol_type'] = ''
            window.Element('protocole').Update(data['info_exp_dic']['protocol_type'])
            data['info_exp_dic']['condition_type'] = ''
            window.Element('condition').Update(data['info_exp_dic']['condition_type'])
            
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            window['random_section'].update(visible=True)
            
            window.FindElement('protocole').Update(values=path_dic["list_protocol"])
            
            window.FindElement('condition').Update(values=['No Stim'])
                        
        
        if event == 'protocole':
            data['info_exp_dic']['condition_type'] = ''
            window.Element('condition').Update(data['info_exp_dic']['condition_type'])
            
            data['info_exp_dic']['protocol_type'] = values['protocole']
            
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            
            if data['info_exp_dic']['protocol_type'] == 'NB' or data['info_exp_dic']['protocol_type'] == 'P0' or data['info_exp_dic']['protocol_type'] == 'Training':
                window.FindElement('condition').Update(values=['No Stim'])
            
            else:
                window.FindElement('condition').Update(values=list_condition)

        # all the experiment paramaters are fill so we can load and pretreate the data
        if event == 'condition':
            data['info_exp_dic']['condition_type'] = values['condition']
            path_dic = gf.path_finder(values['main_folder'], data['info_exp_dic'])
            
            data['path_dic']['lick_path']=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.lick'))
            data['path_dic']['param_path']=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.param'))
            data['path_dic']['coder_path']=glob.glob(os.path.join(path_dic['list_protocol_path_behaviour'][0], '*.coder'))

            data['path_dic']['lick_path'] = os.path.normpath(data['path_dic']['lick_path'][0])
            data['path_dic']['param_path'] = os.path.normpath(data['path_dic']['param_path'][0])
            data['path_dic']['coder_path'] = os.path.normpath(data['path_dic']['coder_path'][0])
            data['path_dic']['ephy_path'] = os.path.normpath(path_dic['list_condition_path_ephy'][0]) 

            if values['radio_training'] or values['protocole']== 'NB' or values['protocole']== 'P0':
                data['info_exp_dic']['condition_type']= 'all'
                
            trial_dic = {}
            trial_dic['time_displayed'] = 0 #we start by displaying the first time delay
            trial_dic['trial_displayed'] = 0 #we start by displaying the first trail
            trial_dic = trial_list_maker(data, trial_dic)
            list_trial = trial_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]['list_trial_display']
         
            
            window_trial_update(data, trial_dic, values['ws_average'])
            window_tag_update()
        
        if event == '400' or event == '400_400' or event == '900_400' or event == '900_400' or event == '400_400_400' or event == '900_400_400' or event == '900'or event == '900_900'or event == '400_900'or event == '900_900_900'or event == '400_900_900':
            data['dic_graph_choice_time'] = {"400":values['400'],"400_400":values['400_400'],"900_400":values['900_400'],"400_400_400":values['400_400_400'],
                         "900_400_400":values['900_400_400'],"900":values['900'],"900_900":values['900_900']
                         ,"400_900":values['400_900'],"900_900_900":values['900_900_900'],"400_900_900":values['400_900_900']}
            
            if data['info_exp_dic']['condition_type'] !='':
                trial_dic = trial_list_maker(data)
                window_trial_update(data, trial_dic, values['ws_average'])
        
        if event =='ws_average' or event == 'trial_by_trial':
            data['average'] = values['ws_average']
            window_trial_update(data, trial_dic, values['ws_average'])
            
        if event=='next': 
            if values['trial_by_trial']:
                if trial_dic['trial_displayed']+1 < len(list_trial):
                    trial_dic['trial_displayed'] +=1
                    data = plot_master(data, trial_dic)
                
                else:
                    if trial_dic['time_displayed']+1 < len(trial_dic['list_time_display']):  
                        trial_dic['trial_displayed'] =0
                        trial_dic['time_displayed'] +=1
                        data = plot_master(data, trial_dic)
                    
            else:
                if trial_dic['time_displayed']+1 < len(trial_dic['list_time_display']):                
                    trial_dic['time_displayed'] +=1
                    data = plot_master(data, trial_dic)
            
                window_trial_update(data, trial_dic, values['ws_average'])
                
        
        if event=='previous':
            if values['trial_by_trial']:
                if trial_dic['trial_displayed'] > 0:
                    trial_dic['trial_displayed'] -=1
                    data = plot_master(data, trial_dic)     
                else:
                    if trial_dic['time_displayed'] > 0:
                        trial_dic['time_displayed'] -=1
                        trial_dic['trial_displayed'] =len(trial_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]['list_trial_display'])-1 #this will give the nb of the last position of the trial list in order to display the last trial of the previous time
                        data = plot_master(data, trial_dic)
            else:
                if trial_dic['time_displayed'] > 0:
                    trial_dic['time_displayed'] -=1
                    data = plot_master(data, trial_dic)
                
                window_trial_update(data, trial_dic, values['ws_average'])
        
        if event=='tag':
            if values['trial_by_trial']:
                    #os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))
                    os.chdir(os.path.dirname('C:\\Users\\Master5.INCI-NSN\\Desktop\\Pierre\\data'))
                    if os.path.exists('taged_trials.txt'):
                        with open ('taged_trials.txt', 'rb') as tag_trials_file:
                            my_depickler = pickle.Unpickler(tag_trials_file)
                            tag_trials_dic = my_depickler.load()
                    else:
                        tag_trials_dic = {}
                    
                    
            # trial_dic['list_time_display'][trial_dic['time_displayed']] = curent time display (i dont want it to be global)
            # list_trial[trial_dic['trial_displayed']] = current trial display  (i dont want it to be global)  
                    if trial_dic['list_time_display'][trial_dic['time_displayed']] not in tag_trials_dic:
                        tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]=[]
                        
                    if list_trial[trial_dic['trial_displayed']] not in tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]:
                        tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]].append(list_trial[trial_dic['trial_displayed']])
                    
                    else:
                        pass
                    
                    with open ('taged_trials.txt', 'wb') as tag_trials_file:
                        my_pickler = pickle.Pickler(tag_trials_file)
                        my_pickler.dump(tag_trials_dic)
                    
                    window_tag_update()


        if event=='untag':
            if values['trial_by_trial']:
                    #os.chdir(os.path.dirname(path_dic['list_condition_path_ephy'][0]))
                    os.chdir(os.path.dirname('C:\\Users\\Master5.INCI-NSN\\Desktop\\Pierre\\data'))
                    if os.path.exists('taged_trials.txt'):
                        with open ('taged_trials.txt', 'rb') as tag_trials_file:
                            my_depickler = pickle.Unpickler(tag_trials_file)
                            tag_trials_dic = my_depickler.load()
                        
                        if trial_dic['list_time_display'][trial_dic['time_displayed']] in tag_trials_dic:
                            if list_trial[trial_dic['trial_displayed']] in tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]:
                                tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]].remove(list_trial[trial_dic['trial_displayed']])
                            
                            if len(tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]])==0:
                                del tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]
                        
                        with open ('taged_trials.txt', 'wb') as tag_trials_file:
                            my_pickler = pickle.Pickler(tag_trials_file)
                            my_pickler.dump(tag_trials_dic)
                    
                        window_tag_update()
                                
                    else:
                        pass
        
        if event == '-tag list-' and not window_tag_list:
            window_tag_list = window_tag_list_maker()
        
        if event == 'go_tag':
            if not values['-TREE-'][0][0] in trial_dic['list_time_display']:    #if we want to display a trial when we didn't selected the coresponding time (400_900 for exemple) we need to tick the corresponding checkbox as well as remaking the trial_dic in order to include the data of that time
                main_window.FindElement(values['-TREE-'][0][0]).Update(True)
                data['dic_graph_choice_time'][values['-TREE-'][0][0]]=True
                trial_dic = trial_list_maker(data, trial_dic)
                window_trial_update(data, trial_dic, False) #we refresh the trial list if open because we had a time in it
                
            trial_dic['time_displayed'] = trial_dic['list_time_display'].index(values['-TREE-'][0][0])
            trial_dic['trial_displayed'] = trial_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]['list_trial_display'].index(values['-TREE-'][0][1])
           
            data['average']=False
            main_window.FindElement('trial_by_trial').Update(True)
            
            if not True in [value for value in data['graph_dic'].values()]:
                main_window.FindElement('display_raster').Update(True)
                data['graph_dic']['raster']=True
                
            data = plot_master(data, trial_dic)
            
        if event == 'display_raster' or event == 'display_PSTH' or event == 'display_wheel' or event == 'raw_data' or event == 'phase' or event == 'hm_amplitude' or event == 'hm_power' or event == 'rl_intensity' or event == 'rl_frequency':
            data['graph_dic'] = {'raster':values['display_raster'], 'PSTH':values['display_PSTH'], 'wheel':values['display_wheel'], 
                               'raw_data':values['raw_data'], 'phase':values['phase'], 'amplitude':values['hm_amplitude'], 
                               'power':values['hm_power'], 'intensity':values['rl_intensity'], 'frequency':values['rl_frequency']}
        
        if event == 'bp_freq_low' or event == 'bp_freq_high':
            data['bandpass_dic'] = {'low': int(values['bp_freq_low']), 'high': int(values['bp_freq_high'])}
        
        if event == 'radio_by_shank':
            window['electrode_selection_section'].update(visible=False)
            window['shank_selection_section'].update(visible=True)
            data['shank_dic'].update({'chanel0':values['Ch_group0'], 'chanel1':values['Ch_group1'], 'both':values['Ch_groupboth'], 'electrode':values['radio_by_electrode']})
        
        if event == 'Ch_group0' or event == 'Ch_group1' or event == 'Ch_groupboth':
            data['shank_dic'].update({'chanel0' : values['Ch_group0'], 'chanel1': values['Ch_group1'], 'both': values['Ch_groupboth']})
        
        if event == 'radio_by_electrode':
            window['shank_selection_section'].update(visible=False)
            window['electrode_selection_section'].update(visible=True)
            if values['electrode_nb'] == 'All electrodes':
                data['shank_dic'].update({'chanel0':values['radio_by_shank'], 'chanel1':values['radio_by_shank'], 'both':values['radio_by_shank'], 'electrode':values['radio_by_electrode'], 'electrode_nb':'all'})
            else:
                data['shank_dic'].update({'chanel0':values['radio_by_shank'], 'chanel1':values['radio_by_shank'], 'both':values['radio_by_shank'], 'electrode':values['radio_by_electrode'], 'electrode_nb':int(values['electrode_nb'].split(' ')[-1])})
        
        if event == 'electrode_nb':
            if values['electrode_nb'] == 'All electrodes':
                data['shank_dic']['electrode_nb']='all'
                
            else:
                data['shank_dic']['electrode_nb']=int(values['electrode_nb'].split(' ')[-1])

        if event == 'phase_freq':
            data['phase_parameters'] = int(values['phase_freq'])
        
        if event == 'tf_freq_low' or event == 'tf_freq_high':
            data['time_frequency_parameters'] = {'low': int(values['tf_freq_low']), 'high': int(values['tf_freq_high'])}
            
    #trial_selection_window
        if event == '-trial list-' and not trial_selection_window:
            if trial_selection_window:
                location = trial_selection_window.CurrentLocation()
                trial_selection_window.close()
            else:
                location = (650,0)
            if values['ws_average']:
                trial_selection_window = window_cbox_list(trial_dic, location)
            else:
                trial_selection_window = window_trial_by_trial(data, location)
            
        if event == 'update':
            trial_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]['trial_dic_choice'] = values
            trial_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]['list_trial_display'] = [cle for cle, v in values.items() if v]
            if len(fig.get_children()) <=1:
                if not data['average']:
                    data['average']=True
                data = plot_master(data, trial_dic)
        
        if event=='select_all':
            for i in values.keys():
                trial_selection_window.FindElement(i).Update(True)
                        
        if event=='deselect_all':
            for i in values.keys():
                trial_selection_window.FindElement(i).Update(False)
        
        if event=='go_trial':            
            trial_dic['trial_displayed'] = values['-TREE-'][0][1]
            trial_dic['time_displayed'] = values['-TREE-'][0][0]        
            main_window.FindElement('trial_by_trial').Update(True)

            data = plot_master(data, trial_dic)
        
        if event=='select_taged_update':
            os.chdir(os.path.dirname('C:\\Users\\Master5.INCI-NSN\\Desktop\\Pierre\\data'))
            if os.path.exists('taged_trials.txt'):
                with open ('taged_trials.txt', 'rb') as tag_trials_file:
                    my_depickler = pickle.Unpickler(tag_trials_file)
                    tag_trials_dic = my_depickler.load()
                if trial_dic['list_time_display'][trial_dic['time_displayed']] in tag_trials_dic:   
                    for i in values.keys():
                        if i in tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]:
                            trial_selection_window.FindElement(i).Update(True)
                        else:
                            trial_selection_window.FindElement(i).Update(False)
                else:
                    sg.popup_error('No tag trial found')
            else:
                sg.popup_error('No tag trial found')
                    
        if event=='deselect_taged_update':
            os.chdir(os.path.dirname('C:\\Users\\Master5.INCI-NSN\\Desktop\\Pierre\\data'))
            if os.path.exists('taged_trials.txt'):
                with open ('taged_trials.txt', 'rb') as tag_trials_file:
                    my_depickler = pickle.Unpickler(tag_trials_file)
                    tag_trials_dic = my_depickler.load()
                
                if trial_dic['list_time_display'][trial_dic['time_displayed']] in tag_trials_dic: 
                    for i in values.keys():
                        if i in tag_trials_dic[trial_dic['list_time_display'][trial_dic['time_displayed']]]:
                            trial_selection_window.FindElement(i).Update(False)
                        else:
                            trial_selection_window.FindElement(i).Update(True)
                else:
                    sg.popup_error('No tag trial found')
            else:
                sg.popup_error('No tag trial found')
    #window_selection_toolbox
        if event=='Selection_toolbox':
             window_selection_toolbox = window_selection_toolbox_maker()   
       
        if event == 'enable_selection':
            selection_master()
        
        if event == 'disable_selection':
            selection_master(enable=False)
            
        if event == 'go_to_selection':
            current_coordinate.update({'x1':float(values['x1']), 'y1':float(values['y1']), 'x2':float(values['x2']), 'y2':float(values['y2'])})
            data = selection_plot(data)
        
        if event == 'save_power_map':
            path_save_selection = sg.popup_get_file('', no_window=True, save_as=True, 
                                                    default_path=f"mice nb{data['info_exp_dic']['mice_nb']}, {data['info_exp_dic']['experiment_type']}, {data['info_exp_dic']['protocol_type']}, {data['info_exp_dic']['condition_type']}, {data['info_exp_dic']['current_time_displayed']}, {data['info_exp_dic']['condition_type']}")
            selection_save(path_save_selection, data)
                     
    #plotting
        if event == '-plot-' or event == '-plot new fig-':
            window_trial_update(data, trial_dic, values['ws_average'])
            
            if event == '-plot-':
                data = plot_master(data, trial_dic)
            else:
                data = plot_master(data, trial_dic, new_fig=True)            
 
    except:
        pass
    
window.close()

    