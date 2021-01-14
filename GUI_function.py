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

def wheel_speed (wheel):

    """
    first column is trial nb, second column is the time in wich the wheel as turn, 
    the third column is the instant speed of the wheel base of time diference between 2 position of the wheel 
    and the distance of 3.875 cm between those 2 position. 
    The first line of each trial is wrong because the previous time is attributaed to a other trial 
    and do not match
    """
    v = np.array([[wheel[i,0],wheel[i,1], (3.875/(wheel[i,1]-wheel[i-1,1]))]for i in range(len(wheel))]) 
    
        
    """
    dic wich separated the data of every trail in order for them to be average later. 
    the key is the trail number and the value is a ndarray of the time in wich 
    the wheel change position(first column) and the instantanious speed at that moment (second column)
    """
    trial_dic ={}
    i=1
    while i < 61: 
        index = np.where(v[:,0] == i)
        trial_dic[i]= np.array([[v[index[0][i],1],v[index[0][i],2]] for i in range(len(index[0]))])
        i+=1
               
    """
    dic wich group the instantenious speed of every trial into time slices (0.1 second per slice) this alow to
    average the data of evry trial (the time in wich the wheel change position is not the same in every trail)
    """
    sampling_dic = {}
    for cle in trial_dic.keys():
        i=0.1
        for time, speed in trial_dic[cle]:
            while True:
                if time <= i:
                    if speed > 150:
                        #print (cle, time, speed)
                        break # i remove the value that are above 1.5 meter/sec
                    append_value(sampling_dic, i, speed)
                    break
                else:
                    i+=0.1
    """
    The values for every time slices is then average
    """
    
    for cle1 in sampling_dic.keys():
        
        sampling_dic[cle1] = np.mean(sampling_dic[cle1])
        
    """
    Smoothed with a gaussian filter and plot the result
    """
    
    lists = sorted(sampling_dic.items()) # sorted by key, return a list of tuples
    
    x, y = zip(*lists) # unpack a list of pairs into two tuples
    
    y = gaussian_filter1d(y,sigma=2)
        
    data = np.array([[x[i],y[i]]for i in range(len(x))])
    
    return data

def plot_maker(wheel_data):
    plt.plot(wheel_data[:,0], wheel_data[:,1])
    plt.axvspan(0,0.5, facecolor="green", alpha=0.3)
    plt.axvspan(1.5,2, facecolor="green", alpha=0.3)
    plt.axvspan(2.55,2.7, facecolor="red", alpha=0.3)
    plt.show()


def path_finder(main_folder_path, group_nb = '', mice_nb = '', experiment_type = '', protocol_type = '', condition_type = ''):
    group_nb = fr'*{group_nb}'
    mice_nb = fr'*{mice_nb}'
    experiment_type = fr'*{experiment_type}'
    protocol_type = fr'*{protocol_type}'
    condition_type = fr'*{condition_type}'
    
    #first we save the path to all the folder with the name 'group_nb'
    list_group_path_ephy = glob.glob(os.path.join(main_folder_path+'/Ephy', group_nb))
    list_group_path_behaviour = glob.glob(os.path.join(main_folder_path+'/Behaviour', group_nb))      
    list_group = [os.path.basename(group)for group in list_group_path_ephy]
    
    #in thoses folders we save the path to all the folder with the name 'mice_nb'
    list_mice_path_ephy = [glob.glob(os.path.join(group_path+fr'/{mice_nb}*'))for group_path in list_group_path_ephy]
    list_mice_path_ephy = [item for sublist in list_mice_path_ephy for item in sublist]
    
    list_mice_path_behaviour = [glob.glob(os.path.join(group_path, mice_nb))for group_path in list_group_path_behaviour]
    list_mice_path_behaviour = [item for sublist in list_mice_path_behaviour for item in sublist]
    
    list_mice = [os.path.basename(mice)[0:3]for mice in list_mice_path_ephy]
    #mice_sex = [os.path.basename(mice)[0:3]for mice in list_mice_path]
    
    #in thoses folders we load all the folder with th name experiment_type
    list_experiment_path_ephy = [glob.glob(os.path.join(mice_path+'/Experiment', experiment_type))for mice_path in list_mice_path_ephy]
    list_experiment_path_ephy = [item for sublist in list_experiment_path_ephy for item in sublist]
    
    list_experiment_path_behaviour = [glob.glob(os.path.join(mice_path, experiment_type))for mice_path in list_mice_path_behaviour]
    list_experiment_path_behaviour= [item for sublist in list_experiment_path_behaviour for item in sublist]
    
    #in thoses folders we load all the folder with th name protocol_type
    list_protocol_path_ephy = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_ephy]
    list_protocol_path_ephy = [item for sublist in list_protocol_path_ephy for item in sublist]
    
    list_protocol_path_behaviour = [glob.glob(os.path.join(experiment_path, protocol_type))for experiment_path in list_experiment_path_behaviour]
    list_protocol_path_behaviour = [item for sublist in list_protocol_path_behaviour for item in sublist]
    
    list_condition_path_ephy = [glob.glob(os.path.join(protocol_path+fr'/{condition_type}'))for protocol_path in list_protocol_path_ephy]
    list_condition_path_ephy = [item for sublist in list_condition_path_ephy for item in sublist]

    
    list_protocol = ['NB','P0','P13','P15', 'P16', 'P18', 'T10', 'T11', 'T12']
    
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

def ephy_plot(list_condition_path_ephy, Ch_group0=True, Ch_group1=True, Ch_group0_power=True, Ch_group1_power=True, Ch_group0_amplitude=True, Ch_group1_amplitude=True):
    mean = ephy_mean(list_condition_path_ephy)    
    
#all session average by shank, raw plot
    if Ch_group0 or Ch_group1:
                
        plot_nb = int(Ch_group0)+int(Ch_group1)
    
        fig, ax = plt.subplots(1, plot_nb, sharex=True, sharey=True)
        fig.suptitle('Whole session average',weight='bold') #main figure title
        plot_position = 0
    
        if plot_nb==1:
            axes=ax
        elif plot_nb>1:
            axes=ax[plot_position]
            fig.set_size_inches(10, 5)
    
        if Ch_group0:
            #first subplot 
            axes.plot(mean['time'], mean['Mean of Ch_group 0'])
            axes.set_ylabel('') 
            axes.set_xlabel('Time (sec)')
            axes.set_title('Ch group 0') 
            plot_position +=1
        
        
        if Ch_group1:
            #second subplot 
            if plot_nb >1:
                axes=ax[plot_position]
        
            axes.plot(mean['time'], mean['Mean of Ch_group 1'])
            axes.set_ylabel('')
            axes.set_xlabel('Time (sec)')
            axes.set_title('Ch group 1') 
       
#all session average by shank, time frequency plot (power)            
    #Chanel 0 plot maker  
    if Ch_group0_power or Ch_group0_amplitude:
        ch_group = 0
        Ch_group0_complex_map, Ch_group0_map_times, Ch_group0_freqs, Ch_group0_tfr_sampling_rate, Ch_group0_ampl_map, Ch_group0_power_map = ephy_time_freq(list_condition_path_ephy, mean, ch_group)
        #This is simply to setup the plotting area (check imshow details to further understand, if interested)
        Ch_group0_delta_freq = Ch_group0_freqs[1] - Ch_group0_freqs[0]
        Ch_group0_extent = (Ch_group0_map_times[0], Ch_group0_map_times[-1], Ch_group0_freqs[0]-Ch_group0_delta_freq/2., Ch_group0_freqs[-1]+Ch_group0_delta_freq/2.)
        
        plot_nb=int(Ch_group0_power)+int(Ch_group0_amplitude)
        fig, ax = plt.subplots(plot_nb, 1, sharex=True, sharey=True)
        fig.suptitle('Time frequency power plot (chanel 0)',weight='bold') #main figure title
        plot_position = 0
        if plot_nb==1:
            axes=ax
        if plot_nb>1:
            axes=ax[plot_position]
        
        if Ch_group0_amplitude:
            axes.imshow(Ch_group0_ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group0_extent,cmap='viridis')
            axes.set_title('Ch group 0 amplitude')
            axes.set_ylabel('Frequency (Hz)')

            plot_position +=1
        
        if Ch_group0_power:
            if plot_nb>1:
              axes=ax[plot_position]                
            axes.imshow(Ch_group0_power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group0_extent,cmap='viridis')
            axes.set_title('Ch group 0 Power')
            axes.set_ylabel('Frequency (Hz)')

        axes.set_xlabel('Time (s)')
    
    #Chanel 1 plot maker
    if Ch_group1_power or Ch_group1_amplitude:
        ch_group = 1        
        Ch_group1_complex_map, Ch_group1_map_times, Ch_group1_freqs, Ch_group1_tfr_sampling_rate, Ch_group1_ampl_map, Ch_group1_power_map = ephy_time_freq(list_condition_path_ephy, mean, ch_group)                 
        #This is simply to setup the plotting area (check imshow details to further understand, if interested)
        Ch_group1_delta_freq = Ch_group1_freqs[1] - Ch_group1_freqs[0]
        Ch_group1_extent = (Ch_group1_map_times[0],Ch_group1_map_times[-1], Ch_group1_freqs[0]-Ch_group1_delta_freq/2., Ch_group1_freqs[-1]+Ch_group1_delta_freq/2.)
    
        plot_nb=int(Ch_group1_power)+int(Ch_group1_amplitude)
        fig, ax = plt.subplots(plot_nb, 1, sharex=True, sharey=True)
        fig.suptitle('Time frequency power plot (chanel 1)',weight='bold') #main figure title
        plot_position = 0
        if plot_nb==1:
            axes=ax
        if plot_nb>1:
            axes=ax[plot_position]
        
        if Ch_group1_amplitude:
            axes.imshow(Ch_group1_ampl_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group1_extent,cmap='viridis')
            axes.set_title('Ch group 1 amplitude')
            axes.set_ylabel('Frequency (Hz)')

            plot_position +=1
        
        if Ch_group1_power:
            if plot_nb>1:
              axes=ax[plot_position]                
            axes.imshow(Ch_group1_power_map.transpose(), interpolation='nearest', origin ='lower', aspect = 'auto', extent = Ch_group1_extent,cmap='viridis')
            axes.set_title('Ch group 1 Power')
            axes.set_ylabel('Frequency (Hz)')

        axes.set_xlabel('Time (s)')
        



def ephy_mean(list_condition_path_ephy):

    #Structure of the probe
    ch_group = ([14,9,12,11,10,13,8,15],[7,0,5,2,3,4,1,6])
 
    list_files = og.file_list(list_condition_path_ephy,no_extension=False,ext='.rbf')
    sigs = np.fromfile(list_condition_path_ephy+'\\'+list_files[-1], dtype=float).reshape(-1,16)
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
        
    mean['time']= list(np.arange(0, mean['Mean of Ch_group 0'].shape[0]/20000, 1/20000))

    
    return mean


def ephy_time_freq(list_condition_path_ephy, mean, ch_group):

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

    
    """
    #wheel speed
    v = B.load_lickfile("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.coder", wheel=True)
    random_delay=B.extract_random_delay("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.param")
    delays, wheel_by_delay = B.separate_by_delay(random_delay, v)   
    
    for cle in delays.keys():
        wheel_data = wheel_speed(wheel_by_delay[cle])        
        plot_maker(wheel_data)
    """

    #path finder
    group_nb = '15'
    mice_nb = '173'
    expermiment_type = 'Random Delay'
    protocol_type = 'P13'
    condition_type = 'Stim'
    dic = path_finder('C:/Users/Master5.INCI-NSN/Desktop/Pierre/data', group_nb, mice_nb, expermiment_type, protocol_type, condition_type)
    
