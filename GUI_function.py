# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 11:52:45 2021

@author: Master5.INCI-NSN
"""
import extrapy.Behaviour as B
import extrapy.Scalogram as scalo
import extrapy.Organize as og
import extrapy.Filters as filters
import numpy as np
from scipy.stats import median_abs_deviation as mad
from scipy.ndimage.filters import gaussian_filter1d
import glob
import os

def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value

def wheel_speed (wheel_path, trial_dic_choice):
    """
    first column is trial nb, second column is the time at which the wheel has turned, 
    the third column is the instant speed of the wheel based on the time diference between 2 position of the wheel 
    and the distance of 3.875 cm between those 2 position. 
    The first line of each trial is wrong because the previous time is attributaed to a other trial 
    and do not match
    """
    wheel = B.load_lickfile(wheel_path, wheel=True)
    v = np.array([[t,w, (3.875/(w-wheel[indx-1,1]))]for indx,(t,w) in enumerate(wheel)]) 
    """
    dic which separates the data of every trial in order for them to be averaged later. 
    the key is the trial number and the value is a ndarray of the time at which 
    the wheel changes position(first column) and the instantaneous speed at that moment (second column)
    """
    trial_dic ={}
    for i, value in trial_dic_choice.items(): 
        if value:
            index = np.where(v[:,0] == i)
            trial_dic[i]= np.array([[v[i,1],v[i,2]] for i in index[0]])

               
    """
    dic which groups the instanteneous speed of every trial into time slices (0.1 second per slice) this allows to
    average the data of evry trial (the time at wich the wheel changes position is not the same in every trial)
    """
    sampling_dic = {}
    for cle,value in trial_dic.items():
        i=0.1
        for time, speed in value:
            while True:
                if time <= i:
                    ### If we are using the median, we can avoid this further removal of outliers
                    # if speed > 150:
                    #     break # i remove the value that are above 1.5 meter/sec
                    append_value(sampling_dic, i, speed)
                    break
                else: 
                    i+=0.1
    """
    The values of every time slices are then averaged
    """
    for cle1,val1 in sampling_dic.items():
        sampling_dic[cle1] = np.median(val1)  #For the moment let's use median, this allows us to average the wheel data in the future
        
    """
    Smooth with a gaussian filter and plot the result
    """
    
    lists = sorted(sampling_dic.items()) # sorted by key, return a list of tuples
    
    x, y = zip(*lists) # unpack a list of pairs into two tuples
    
    y = gaussian_filter1d(y,sigma=2)
        
    data = np.array([[x[i],y[i]]for i in range(len(x))])
    return data, trial_dic
    
    ### This is just a different style of coding the previous lines, just to see the personal differences ###
    # lists = np.array(sorted(sampling_dic.items()))
    # y = gaussian_filter1d(lists[:,1],sigma=2)
    # return np.array(list(zip(lists[:,0],y)))
    

def path_finder(main_folder_path, info_exp_dic):
    """this function create a dictionary that contain the path to all the file need for both behaviour and electrophy. 
    we can specify which group, mice_nb, experiment type, protocole type, condition type. 
    The folder structure need to be respected for it to work properly (see Github/TeamIsope/GUI/ReadMe)    
    """
    group_nb = info_exp_dic['group_nb'].split(' ')[-1] #this is done to not load folder wich dont start by Group
    group_nb = fr'*Group {group_nb}*'
    mice_nb = fr"*{info_exp_dic['mice_nb']}"
    experiment_type = fr"*{info_exp_dic['experiment_type']}"
    protocol_type = fr"*{info_exp_dic['protocol_type']}"
    condition_type = fr"{info_exp_dic['condition_type']}"

    #first we save the path to all the folder with the name 'group_nb'
    list_group_path_ephy = glob.glob(os.path.join(main_folder_path+'/Ephy', group_nb))
    list_group_path_behaviour = glob.glob(os.path.join(main_folder_path+'/Behaviour', group_nb))      
    list_group = [os.path.basename(group)for group in list_group_path_behaviour]
    dic = {"list_group_path_ephy": list_group_path_ephy,"list_group_path_behaviour": list_group_path_behaviour,"list_group": list_group}
    
    #this if cascade is there to avoid loading evry thing at first and save a lot of loading time
    if group_nb!='*':
        #in thoses folders we save the path to all the folder with the name 'mice_nb'
        list_mice_path_ephy = [glob.glob(os.path.join(group_path, mice_nb))for group_path in list_group_path_ephy]
        list_mice_path_ephy = [item for sublist in list_mice_path_ephy for item in sublist]
        dic["list_mice_path_ephy"] = list_mice_path_ephy
        
        list_mice_path_behaviour = [glob.glob(os.path.join(group_path, mice_nb))for group_path in list_group_path_behaviour]
        list_mice_path_behaviour = [item for sublist in list_mice_path_behaviour for item in sublist]
        dic["list_mice_path_behaviour"] = list_mice_path_behaviour
        
        list_mice = [os.path.basename(mice)for mice in list_mice_path_behaviour]
        dic["list_mice"]= list_mice
        
        if mice_nb!='*':
            #in thoses folders we load all the folder with th name experiment_type 
            list_experiment_path_ephy = [glob.glob(os.path.join(mice_path, experiment_type))for mice_path in list_mice_path_ephy]
            list_experiment_path_ephy = [item for sublist in list_experiment_path_ephy for item in sublist]
            dic["list_experiment_path_ephy"]=list_experiment_path_ephy
            
            list_experiment_path_behaviour = [glob.glob(os.path.join(mice_path, experiment_type))for mice_path in list_mice_path_behaviour]
            list_experiment_path_behaviour= [item for sublist in list_experiment_path_behaviour for item in sublist]
            dic['list_experiment_path_behaviour']=list_experiment_path_behaviour
    
            if experiment_type!='*':
                #in thoses folders we load all the folder with th name protocol_type
                list_protocol_path_ephy = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_ephy]
                list_protocol_path_ephy = [item for sublist in list_protocol_path_ephy for item in sublist]
                dic['list_protocol_path_ephy']=list_protocol_path_ephy
                
                list_protocol_path_behaviour = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_behaviour]
                list_protocol_path_behaviour = [item for sublist in list_protocol_path_behaviour for item in sublist]
                dic['list_protocol_path_behaviour']=list_protocol_path_behaviour
                
                list_protocol = [os.path.basename(protocol)for protocol in list_protocol_path_ephy]
                dic['list_protocol']=list_protocol
    
                if protocol_type !='*':
                    list_condition_path_ephy = [glob.glob(os.path.join(protocol_path, condition_type))for protocol_path in list_protocol_path_ephy]
                    list_condition_path_ephy = [item for sublist in list_condition_path_ephy for item in sublist]
                    dic['list_condition_path_ephy']=list_condition_path_ephy

    return dic

def lick_data_calc(trial_dic, trial_use, current_time_displayed, average):
    if average:
        trial_data=trial_dic[current_time_displayed]['trial_data']

    else:
        trial_data = {i:v for i, v in trial_dic[current_time_displayed]['trial_data'].items() if i== trial_use}

    lick_data = np.empty((1,2))
    for i, value in trial_data.items():
        if trial_dic[current_time_displayed]['trial_dic_choice'][i]:
            if lick_data.shape[0] == 1:
                lick_data = value
            else:
                lick_data = np.vstack((lick_data, value))
                
    return lick_data

def ephy_data_calc(data, trial_dic, current_time_displayed):
    if data['average']:
        ephy_data = list_file_ephy_maker(trial_dic, data['info_exp_dic']['condition_type'], data['path_dic']['ephy_path'], 
                                         data['bandpass_dic'], data['shank_dic'], current_time_displayed)
        raw_data = calc_raw_data(ephy_data, data['average']) 
    else:
        current_trial = data['info_exp_dic']['trial_use']
        
        if data['info_exp_dic']['condition_type'] == 'Stim':
            file_nb = int(current_trial)-31 
        else:
            file_nb = int(current_trial)-1 #-1 beacause the list start at 0
        
        ephy_names = og.file_list(data['path_dic']['ephy_path'],True,'.rbf')
        file_name = ephy_names[file_nb]
        file= [(current_trial, os.path.normpath(fr"{data['path_dic']['ephy_path']}/{file_name}.rbf"))]
        
        ephy_data = data_ephy_calc(file, data['bandpass_dic'], data['shank_dic'])
        ephy_data = ephy_data[current_trial]
        raw_data = calc_raw_data(ephy_data, data['average']) 
    
    return ephy_data, raw_data

def calc_raw_data(ephy_data, average):
    if average:
        average_data_temp = {}
        for trial_nb in ephy_data.keys():
            for key, value in ephy_data[trial_nb].items():
                if key not in average_data_temp:
                    average_data_temp[key]= value
                else:
                    average_data_temp[key]=np.vstack((average_data_temp[key], value))
        raw_data = {}
        for k, v in average_data_temp.items():
            raw_data_temp = np.median(v, axis=0)
            time = np.arange(0, raw_data_temp.shape[0]/20000, 1/20000)
            raw_data[k] = np.column_stack((raw_data_temp, time))
    else:
        raw_data = {}
        for shank, value in ephy_data.items():
            time = np.arange(0, value.shape[0]/20000, 1/20000)
            raw_data[shank] = np.column_stack((value, time))
        
    return raw_data

def list_file_ephy_maker(trial_dic, condition_type, ephy_path, bandpass_dic, shank_dic, current_time_displayed):
    
    trial_dic_choice= trial_dic[current_time_displayed]['trial_dic_choice']
    if condition_type== 'Stim':
        list_trial = [int(i)-30 for i, value in trial_dic_choice.items() if value]
    else:
        list_trial = [int(i) for i, value in trial_dic_choice.items() if value]

    ephy_names = og.file_list(ephy_path,True,'.rbf')
    
    list_files = []
    for idx, file in enumerate(ephy_names):
        file_path = os.path.normpath(fr'{ephy_path}/{file}.rbf')
        for x in list_trial:
            if idx+1 == x:
                if condition_type== 'Stim':
                    trial_nb = x+30
                else:
                    trial_nb = x
                list_files.append((trial_nb, file_path))
    
    data_ephy = data_ephy_calc(list_files, bandpass_dic, shank_dic)
    
    return(data_ephy)    

def data_ephy_calc(list_files, bandpass_dic, shank_dic):
    
    if bandpass_dic['low'] == 0:
        bandpass_dic['low'] = 0.1

    #Structure of the probe Chanel 0:[14, 12, 10, 8, 9, 11, 13, 15],  Chanel 1:[7, 5, 3, 1, 0, 2, 4, 6]   
    if shank_dic['chanel0']:
        ch_group={'Ch_group 0':[14, 12, 10, 8, 9, 11, 13, 15]}
    elif shank_dic['chanel1']:
        ch_group={'Ch_group 1':[7, 5, 3, 1, 0, 2, 4, 6]}
    elif shank_dic['both']:
        ch_group={'Ch_group 0':[14, 12, 10, 8, 9, 11, 13, 15], 'Ch_group 1':[7, 5, 3, 1, 0, 2, 4, 6]}
    elif shank_dic['electrode']:
        if shank_dic['electrode_nb'] == 'all':
            ch_group={'electrode nb 0': [0], 'electrode nb 1': [1], 'electrode nb 2': [2], 'electrode nb 3': [3], 'electrode nb 4': [4], 'electrode nb 5': [5],
                     'electrode nb 6': [6], 'electrode nb 7': [7], 'electrode nb 8': [8],'electrode nb 9': [9],'electrode nb 10': [10],
                     'electrode nb 11': [11], 'electrode nb 12': [12],'electrode nb 13': [13],'electrode nb 14': [14],'electrode nb 15': [15]}
        else:
            ch_group={f"electrode nb {shank_dic['electrode_nb']}": [shank_dic['electrode_nb']]}
               
    data_ephy = {}
    for i in list_files:
        data_ephy[i[0]]={}
        sigs = np.fromfile(i[1], dtype=float).reshape(-1,16)
        for ind, gr in ch_group.items():
            if ind not in data_ephy:
               shank_average = np.median(sigs[:,gr], axis=1)
               shank_average = filters.bandpass_filter(shank_average, order=8, sample_rate=20000,freq_low=bandpass_dic['low'], 
                                                       freq_high=bandpass_dic['high'], axis=0)
               data_ephy[i[0]][ind] = shank_average
                   
    return data_ephy

def calc_complex(ephy_data, average, scalogram_parameters):
    complex_dic = {}
    if average:
        for v in ephy_data.values():
            for ind, val in v.items():
                complex_map, map_times, freqs, tfr_sampling_rate = scalo.compute_timefreq(val, sampling_rate=20000, 
                                                                                          f_start=(scalogram_parameters['low']+0.1), 
                                                                                          f_stop=(scalogram_parameters['high']+0.1), 
                                                                                          delta_freq=0.1, nb_freq=None,f0=2.5,  
                                                                                          normalisation = 0, t_start=0)
                if not ind in complex_dic:
                    complex_dic[ind]={'complex_map':complex_map, 'map_times':map_times, 'freqs':freqs, 'tfr_sampling_rate':tfr_sampling_rate, 
                                      'amplitude_map':np.abs(complex_map), 'power_map':np.abs(complex_map)**2, 'power_MAD':None, 'amplitude_MAD':None}
                else:
                    complex_dic[ind]['complex_map'] = np.dstack((complex_dic[ind]['complex_map'], complex_map))
                    ampl_map=np.abs(complex_map)
                    complex_dic[ind]['amplitude_map'] = np.dstack((complex_dic[ind]['amplitude_map'], ampl_map))
                    complex_dic[ind]['power_map'] = np.dstack((complex_dic[ind]['power_map'], ampl_map**2))
                
                    
        for indx in complex_dic.keys():
            for key, value in complex_dic[indx].items():
                if key == 'complex_map':
                    complex_dic[indx][key]= np.mean(value, axis=2)
                elif key == 'power_map' or key == 'amplitude_map':
                    complex_dic[indx][key]= np.median(value, axis=2)
                    complex_dic[indx][key.replace('map','MAD')]= mad(value, axis=2)
                else:
                    continue
            
        complex_dic = calc_extent(complex_dic)

    
    else:
        for i, v in ephy_data.items():
            complex_map, map_times, freqs, tfr_sampling_rate = scalo.compute_timefreq(v, sampling_rate=20000, 
                                                                                      f_start=(scalogram_parameters['low']+0.1), 
                                                                                      f_stop=(scalogram_parameters['high']+0.1), 
                                                                                      delta_freq=0.1, nb_freq=None,f0=2.5,  
                                                                                      normalisation = 0, t_start=0)
            ampl_map= np.abs(complex_map)
            power_map=ampl_map**2
            delta_freq = freqs[1] - freqs[0] 
            extent = (map_times[0], map_times[-1], freqs[0]-delta_freq/2., freqs[-1]+delta_freq/2.)
            complex_dic[i]={'complex_map':complex_map, 'amplitude_map':ampl_map, 'power_map':power_map, 'map_times':map_times, 
                            'freqs':freqs, 'tfr_sampling_rate':tfr_sampling_rate, 'delta_freq':delta_freq, 'extent':extent}
            
    return complex_dic
  
def calc_extent(complex_dic):
    for indx in complex_dic.keys():
        delta_freq = complex_dic[indx]['freqs'][1] - complex_dic[indx]['freqs'][0] 
        complex_dic[indx]['delta_freq']=delta_freq
        
        extent = (complex_dic[indx]['map_times'][0], complex_dic[indx]['map_times'][-1], 
                   complex_dic[indx]['freqs'][0]-delta_freq/2., complex_dic[indx]['freqs'][-1]+delta_freq/2.)
        complex_dic[indx]['extent']=extent
    return complex_dic
        
def calc_phase(complex_data, phase_frequency):    
    phase_frequency = (phase_frequency*10)-1
    phase_dic = {}
    for indx in complex_data.keys():
        phase = np.angle(complex_data[indx]['complex_map'][:,phase_frequency])
        time = np.arange(0,10,10/len(phase))
        phase_dic[indx] =  np.column_stack((phase, time))
        
    return phase_dic

def ridge_line_calc(complex_data, ridgle_line_parameters, power):
    ridge_line_dic = {}
    for key in complex_data.keys():
        if power:
            ridge_map = [complex_data[key]['power_map'], complex_data[key]['tfr_sampling_rate']]
        else:
            ridge_map = [complex_data[key]['amplitude_map'], complex_data[key]['tfr_sampling_rate']]
        ridge,theta,x,y = scalo.ridge_line(ridge_map[0],ridge_map[1],t0=0,t1=9,f0=ridgle_line_parameters['low'],f1=ridgle_line_parameters['high'], rescale=True)
        ridge_line_dic[key]={'ridge':ridge, 'theta':theta, 'x':x, 'y':y, 'map_times':complex_data[key]['map_times']}
    
    return ridge_line_dic        

def ephy_plot_raw_data(axes, average_data, current_chanel, shank_dic):       
    axes.plot(average_data[current_chanel][:,1], average_data[current_chanel][:,0]) 
    axes.set_title(f'{current_chanel}: Raw data')
    if  shank_dic['both'] and current_chanel == 'Ch_group 1': 
        pass
    else:
        axes.set_ylabel('Intensity (V)')

def ephy_plot_phase(axes, phase_dic, current_chanel, shank_dic, phase_frequency):        
    axes.plot(phase_dic[current_chanel][:,1], phase_dic[current_chanel][:,0])
    axes.set_title(f'{current_chanel}: instantenious phase')
    if shank_dic['both'] and current_chanel == 'Ch_group 1': 
        pass
    else:
        axes.set_ylabel('Intensity (V)') 

def ephy_plot_amplitude( axes, ampl_map, extent, current_chanel, shank_dic):
    axes.imshow(ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
    axes.set_title('Amplitude')
    axes.set_title(f'{current_chanel}: Amplitude')
    if  shank_dic['both'] and current_chanel == 'Ch_group 1': 
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')
    

def ephy_plot_power (axes, power_map, extent, current_chanel, shank_dic):
    axes.imshow(power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
    axes.set_title(f'{current_chanel}: Power')
    if  shank_dic['both'] and current_chanel == 'Ch_group 1': 
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')
    

def ephy_plot_intensity(axes, map_times, ridge, current_chanel, shank_dic):   
    axes.plot(map_times,ridge,color='r',alpha=0.5)            
    axes.set_title(f'{current_chanel}: Intensity of the ridge')
    if shank_dic['both'] and current_chanel == 'Ch_group 1':
        pass
    else:
        axes.set_ylabel('Intensity')

def ephy_plot_frequency(axes, map_times, y, current_chanel, shank_dic):
    axes.plot(map_times,y,color='r',alpha=0.5)            
    axes.set_title(f'{current_chanel}: Frequency of the ridge')
    if shank_dic['both'] and current_chanel == 'Ch_group 1':
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')
        
def data_slicer(data_sliced, coordonate, time_column=0, calc_x=True, calc_y=True, nb_dimension=2):
    """
    remouve the data of the np.array based on the coordonate feed

    """
    if data_sliced is not None:
        if nb_dimension == 1:
            if calc_y:
                y_begining = np.where(data_sliced >= (coordonate['y1']-(coordonate['y1']*0.05)))[0]
                y_end = np.where(data_sliced <= (coordonate['y2']+(coordonate['y2']*0.05)))[0]
                y = np.intersect1d(y_begining, y_end)
                data_sliced = data_sliced[y] 
                
            if calc_x:
                x_begining = np.where(data_sliced >= (coordonate['x1']-(coordonate['x1']*0.05)))[0]
                x_end = np.where(data_sliced <= (coordonate['x2']+(coordonate['x2']*0.05)))[0]
                x = np.intersect1d(x_begining, x_end)
                data_sliced = data_sliced[x] 
                
        elif nb_dimension == 2:
            if calc_y:
                y_begining = np.where(data_sliced[:,0] >= (coordonate['y1']-(coordonate['y1']*0.05)))[0]
                y_end = np.where(data_sliced[:,0] <= (coordonate['y2']+(coordonate['y2']*0.05)))[0]
                y = np.intersect1d(y_begining, y_end)
                data_sliced = data_sliced[y,:] 
                
            if calc_x:
                x_begining = np.where(data_sliced[:,time_column] >= (coordonate['x1']-(coordonate['x1']*0.05)))[0]
                x_end = np.where(data_sliced[:,time_column] <= (coordonate['x2']+(coordonate['x2']*0.05)))[0]
                x = np.intersect1d(x_begining, x_end)
                data_sliced = data_sliced[x,:]
    

    return data_sliced

def ephy_data_selection(complex_data, current_coordinate, x_only=False):
    for shank in complex_data.keys():
        complex_dic_temp = {}
        for key, value in complex_data[shank].items():
            if 'complex' in key or 'amplitude' in key or 'power' in key:
                if not x_only:
                    value_temp = value[:, int(((current_coordinate['y1']*10)-1)):int(((current_coordinate['y2']*10)-1))]
                else:
                    value_temp = value
                time = np.array(range(0,value.shape[0],1))/complex_data[shank]['tfr_sampling_rate']
                value_temp = np.column_stack((time, value_temp))
                value_temp = data_slicer(value_temp, current_coordinate, time_column=0, calc_y=False)
                complex_dic_temp['map_times'] = value_temp[:,0]
                complex_dic_temp[key] = np.delete(value_temp, 0, axis=1)
            elif 'time' in key:
                continue
            elif 'tfr' in key:
                complex_dic_temp[key] = value
            elif 'freqs' in key:
                complex_dic_temp[key] = np.arange(current_coordinate['y1'], current_coordinate['y2'], 0.1)
        complex_data[shank]=complex_dic_temp
    
    complex_data = calc_extent(complex_data)
        
    return complex_data   
