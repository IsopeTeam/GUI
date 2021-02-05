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
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib.pyplot as plt
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

def wheel_speed (wheel, trial_dic_choice):
    """
    first column is trial nb, second column is the time at which the wheel has turned, 
    the third column is the instant speed of the wheel based on the time diference between 2 position of the wheel 
    and the distance of 3.875 cm between those 2 position. 
    The first line of each trial is wrong because the previous time is attributaed to a other trial 
    and do not match
    """
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
    

def path_finder(main_folder_path, group_nb = '', mice_nb = '', experiment_type = '', protocol_type = '', condition_type = ''):
    """this function create a dictionary that contain the path to all the file need for both behaviour and electrophy. 
    we can specify which group, mice_nb, experiment type, protocole type, condition type. 
    The folder structure need to be respected for it to work properly (see Github/TeamIsope/GUI/ReadMe)    
    """
    group_nb = group_nb.split(' ')[-1] #this is done to not load folder wich dont start by Group
    group_nb = fr'*Group {group_nb}*'
    mice_nb = fr'*{mice_nb}'
    experiment_type = fr'*{experiment_type}'
    protocol_type = fr'*{protocol_type}'
    condition_type = fr'{condition_type}'

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

def list_file_ephy_maker(trial_dic, condition_type, ephy_path, bandpass_dic, current_time_displayed):
    
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
    
    data_ephy = data_ephy_calc(list_files, bandpass_dic)
    
    return(data_ephy)    

def data_ephy_calc(list_files, bandpass_dic):
    
    if bandpass_dic['low'] == 0:
        bandpass_dic['low'] = 0.1
        
    #Structure of the probe
    ch_group = ([14,9,12,11,10,13,8,15],[7,0,5,2,3,4,1,6])
        
    data_ephy = {}
    for i in list_files:
        data_ephy[i[0]]={}
        sigs = np.fromfile(i[1], dtype=float).reshape(-1,16)
        for ind,gr in enumerate(ch_group):
            if f'Ch_group {ind}' not in data_ephy:
               shank_average = np.mean(sigs[:,gr], axis=1)
               shank_average = filters.bandpass_filter(shank_average, order=8, sample_rate=20000,freq_low=bandpass_dic['low'], freq_high=bandpass_dic['high'], axis=0)
               data_ephy[i[0]][f'Ch_group {ind}'] = shank_average
                   
    return data_ephy

def calc_raw_data(ephy_data, graph_dic):

    if graph_dic['ws_average']:
        average_data_temp = {}
        for trial_nb in ephy_data.keys():
            for key, value in ephy_data[trial_nb].items():
                if key not in average_data_temp:
                    average_data_temp[key]= value
                else:
                    average_data_temp[key]=np.vstack((average_data_temp[key], value))
        raw_data = {}
        for k, v in average_data_temp.items():
            raw_data[k]= np.mean(v, axis=0)
        raw_data['time']= list(np.arange(0, raw_data['Ch_group 0'].shape[0]/20000, 1/20000))
    else:
        raw_data = {'Ch_group 0': ephy_data['Ch_group 0'], 'Ch_group 1': ephy_data['Ch_group 1']}
        raw_data['time']= list(np.arange(0, raw_data['Ch_group 0'].shape[0]/20000, 1/20000))
        
    return raw_data
        
      
def calc_phase(ephy_data, graph_dic):
    
    phase_dic = {}
    if graph_dic['ws_average']:
        for i, v in ephy_data.items():
            phase_dic[i]={}
            for ind, val in v.items():
                complex_map, *_ = scalo.compute_timefreq(val, sampling_rate=20000, f_start=0.1, f_stop=30.1, delta_freq=0.1, nb_freq=None,f0=2.5,  normalisation = 0, t_start=0)
                phase_dic[i][ind] = complex_map
                    
        Ch_group0_list = []
        Ch_group1_list = []
        for value in phase_dic.values():
            Ch_group0_list.append(value['Ch_group 0'])
            Ch_group1_list.append(value['Ch_group 1']) 
        phase_dic = {'Ch_group 0': np.mean(Ch_group0_list, axis=0), 'Ch_group 1':np.mean(Ch_group1_list, axis=0)}
    
    else:
        for i, v in ephy_data.items():
            complex_map, *_ = scalo.compute_timefreq(v, sampling_rate=20000, f_start=0.1, f_stop=30.1, delta_freq=0.1, nb_freq=None,f0=2.5,  normalisation = 0, t_start=0)
            phase_dic[i] = complex_map
            
    return phase_dic

def graph_ephy_raw(ephy_data, graph_dic, shank_dic, phase_frequency, fig, info_exp_dic, new_fig):
    
    if graph_dic['raw_data']:
        raw_data = calc_raw_data(ephy_data, graph_dic)
    
    if graph_dic['phase']:
        phase_dic = calc_phase(ephy_data, graph_dic)
    
    trial_use = info_exp_dic['trial_use']
    mice_nb = info_exp_dic['mice_nb']
    experiment_type = info_exp_dic['experiment_type']
    current_time = info_exp_dic['current_time']
    protocol_type = info_exp_dic['protocol_type']
    condition_type = info_exp_dic['condition_type']
    
    if graph_dic['ws_average']:
       title = fr'Whole session average. Number of trials used {trial_use}'+'\n'+fr'Mouse nb {mice_nb}, {experiment_type}: {current_time}, protocol {protocol_type}, {condition_type}'
    else:
        title = fr'Trial nb {trial_use}'+'\n'+fr'Mouse nb {mice_nb}, {experiment_type}: {current_time}, protocol {protocol_type}, {condition_type}'
    
    
    if shank_dic['both']:
        column_nb = 2
        chanel = 0
        plot_position = 0
    
    elif shank_dic['chanel0']:
        column_nb = 1
        chanel = 0
        plot_position = 0

    else:
        column_nb = 1
        chanel = 1
        plot_position = 0


    plot_nb = int(graph_dic['raw_data'])+int(graph_dic['phase'])
    
    if new_fig:
        fig_new = plt.figure(title)
        ax = fig_new.subplots(plot_nb, column_nb, sharex=True)
        fig_new.suptitle(title,weight='bold')
    else:
        plt.figure(0)
        ax = fig.subplots(plot_nb, column_nb, sharex=True)
        fig.suptitle(title,weight='bold') #main figure title


    if plot_nb==1 and not shank_dic['both']: #only one plot
        axes=ax
    elif plot_nb>1 and not shank_dic['both']: #multiple plot but 1 column
        axes=ax[plot_position]
    elif plot_nb==1 and shank_dic['both']:   #multiple column 1 line
        axes = ax[plot_position]
    else:   #multiple column multiple line
        axes = ax[0,0]
                
    #average plot
    if graph_dic['raw_data']:
        ephy_plot_average(axes, raw_data, chanel, shank_dic)
        
        if shank_dic['both']: #if we use both chanel
            chanel +=1 
            if graph_dic['phase']: #if we also plot phase
                axes = ax[plot_position,chanel] #we plot with 2 dimention
                plot_position +=1
            else:
                plot_position +=1
                axes = ax[plot_position] #when only average plot we have 1 dimention
                
            ephy_plot_average(axes, raw_data, chanel, shank_dic) #axes are set up we can plot the second average
        
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]
                
        else: #if we use only one chanel
            plot_position +=1
    
    #instant phase plot
    if graph_dic['phase']:
        if plot_nb >1 and not shank_dic['both']:
            axes=ax[plot_position]
        
        if chanel == 0: #this is simply to have the right name on the variable for ech channel (in order to not calculate them again for the time freq)
            ephy_plot_phase(axes, phase_dic, chanel, shank_dic, phase_frequency)
        else:
            ephy_plot_phase(axes, phase_dic, chanel, shank_dic, phase_frequency)
            
        if shank_dic['both']: #if we use both chanel
            chanel +=1
            if graph_dic['raw_data']:
                axes = ax[plot_position,chanel]
                plot_position+=1

            else:
                plot_position+=1
                axes = ax[plot_position]
            ephy_plot_phase(axes, phase_dic, chanel, shank_dic, phase_frequency)
            
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]      
        else: #if we use only one chanel
            plot_position += 1
            
    if shank_dic['both'] and plot_nb>1:
        ax[plot_position-1,0].set_xlabel('Time (s)')
        ax[plot_position-1,1].set_xlabel('Time (s)')
    elif not shank_dic['both'] and plot_nb>1:
        ax[plot_position-1].set_xlabel('Time (s)')
    elif shank_dic['both'] and plot_nb==1:
        ax[plot_position-1].set_xlabel('Time (s)')
    else:
        ax.set_xlabel('Time (s)')
                
    
    current_time= str(current_time)
    current_reward_time = int(current_time[-3:])
    current_reward_time=2.05+(float(current_reward_time)/1000) #determine when the reward happen depending of the keys of the dictionary
    if plot_nb >1 or shank_dic['both']:
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
    

def graph_ephy_time_frequency(ephy_data, graph_dic, shank_dic, rl_dic, fig, info_exp_dic, new_fig):
    
    trial_use = info_exp_dic['trial_use']
    mice_nb = info_exp_dic['mice_nb']
    experiment_type = info_exp_dic['experiment_type']
    current_time = info_exp_dic['current_time']
    protocol_type = info_exp_dic['protocol_type']
    condition_type = info_exp_dic['condition_type']
    
    if graph_dic['ws_average']:
       title = fr'Whole session average. Number of trials used {trial_use}'+'\n'+fr'Mouse nb {mice_nb}, {experiment_type}: {current_time}, protocol {protocol_type}, {condition_type}'
    else:
        title = fr'Trial nb {trial_use}'+'\n'+fr'Mouse nb {mice_nb}, {experiment_type}: {current_time}, protocol {protocol_type}, {condition_type}'
    

    if shank_dic['both']:
        column_nb = 2
        chanel = 0
        plot_position = 0
    
    elif shank_dic['chanel0']:
        column_nb = 1
        chanel = 0
        plot_position = 0

    else:
        column_nb = 1
        chanel = 1
        plot_position = 0
    
    #if we did not already calculate those value in the phase plot we do it here
    if not shank_dic['both']:
        if chanel ==0 :
            complex_map0, map_times0, freqs0, tfr_sampling_rate0, ampl_map0, power_map0 = ephy_time_freq(ephy_data, 0, graph_dic)
            
        if chanel ==1 :
            complex_map1, map_times1, freqs1, tfr_sampling_rate1, ampl_map1, power_map1 = ephy_time_freq(ephy_data, 1, graph_dic)
    
    elif shank_dic['both'] :
        complex_map0, map_times0, freqs0, tfr_sampling_rate0, ampl_map0, power_map0 = ephy_time_freq(ephy_data, 0, graph_dic)
        complex_map1, map_times1, freqs1, tfr_sampling_rate1, ampl_map1, power_map1 = ephy_time_freq(ephy_data, 1, graph_dic)

    #This is simply to setup the plotting area (check imshow details to further understand, if interested)
    if chanel ==0 or shank_dic['both']:
        delta_freq0 = freqs0[1] - freqs0[0]
        extent0 = (map_times0[0], map_times0[-1], freqs0[0]-delta_freq0/2., freqs0[-1]+delta_freq0/2.)
    
    if chanel ==1 or shank_dic['both']:
        delta_freq1 = freqs1[1] - freqs1[0]
        extent1 = (map_times1[0], map_times1[-1], freqs1[0]-delta_freq1/2., freqs1[-1]+delta_freq1/2.)
    
    #we then creat the main figure and setup the proper nb of line and column
    plot_nb = int(graph_dic['hm_amplitude'])+int(graph_dic['hm_power']+int(graph_dic['rl_intensity'])+ int(graph_dic['rl_frequency']))
    

    if new_fig:
        fig_new = plt.figure(title)
        ax = fig_new.subplots(plot_nb, column_nb, sharex=True)
        fig_new.suptitle(title,weight='bold')
    else:
        plt.figure(0)
        ax = fig.subplots(plot_nb, column_nb, sharex=True)
        fig.suptitle(title,weight='bold') #main figure title
        
    
    plt.subplots_adjust(hspace=0.4)
    plot_position = 0
   
    if plot_nb==1 and not shank_dic['both']: #only one plot
        axes=ax
    elif plot_nb>1 and not shank_dic['both']: #multiple plot but 1 column
        axes=ax[plot_position]
    elif plot_nb==1 and shank_dic['both']:   #multiple column 1 line
        axes = ax[plot_position]
    else:   #multiple column multiple line
        axes = ax[0,0]
    
#scalogram
    #amplitude
    if graph_dic['hm_amplitude']:
        if chanel ==0 :
            ephy_plot_amplitude(axes, ampl_map0, extent0, chanel, shank_dic)
            ridge_map0 = [ampl_map0, tfr_sampling_rate0] #this will be use to know wich graph to used for the ridge line
        else:
            ephy_plot_amplitude(axes, ampl_map1, extent1, chanel, shank_dic)
            ridge_map1 = [ampl_map1, tfr_sampling_rate1]
        
        #ridge_map0 = [Ch_group0_ampl_map, Ch_group0_tfr_sampling_rate]
        
        if shank_dic['both']:#if we use both chanel
            chanel +=1
            if plot_nb>1:#if we also plot power or ridge
                axes= ax[plot_position,chanel]
                plot_position +=1
            else:
                plot_position +=1
                axes = ax[plot_position] #when only amplitude plot we have 1 dimention
            
            ephy_plot_amplitude(axes, ampl_map1, extent1, chanel, shank_dic)#axes are set up we can plot the second average
            ridge_map1 = [ampl_map1, tfr_sampling_rate1]
        
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]
        else: #if we use only one chanel
            plot_position +=1

    #power
    if graph_dic['hm_power']:
        if plot_nb >1 and not shank_dic['both']:
            axes=ax[plot_position]
            
        if chanel ==0 :
            ephy_plot_power(axes, power_map0, extent0, chanel, shank_dic)
            ridge_map0 = [power_map0, tfr_sampling_rate0]
        else:
            ephy_plot_power(axes, power_map1, extent1, chanel, shank_dic)
            ridge_map1 = [power_map1, tfr_sampling_rate1]
                    
        if shank_dic['both']:#if we use both chanel
            chanel +=1
            if plot_nb>1:#if we also plot  ridge
                axes= ax[plot_position, chanel]
                plot_position +=1
            else:
                plot_position +=1
                axes = ax[plot_position] #when only power plot we have 1 dimention
            
            ephy_plot_power(axes, power_map1, extent1, chanel, shank_dic)#axes are set up we can plot the second average
            ridge_map1 = [power_map1, tfr_sampling_rate1]
        
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]
        else: #if we use only one chanel
            plot_position +=1

      
    if graph_dic['rl_intensity'] or graph_dic['rl_frequency']: #if we plot ridge we need to calculate those value 
        if chanel==0:
            ridge0,theta0,x0,y0 = scalo.ridge_line(ridge_map0[0],ridge_map0[1],t0=0,t1=9,f0=rl_dic['low'],f1=rl_dic['high'], rescale=True)
            #ax[plot_position-1].plot(map_times0[:-1],y0,color='r') if we want to plot the ridge line on amplitude or power map
        
        if chanel ==1 or shank_dic['both']: 
            ridge1,theta1,x1,y1 = scalo.ridge_line(ridge_map1[0],ridge_map1[1],t0=0,t1=9,f0=rl_dic['low'],f1=rl_dic['high'], rescale=True)
            #ax[plot_position-1].plot(map_times1[:-1],y1,color='r')

    #ridge intensity
    if graph_dic['rl_intensity']:
        if plot_nb >1 and not shank_dic['both']:
            axes=ax[plot_position]
            
        if chanel ==0 :
            ephy_plot_intensity(axes, map_times0[:-1], ridge0, chanel, shank_dic, graph_dic['hm_power'])
        else:
            ephy_plot_intensity(axes,map_times1[:-1], ridge1, chanel, shank_dic, graph_dic['hm_power'])
                 
        if shank_dic['both']:#if we use both chanel
            chanel +=1
            if plot_nb>1:#if we also plot ridge
                axes= ax[plot_position,chanel]
                plot_position +=1
            else:
                plot_position +=1
                axes = ax[plot_position] #when only amplitude plot we have 1 dimention
            
            ephy_plot_intensity(axes, map_times1[:-1], ridge1, chanel, shank_dic, graph_dic['hm_power'])#axes are set up we can plot the second average
            
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]
        else: #if we use only one chanel
            plot_position +=1

    #ridge frequency
    if graph_dic['rl_frequency']:
        if plot_nb >1 and not shank_dic['both']:
            axes=ax[plot_position]
            
        if chanel ==0 :
            ephy_plot_frequency(axes, map_times0[:-1], y0, chanel, shank_dic)
        else:
            ephy_plot_frequency(axes,map_times1[:-1], y1, chanel, shank_dic)
                 
        if shank_dic['both']:#if we use both chanel
            chanel +=1
            if plot_nb>1:#if we also plot ridge
                axes= ax[plot_position,chanel]
                plot_position +=1
            else:
                plot_position +=1
                axes = ax[plot_position] #when only amplitude plot we have 1 dimention
            ephy_plot_frequency(axes, map_times1[:-1], y1, chanel, shank_dic)#axes are set up we can plot the second average
            chanel=0
            if plot_position < plot_nb:
                axes = ax[plot_position,chanel]
                
        else: #if we use only one chanel
            plot_position +=1


    if shank_dic['both'] and plot_nb>1:
        ax[plot_position-1,0].set_xlabel('Time (s)')
        ax[plot_position-1,1].set_xlabel('Time (s)')
    elif not shank_dic['both'] and plot_nb>1:
        ax[plot_position-1].set_xlabel('Time (s)')
    elif shank_dic['both'] and plot_nb==1:
        ax[plot_position-1].set_xlabel('Time (s)')
    else:
        ax.set_xlabel('Time (s)')
    
    current_time= str(current_time)
    current_reward_time = int(current_time[-3:])
    current_reward_time=2.05+(float(current_reward_time)/1000) #determine when the reward happen depending of the keys of the dictionary
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

def ephy_plot_average(axes, average_data, chanel, shank_dic):       
    axes.plot(average_data['time'], average_data[fr'Ch_group {chanel}']) 
    axes.set_title(fr'Ch group {chanel}: whole session average')
    if  shank_dic['both'] and chanel ==1: 
        pass
    else:
        axes.set_ylabel('Intensity (V)')

def ephy_plot_phase(axes, phase_dic, chanel, shank_dic, phase_frequency):       
    phase_frequency = (phase_frequency*10)-1
    phase = np.angle(phase_dic[fr'Ch_group {chanel}'][:,phase_frequency])
    time = np.arange(0,10,10/len(phase))
    axes.plot(time, phase)
    axes.set_title(fr'Ch group {chanel}: instantenious phase')
    if shank_dic['both'] and chanel ==1: 
        pass
    else:
        axes.set_ylabel('Intensity (V)') 


def ephy_plot_amplitude( axes, ampl_map, extent, chanel, shank_dic):
    axes.imshow(ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
    axes.set_title('Amplitude')
    axes.set_title(fr'Ch group {chanel}: Amplitude')
    if  shank_dic['both'] and chanel ==1: 
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')


def ephy_plot_power (axes, power_map, extent, chanel, shank_dic):
    axes.imshow(power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
    axes.set_title(fr'Ch group {chanel}: Power')
    if  shank_dic['both'] and chanel ==1: 
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')


def ephy_plot_intensity(axes, map_times, ridge, chanel, shank_dic, graph_power):
    axes.plot(map_times,ridge,color='r',alpha=0.5)            
    axes.set_title(fr'Ch group {chanel}: Intensity of the ridge')
    if shank_dic['both'] and chanel == 1:
        pass
    else:
        axes.set_ylabel('Intensity')

def ephy_plot_frequency(axes, map_times, y, chanel, shank_dic):
    axes.plot(map_times,y,color='r',alpha=0.5)            
    axes.set_title(fr'Ch group {chanel}: Frequency of the ridge')
    if shank_dic['both'] and chanel ==1:
        pass
    else:
        axes.set_ylabel('Frequency (Hz)')
        
        
def ephy_time_freq(ephy_data, chanel, graph_dic):
      
    if graph_dic['ws_average']:
        time_freq_dic = {}
        for i, v in ephy_data.items():
            if i == 'list_trial_display':
                pass
            else:
                time_freq_dic[i]={}
                complex_map, map_times, freqs, tfr_sampling_rate = scalo.compute_timefreq(v[fr'Ch_group {chanel}'], sampling_rate=20000, f_start=0.1, f_stop=30.1, delta_freq=0.1, nb_freq=None,f0=2.5,  normalisation = 0, t_start=0)
                time_freq_dic[i] = complex_map
    
        
        Ch_group_list = []
        for value in time_freq_dic.values():
            Ch_group_list.append(value)
        
        complex_map = np.mean(Ch_group_list, axis=0)  
        ampl_map = np.abs(complex_map)  
        power_map = ampl_map**2
    
    else:
        complex_map, map_times, freqs, tfr_sampling_rate = scalo.compute_timefreq(ephy_data[fr'Ch_group {chanel}'], sampling_rate=20000, f_start=0.1, f_stop=30.1, delta_freq=0.1, nb_freq=None,f0=2.5,  normalisation = 0, t_start=0)
        ampl_map = np.abs(complex_map)  
        power_map = ampl_map**2

    return complex_map, map_times, freqs, tfr_sampling_rate, ampl_map, power_map

    

if __name__ == '__main__' :

    fig = plt.figure('Main Figure')
    #wheel speed
    v = B.load_lickfile("\\equipe2-nas1\F.LARENO-FACCINI\BACKUP FEDE\Behaviour\Group 15\176 (CM16-Buz - Female)\Training\T8-2\176_2020_07_24_15_24_44.coder", wheel=True)
    random_delay=B.extract_random_delay("C:/Users/Master5.INCI-NSN/Desktop/Pierre/data/Behaviour/Group 15/176 F/Random Delay/P16/176_2020_07_26_14_52_13.param")
    delays, wheel_by_delay = B.separate_by_delay(random_delay, v) 

""""
    wheel_data = wheel_speed(wheel_by_delay['400'])        
    plt.plot(wheel_data[:,0], wheel_data[:,1])
    
    #for cle in delays.keys():
        #wheel_data = wheel_speed(wheel_by_delay[cle])        
        #plt.plot(wheel_data[:,0], wheel_data[:,1])
    
    plt.axvspan(0,0.5, facecolor="green", alpha=0.3)
    plt.axvspan(1.5,2, facecolor="green", alpha=0.3)
    plt.axvspan(2.55,2.7, facecolor="red", alpha=0.3)
    plt.show()
"""
    
"""
    #path finder
    group_nb = '15'
    mice_nb = '173'
    experiment_type = 'Random Delay'
    protocol_type = 'P13'
    condition_type = 'stim'
    dic = path_finder('C:/Users/Master5.INCI-NSN/Desktop/Pierre/data', group_nb, mice_nb, experiment_type, protocol_type, condition_type)
    
"""