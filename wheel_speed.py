# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 11:52:45 2021
@author: Master5.INCI-NSN
"""
import extrapy.Behaviour as B
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import matplotlib.pyplot as plt


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

def wheel_speed (wheel, nb_trials=60):

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
    for i in range(1,nb_trials+1): 
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
    
    
    

def plot_maker(wheel_data):
    plt.plot(wheel_data[:,0], wheel_data[:,1])


if __name__ == '__main__' :
    v = B.load_lickfile("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.coder", wheel=True)
    random_delay=B.extract_random_delay("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.param")
    delays, wheel_by_delay = B.separate_by_delay(random_delay, v)   
    
    for val in wheel_by_delay.values():
        wheel_data = wheel_speed(val,nb_trials=60)        
        plot_maker(wheel_data)


    plt.axvspan(0,0.5, facecolor="green", alpha=0.3)
    plt.axvspan(1.5,2, facecolor="green", alpha=0.3)
    plt.axvspan(2.55,2.7, facecolor="red", alpha=0.3)
    plt.show()
