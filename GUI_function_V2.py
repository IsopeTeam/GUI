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

def wheel_speed (wheel, condition_type='No Stim'):

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
    if condition_type == 'No Stim':
        nb_trials= [1,30]
    
    elif condition_type == 'Stim':
        nb_trials= [31,60]
    else:
        nb_trials=[1, 60]
        
    trial_dic ={}
    for i in range(nb_trials[0],nb_trials[1]+1): 
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
                    #     #print (cle, time, speed)
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
    
    return data
    
    ### This is just a different style of coding the previous lines, just to see the personal differences ###
    # lists = np.array(sorted(sampling_dic.items()))
    # y = gaussian_filter1d(lists[:,1],sigma=2)
    # return np.array(list(zip(lists[:,0],y)))
    

def path_finder(main_folder_path, group_nb = '', mice_nb = '', experiment_type = '', protocol_type = '', condition_type = ''):
    """this function create a dictionary that contain the path to all the file need for both behaviour and electrophy. 
    we can specify which group, mice_nb, experiment type, protocole type, condition type. 
    The folder structure need to be respected for it to work properly (see Github/TeamIsope/GUI/ReadMe)    
    """
    group_nb = fr'*{group_nb}'
    mice_nb = fr'*{mice_nb}'
    experiment_type = fr'*{experiment_type}'
    protocol_type = fr'*{protocol_type}'
    condition_type = fr'{condition_type}'
    
    #first we save the path to all the folder with the name 'group_nb'
    list_group_path_ephy = glob.glob(os.path.join(main_folder_path+'/Ephy', group_nb))
    list_group_path_behaviour = glob.glob(os.path.join(main_folder_path+'/Behaviour', group_nb))      
    list_group = [os.path.basename(group)for group in list_group_path_behaviour]
    
    #in thoses folders we save the path to all the folder with the name 'mice_nb'
    list_mice_path_ephy = [glob.glob(os.path.join(group_path+fr'/{mice_nb} (CM16-Buz - *'))for group_path in list_group_path_ephy]
    list_mice_path_ephy = [item for sublist in list_mice_path_ephy for item in sublist]
    
    list_mice_path_behaviour = [glob.glob(os.path.join(group_path, mice_nb))for group_path in list_group_path_behaviour]
    list_mice_path_behaviour = [item for sublist in list_mice_path_behaviour for item in sublist]
    
    list_mice = [os.path.basename(mice)for mice in list_mice_path_behaviour]
    
    """
    #in thoses folders we load all the folder with th name experiment_type
    if experiment_type == '*Training':
        list_experiment_path_ephy = [glob.glob(os.path.join(mice_path, experiment_type))for mice_path in list_mice_path_ephy]
        list_experiment_path_ephy = [item for sublist in list_experiment_path_ephy for item in sublist]"""
    

    list_experiment_path_ephy = [glob.glob(os.path.join(mice_path+'/Experiment', experiment_type))for mice_path in list_mice_path_ephy]
    list_experiment_path_ephy = [item for sublist in list_experiment_path_ephy for item in sublist]
    
    list_experiment_path_behaviour = [glob.glob(os.path.join(mice_path, experiment_type))for mice_path in list_mice_path_behaviour]
    list_experiment_path_behaviour= [item for sublist in list_experiment_path_behaviour for item in sublist]
    
    #in thoses folders we load all the folder with th name protocol_type
    list_protocol_path_ephy = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_ephy]
    list_protocol_path_ephy = [item for sublist in list_protocol_path_ephy for item in sublist]
    
    list_protocol_path_behaviour = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_behaviour]
    list_protocol_path_behaviour = [item for sublist in list_protocol_path_behaviour for item in sublist]
    
    list_condition_path_ephy = [glob.glob(os.path.join(protocol_path, condition_type))for protocol_path in list_protocol_path_ephy]
    list_condition_path_ephy = [item for sublist in list_condition_path_ephy for item in sublist]

    
    list_protocol = [os.path.basename(protocol)for protocol in list_protocol_path_behaviour]
    
    
    list_condition = ['Stim', 'No Stim']
                
    dic = {"list_group_path_ephy": list_group_path_ephy,
           "list_group_path_behaviour": list_group_path_behaviour,
           "list_group": list_group,
           "list_mice_path_ephy": list_mice_path_ephy,
           "list_mice_path_behaviour": list_mice_path_behaviour,
           "list_mice": list_mice,
           "list_experiment_path_ephy": list_experiment_path_ephy,
           "list_experiment_path_behaviour": list_experiment_path_behaviour,
           "list_protocol_path_ephy": list_protocol_path_ephy,
           "list_protocol_path_behaviour": list_protocol_path_behaviour,
           "list_protocol":list_protocol,
           "list_condition_path_ephy":list_condition_path_ephy,
           "list_condition":list_condition}
    return dic

def random_ephy(list_protocol_path_ephy, lick_path, param_path, dic_graph_choice_ephy, dic_graph_choice_time, mice_nb, protocol_type, condition_type, bandpass_dic):
    v = B.load_lickfile(lick_path)
    random_delay=B.extract_random_delay(param_path, skip_last=True)
    random, lick_by_delay = B.separate_by_delay(random_delay, v)
    random_choice = 'Random Delay'
    
    #Import all the files, by creating a list of them
    
    stim_dir = fr'{list_protocol_path_ephy}/Stim'
    stim_names = og.file_list(stim_dir,True,'.rbf')
    
    nostim_dir = fr'{list_protocol_path_ephy}/No Stim'
    nostim_names = og.file_list(nostim_dir,True,'.rbf')
     
    signals_by_delay = {}
    for k in random.keys():
        if dic_graph_choice_time[k]:
            signals_by_delay[k] = {}
            signals_by_delay[k]['NoStim'] = []
            signals_by_delay[k]['Early_Stim'] = []
            signals_by_delay[k]['Late_Stim'] = []
            for idx, file in enumerate(nostim_names):
    
                #Location of the file
                nostim_path =os.path.normpath(fr'{nostim_dir}/{file}.rbf')
                
                try: # To avoid the crash in case there are less Stim files than NoStim
                    stim_path =fr'{stim_dir}/{stim_names[idx]}.rbf'
                except:
                    continue
                #Divide by delay and channel group
                for x in random[k]:
                    if idx+1 == x[1]:
                            signals_by_delay[k]['NoStim'].append(nostim_path)
                    elif idx+31 == x[1]:
                        if idx<10:
                            signals_by_delay[k]['Early_Stim'].append(stim_path)
    
                        elif idx>=10:
                            signals_by_delay[k]['Late_Stim'].append(stim_path)
                list_files = []
                if condition_type == 'No Stim':
                    for value in signals_by_delay[k]['NoStim']:
                        list_files.append(os.path.basename(value))
                
                if condition_type == 'Stim':
                    for value in signals_by_delay[k]['Early_Stim']:
                        list_files.append(os.path.basename(value))
                    for value in signals_by_delay[k]['Late_Stim']:
                        list_files.append(os.path.basename(value))
                
            list_condition_path_ephy = fr'{list_protocol_path_ephy}/{condition_type}'
            reward_time =  k
            ephy_plot(list_condition_path_ephy, dic_graph_choice_ephy, mice_nb, protocol_type, condition_type, bandpass_dic, random_choice, list_files, reward_time)



def ephy_plot(list_condition_path_ephy, dic_graph_choice_ephy, mice_nb, protocol_type, condition_type, bandpass_dic, random_choice='Fixed Delay', list_files = [], reward_time=500):


    if random_choice == 'Fixed Delay':
        list_files = og.file_list(list_condition_path_ephy,no_extension=False,ext='.rbf')
        mean = ephy_mean(list_condition_path_ephy, list_files, bandpass_dic)
    
    else:
        mean = ephy_mean(list_condition_path_ephy, list_files, bandpass_dic)
    
    """
    This function create the plot for the electrophy part of the GUI, we feed it the path for the electrophy files. 
    It then call either, or both, ephy_mean(which calculate all the data for ploting the average on a session) and/or 
    ephy_time_freq (wich calculate all the data for time frequency plot)
    """
#all session average by shank, raw plot
    if dic_graph_choice_ephy['Ch_group0'] or dic_graph_choice_ephy['Ch_group1']:
        plot_nb = int(dic_graph_choice_ephy['Ch_group0'])+int(dic_graph_choice_ephy['Ch_group1'])
    
        fig, ax = plt.subplots(1, plot_nb, sharex=True, sharey=True)
        fig.suptitle(fr'Whole session average. Mouse nb:{mice_nb}, {random_choice}: {reward_time}, protocol {protocol_type}, {condition_type}',weight='bold') #main figure title
        plot_position = 0
    
        if plot_nb==1:
            axes=ax
        elif plot_nb>1:
            axes=ax[plot_position]
            fig.set_size_inches(10, 5)
        if dic_graph_choice_ephy['Ch_group0']:
            #first subplot 
            axes.plot(mean['time'], mean['Mean of Ch_group 0'])
            axes.set_ylabel('') 
            axes.set_xlabel('Time (sec)')
            axes.set_title('Ch group 0') 
            plot_position +=1
        
        
        if dic_graph_choice_ephy['Ch_group1']:
            #second subplot 
            if plot_nb >1:
                axes=ax[plot_position]
        
            axes.plot(mean['time'], mean['Mean of Ch_group 1'])
            axes.set_ylabel('')
            axes.set_xlabel('Time (sec)')
            axes.set_title('Ch group 1') 
        
        reward_time= str(reward_time)
        current_reward_time = int(reward_time[-3:])
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
            
#all session average by shank, time frequency plot (power)            
    #Chanel 0 plot maker  
    if dic_graph_choice_ephy['Ch_group0_power'] or dic_graph_choice_ephy['Ch_group0_amplitude']:
        Ch_group0_complex_map, Ch_group0_map_times, Ch_group0_freqs, Ch_group0_tfr_sampling_rate, Ch_group0_ampl_map, Ch_group0_power_map = ephy_time_freq(list_condition_path_ephy, mean, 0, bandpass_dic)
        
        #This is simply to setup the plotting area (check imshow details to further understand, if interested)
        Ch_group0_delta_freq = Ch_group0_freqs[1] - Ch_group0_freqs[0]
        Ch_group0_extent = (Ch_group0_map_times[0], Ch_group0_map_times[-1], Ch_group0_freqs[0]-Ch_group0_delta_freq/2., Ch_group0_freqs[-1]+Ch_group0_delta_freq/2.)
        
        plot_nb=int(dic_graph_choice_ephy['Ch_group0_power'])+int(dic_graph_choice_ephy['Ch_group0_amplitude'])+int(dic_graph_choice_ephy['Ch_group0_intensity'])+int(dic_graph_choice_ephy['Ch_group0_frequency'])
        fig, ax = plt.subplots(plot_nb, 1, sharex=True)
        plt.subplots_adjust(hspace=0.4)
        fig.suptitle('Time frequency power plot (chanel 0).\n'+fr'Mouse nb:{mice_nb}, {random_choice}: {reward_time}, protocol {protocol_type}, {condition_type}'+'\n',weight='bold') #main figure title
        plot_position = 0
        if plot_nb==1:
            axes=ax
        if plot_nb>1:
            axes=ax[plot_position]
        
        if dic_graph_choice_ephy['Ch_group0_amplitude']:
            axes.imshow(Ch_group0_ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group0_extent,cmap='viridis')
            axes.set_title('Amplitude')
            axes.set_ylabel('Frequency (Hz)')
            ridge_map0 = [Ch_group0_ampl_map, Ch_group0_tfr_sampling_rate]

            plot_position +=1
        
        if dic_graph_choice_ephy['Ch_group0_power']:
            if plot_nb>1:
              axes=ax[plot_position]                
            axes.imshow(Ch_group0_power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group0_extent,cmap='viridis')
            axes.set_title('Power')
            axes.set_ylabel('Frequency (Hz)')
            ridge_map0 = [Ch_group0_power_map, Ch_group0_tfr_sampling_rate]
            
            plot_position +=1
        
    #ridge map
    if dic_graph_choice_ephy['Ch_group0_intensity'] or dic_graph_choice_ephy['Ch_group0_frequency']:
        ridge0,theta0,x0,y0 = scalo.ridge_line(ridge_map0[0],ridge_map0[1],t0=0,t1=9,f0=bandpass_dic['freq_low'],f1=bandpass_dic['freq_high'], rescale=True)
        ax[plot_position-1].plot(Ch_group0_map_times[:-1],y0,color='r')
        
        if dic_graph_choice_ephy['Ch_group0_intensity']:
            if plot_nb>1:
              axes=ax[plot_position]
            
            axes.plot(Ch_group0_map_times[:-1],ridge0,color='r',alpha=0.5)            
            axes.set_title('Amplitude of the ridge')
            axes.set_ylabel('Amplitude (V)')

            plot_position +=1
            
        if dic_graph_choice_ephy['Ch_group0_frequency']:
            if plot_nb>1:
              axes=ax[plot_position] 
            axes.plot(Ch_group0_map_times[:-1],y0,color='r',alpha=0.5)            
            axes.set_title('Frequency of the ridge')
            axes.set_ylabel('Frequency (Hz)')


        axes.set_xlabel('Time (s)')
        
        reward_time= str(reward_time)
        current_reward_time = int(reward_time[-3:])
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
        

    
    #Chanel 1 plot maker
    if dic_graph_choice_ephy['Ch_group1_power'] or dic_graph_choice_ephy['Ch_group1_amplitude']:
        Ch_group1_complex_map, Ch_group1_map_times, Ch_group1_freqs, Ch_group1_tfr_sampling_rate, Ch_group1_ampl_map, Ch_group1_power_map = ephy_time_freq(list_condition_path_ephy, mean, 1, bandpass_dic)                 
        #This is simply to setup the plotting area (check imshow details to further understand, if interested)
        Ch_group1_delta_freq = Ch_group1_freqs[1] - Ch_group1_freqs[0]
        Ch_group1_extent = (Ch_group1_map_times[0],Ch_group1_map_times[-1], Ch_group1_freqs[0]-Ch_group1_delta_freq/2., Ch_group1_freqs[-1]+Ch_group1_delta_freq/2.)
    
        plot_nb=int(dic_graph_choice_ephy['Ch_group1_power'])+int(dic_graph_choice_ephy['Ch_group1_amplitude'])+int(dic_graph_choice_ephy['Ch_group1_intensity'])+int(dic_graph_choice_ephy['Ch_group1_frequency'])
        fig, ax = plt.subplots(plot_nb, 1, sharex=True)
        plt.subplots_adjust(hspace=0.3)
        fig.suptitle('Time frequency power plot (chanel 1).\n'+fr' Mouse nb:{mice_nb}, {random_choice}: {reward_time}, protocol {protocol_type}, {condition_type}'+'\n',weight='bold') #main figure title
        plot_position = 0
        if plot_nb==1:
            axes=ax
        if plot_nb>1:
            axes=ax[plot_position]
        
        if dic_graph_choice_ephy['Ch_group1_amplitude']:
            axes.imshow(Ch_group1_ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group1_extent,cmap='viridis')
            axes.set_title('Amplitude')
            axes.set_ylabel('Frequency (Hz)')
            ridge_map1 = [Ch_group1_ampl_map, Ch_group1_tfr_sampling_rate]

            plot_position +=1
        
        if dic_graph_choice_ephy['Ch_group1_power']:
            if plot_nb>1:
              axes=ax[plot_position]                
            axes.imshow(Ch_group1_power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group1_extent,cmap='viridis')
            axes.set_title('Power')
            axes.set_ylabel('Frequency (Hz)')
            ridge_map1 = [Ch_group1_power_map, Ch_group1_tfr_sampling_rate]
            
            plot_position +=1
        
        #Ridge Map
        if dic_graph_choice_ephy['Ch_group1_intensity'] or dic_graph_choice_ephy['Ch_group1_frequency']:
            ridge1,*_,y1 = scalo.ridge_line(ridge_map1[0],ridge_map1[1],t0=0,t1=9,f0=bandpass_dic['freq_low'],f1=bandpass_dic['freq_high'], rescale=True)
            ax[plot_position-1].plot(Ch_group1_map_times[:-1],y1,color='r')
            
            if dic_graph_choice_ephy['Ch_group1_intensity']:
                if plot_nb>1:
                  axes=ax[plot_position]
                axes.plot(Ch_group1_map_times[:-1],ridge1,color='r',alpha=0.5)            
                axes.set_title('Amplitude of the ridge')
                axes.set_ylabel('Amplitude (V)')
    
                plot_position +=1
                
            if dic_graph_choice_ephy['Ch_group1_frequency']:
                if plot_nb>1:
                  axes=ax[plot_position] 
                axes.plot(Ch_group1_map_times[:-1],y1,color='r',alpha=0.5)            
                axes.set_title('Frequency of the ridge')
                axes.set_ylabel('Frequency (Hz)')
            

        axes.set_xlabel('Time (s)')
        
        reward_time= str(reward_time)
        current_reward_time = int(reward_time[-3:])
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

        

def ephy_mean(list_condition_path_ephy, list_files, bandpass_dic):

    #Structure of the probe
    ch_group = ([14,9,12,11,10,13,8,15],[7,0,5,2,3,4,1,6])
        
    signal = {}
    for i in list_files:
        path = list_condition_path_ephy+'\\'+i
        sigs = np.fromfile(path, dtype=float).reshape(-1,16)
        for ind,gr in enumerate(ch_group):
            if f'Ch_group {ind}' not in signal:
                signal[f'Ch_group {ind}'] = sigs[:,gr]
            else:
                signal[f'Ch_group {ind}'] = np.hstack((signal[f'Ch_group {ind}'],sigs[:,gr]))
    mean = {}
    for k,v in signal.items():
        mean[f'Mean of {k}'] = np.mean(v,axis=1)
    

    if bandpass_dic['on_bandpass']:
        if bandpass_dic['freq_low'] == 0:
            bandpass_dic['freq_low'] = 0.1
        mean_temp={}
        for key, value in mean.items():
            mean_temp[key] = filters.bandpass_filter(value, order=8, sample_rate=bandpass_dic['sample_rate'],freq_low=bandpass_dic['freq_low'], freq_high=bandpass_dic['freq_high'], axis=0)
        for key, value in mean_temp.items(): 
            mean[key]=value
    mean['time']= list(np.arange(0, mean['Mean of Ch_group 0'].shape[0]/20000, 1/20000))
    return mean


def ephy_time_freq(list_condition_path_ephy, mean, ch_group, bandpass_dic):
    

    #Convolve the signal with the complex Morlet wavelet
    complex_map, map_times, freqs, tfr_sampling_rate = scalo.compute_timefreq(mean[fr'Mean of Ch_group {ch_group}'],sampling_rate=20000, f_start=0.1, f_stop=30.1, delta_freq=0.1, nb_freq=None,f0=2.5,  normalisation = 0, t_start=0)
    
    #The result is a complex array so to obtain the amplitude values we need to calculate the absolute value of the array
    ampl_map = (np.abs(complex_map))
    #Whereas to get the power values we simply have to square the amplitude result
    power_map = ampl_map**2
    
    return complex_map, map_times, freqs, tfr_sampling_rate, ampl_map, power_map 

    """
    #Behavioural events
    for a in ax:
        a.axvspan(0,0.5, color='green', alpha=0.2)
        a.axvspan(1.5,2, color='green', alpha=0.2)
        a.axvspan(2.55,2.7, color='r', alpha=0.2)
    
    
    #Plot the ridge of theta (4-12 Hz)
    ridge,*_,y = scalo.ridge_line(ampl_map,tfr_sampling_rate,t0=0, t1=9,f0=4,f1=12, rescale=True)
    ax[0].plot(map_times[:-1],y,color='r')
    
    
    
    
    #Now we can plot the ridge by focusing on the amplitude values
    plt.plot(map_times[:-1],ridge,color='r',alpha=0.5)
    
    plt.title('Ridge of amplitude of theta')
    plt.ylabel('Amplitude (V)')
    plt.xlabel('Time (s)')
    
    #Behavioural events
    plt.axvspan(0,0.5, color='green', alpha=0.2)
    plt.axvspan(1.5,2, color='green', alpha=0.2)
    plt.axvspan(2.55,2.7, color='r', alpha=0.2)

"""

if __name__ == '__main__' :

    
    #wheel speed
    v = B.load_lickfile("C:/Users/bivoc/Documents/Cour/M2/Stage/code/data/Behaviour/Group 15/173/Random Delay/P13/173_2020_07_26_11_15_45.coder", wheel=True)
    random_delay=B.extract_random_delay("C:/Users/bivoc/Documents/Cour/M2/Stage/code/data/Behaviour/Group 15/173/Random Delay/P13/173_2020_07_26_11_15_45.param")
    delays, wheel_by_delay = B.separate_by_delay(random_delay, v) 


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

    #path finder
    group_nb = '15'
    mice_nb = '173'
    expermiment_type = 'Random Delay'
    protocol_type = 'P13'
    condition_type = 'stim'
    dic = path_finder('C:/Users/Master5.INCI-NSN/Desktop/Pierre/data', group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
    
"""