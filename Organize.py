# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 10:52:04 2020

@author: F.LARENO-FACCINI
"""
import os
import glob

#Remove the extension from the name in the list
def remove_extension(names, ext='.rbf'):
    return [x.replace(f"{ext}","") for x in names]

def file_list(path, no_extension=True, ext='.xlsx'):
    files = [os.path.basename(i) for i in glob.glob(path+f'/*{ext}')]
    if no_extension:
        return remove_extension(files, ext)
    if not no_extension:
        return files



if __name__ == '__main__':

    path = r"C:\Users\F.LARENO-FACCINI\Anaconda3\Lib\site-packages\extrapy"
    files = file_list(path, ext='.py')

