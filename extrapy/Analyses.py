# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 18:35:34 2020

@author: F.LARENO-FACCINI
"""

import numpy as np

def MAD(a,axis=None):
    '''
    Computes median absolute deviation of an array along given axis
    '''
    #Median along given axis but keep reduced axis so that result can still broadcast along a
   
    med = np.nanmedian(a, axis=axis, keepdims=True)
    mad = np.median(np.abs(a-med),axis=axis) #MAD along the given axis
   
    return mad