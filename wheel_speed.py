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

if __name__ == '__main__' :
    v = B.load_lickfile("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.coder", wheel=True)
    random_delay=B.extract_random_delay("C:/Users/Master5.INCI-NSN/Desktop/Pierre/ER-P13/173_2020_07_26_11_15_45.param")
    delays, wheel_by_delay = B.separate_by_delay(random_delay, v)   
    
    for cle in delays.keys():
        wheel_data = wheel_speed(wheel_by_delay[cle])        
        plot_maker(wheel_data)


    
"""
plt.plot(x, y)
plt.axvspan(0,0.5, facecolor="green", alpha=0.3)
plt.axvspan(1.5,2, facecolor="green", alpha=0.3)
plt.axvspan(2.55,2.7, facecolor="red", alpha=0.3)
plt.show()
"""
