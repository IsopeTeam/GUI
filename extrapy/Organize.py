# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 10:52:04 2020

@author: F.LARENO-FACCINI
"""
import os
import glob
import extrapy.Behaviour as bv
import numpy as np

#Remove the extension from the name in the list
def remove_extension(names, ext='.rbf'):
    return [x.replace(f"{ext}","") for x in names]

def file_list(path, no_extension=True, ext='.xlsx'):
    files = [os.path.basename(i) for i in glob.glob(path+f'/*{ext}')]
    if no_extension:
        return remove_extension(files, ext)
    if not no_extension:
        return files

#Removes trials where the mouse licks only at the time of the reward (this is most probably a false positive of the water drop)
#and when the mouse doesn't lick until after 4 seconds (in this case he hasn't performed the task so we exclude it)
def remove_empty_trials(path,skip_last=False,end_of_second_cue=2):
    licks = bv.load_lickfile(path)
    
    ot = bv.extract_ot(path.replace('.lick','.param'),skip_last=skip_last)[0]/1000
    reward_len = bv.extract_water_duration(path.replace('.lick','.param'),skip_last=skip_last)[0]/1000
    len_delay = bv.extract_random_delay(path.replace('.lick','.param'),skip_last=skip_last)
    
    
    len_trial = int(len_delay[-1][1])
    for i in range(1,len_trial+1):
        reward_on = end_of_second_cue+len_delay[i-1][0]/1000+ot
        reward_off = reward_on+reward_len

        trial_x = licks[np.where((licks[:,0]==i) & (licks[:,1]<4))]
        good_licks = trial_x[np.where(~((trial_x[:,1]>=(reward_on)) & (trial_x[:,1]<=(reward_off))))]
        
        if len(good_licks)==0:
            licks = np.delete(licks,np.where(licks[:,0]==i),axis=0)
    if len_trial < licks[-1,0]:
        licks = np.delete(licks,np.where(licks[:,0]==licks[-1,0]),axis=0)

    return licks

if __name__ == '__main__':

    path = r"C:\Users\F.LARENO-FACCINI\Anaconda3\Lib\site-packages\extrapy"
    files = file_list(path, ext='.py')

