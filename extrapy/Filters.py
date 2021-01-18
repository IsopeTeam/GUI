# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 14:02:27 2019
@author: Federica Lareno Faccini (adapted from an original script of Sam Garcia)
"""

def bandpass_filter(signal, order=8, sample_rate=20000,freq_low=400,freq_high=2000, axis=0):
    
    import scipy.signal
    
    Wn = [freq_low/(sample_rate/2),freq_high/(sample_rate/2)]
    
    sos_coeff = scipy.signal.iirfilter(order,Wn,btype='band',ftype='butter',output='sos')
    
    filtered_signal = scipy.signal.sosfiltfilt(sos_coeff, signal, axis=axis)
    
    return filtered_signal



def notch_filter(signal, order=8, sample_rate=20000,freq_low=48,freq_high=52, axis=0):
    
    import scipy.signal as sig

    Wn = [freq_low/(sample_rate/2),freq_high/(sample_rate/2)]
    
    notch_coeff = sig.iirfilter(order,Wn,btype='bandstop',ftype='butter',output='sos')
    
    notch_signal = sig.sosfiltfilt(notch_coeff, signal, axis=axis)

    return notch_signal





##----------------------------------- TRIAL -----------------------------------
    
if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    import numpy as np    

    
    path = r'D:\F.LARENO.FACCINI\Preliminary Results\Ephy\Coordinate Hunting\852\RBF\VI\P19\2019-10-03T16-55-19_1300um_P19_VI.rbf'
    data = np.fromfile(path,dtype='float64').reshape(-1,16)
    
    sampling_rate = 20000
    freq_low=1.
    freq_high=100.
    
    duration = 1./sampling_rate * len(data[:,0])
    sig_times = np.arange(0, duration, 1./sampling_rate)
    
    notch = notch_filter(signal=data[:,1])
    
    plt.plot(sig_times, data[:,1], linewidth=0.3, alpha=0.3, color='k', label='Raw signal')
    plt.plot(sig_times, bandpass_filter(notch,freq_low=freq_low,freq_high=freq_high), linewidth=0.3, color='b', label='Filtered signal')
    plt.legend()
    
    #low = 0.0049
    #high = 0.0051
    #order = 2
    #filter_type = 'butter'
    #ripple = 3
    #
    #b, a = signal.iirfilter(order, [low, high], rp=ripple, btype='bandstop',
    #                 analog=False, ftype=filter_type)
    #w, h = signal.freqz(b, a, 1000)
    #
    ## Frequency Response
    #fig = plt.figure()
    #ax = fig.add_subplot(1, 1, 1)
    #ax.semilogx(w / (2*np.pi), 20 * np.log10(np.maximum(abs(h), 1e-5)))
    #ax.set_xlabel('Frequency [Hz]')
    #ax.set_ylabel('Amplitude [dB]')
    #ax.axis((10, 1000, -100, 10))
    #ax.grid(which='both', axis='both')