# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 10:04:18 2019

@author: Sam Garcia (adapted by Federica Lareno Faccini)
"""
import numpy as np
import scipy.signal
from scipy import fftpack


def generate_wavelet_fourier(len_wavelet, f_start, f_stop, delta_freq, 
            sampling_rate, f0, normalisation):
    """
    Compute the wavelet coefficients at all scales and makes its Fourier transform.
    When different signal scalograms are computed with the exact same coefficients, 
        this function can be executed only once and its result passed directly to compute_morlet_scalogram
        
    Output:
        wf : Fourier transform of the wavelet coefficients (after weighting), Fourier frequencies are the first 
    """
    # compute final map scales
    scales = f0/np.arange(f_start,f_stop,delta_freq)*sampling_rate
    # compute wavelet coeffs at all scales
    xi=np.arange(-len_wavelet/2.,len_wavelet/2.)
    xsd = xi[:,np.newaxis] / scales
    wavelet_coefs=np.exp(complex(1j)*2.*np.pi*f0*xsd)*np.exp(-np.power(xsd,2)/2.)

    weighting_function = lambda x: x**(-(1.0+normalisation))
    wavelet_coefs = wavelet_coefs*weighting_function(scales[np.newaxis,:])

    # Transform the wavelet into the Fourier domain
    #~ wf=fft(wavelet_coefs.conj(),axis=0) <- FALSE
    wf=fftpack.fft(wavelet_coefs,axis=0)
    wf=wf.conj() # at this point there was a mistake in the original script
    
    return wf


def convolve_scalogram(sig, wf):
    """
    Convolve with fft the signal (in time domain) with the wavelet
    already computed in freq domain.
    
    Parameters
    ----------
    sig: numpy.ndarray (1D, float)
        The signal
    wf: numpy.array (2D, complex)
        The wavelet coefficient in fourrier domain.
    """
    n = wf.shape[0]
    assert sig.shape[0]<=n, 'the sig.size is longer than wf.shape[0] {} {}'.format(sig.shape[0], wf.shape[0])
    sigf=fftpack.fft(sig,n)
    wt_tmp=fftpack.ifft(sigf[:,np.newaxis]*wf,axis=0)
    wt = fftpack.fftshift(wt_tmp,axes=[0])
    return wt

def compute_timefreq(sig, sampling_rate, f_start, f_stop, delta_freq=1., nb_freq=None,
                f0=2.5,  normalisation = 0.,  min_sampling_rate=None, wf=None,
                t_start=0., zero_pad=True, joblib_memory=None):
    """
    
    """
    #~ print 'compute_timefreq'
    sampling_rate = float(sampling_rate)
    
    if nb_freq is not None:
        delta_freq = (f_stop-f_start)/nb_freq
    
    if min_sampling_rate is None:
        min_sampling_rate =  min(4.* f_stop, sampling_rate)
        
    
    #decimate
    ratio = int(sampling_rate/min_sampling_rate)
    #~ print 'ratio', ratio
    if ratio>1:
        # sig2 = tools.decimate(sig, ratio)
        sig2 = scipy.signal.decimate(sig, ratio, n=4, zero_phase=True)
    else:
        sig2 = sig
        ratio=1
    
    tfr_sampling_rate = sampling_rate/ratio
    #~ print 'tfr_sampling_rate', tfr_sampling_rate
    
    n_init = sig2.size
    if zero_pad:
        n = int(2 ** np.ceil(np.log(n_init)/np.log(2))) # extension to next power of  2
    else:
        n = n_init
    #~ print 'n_init', n_init, 'n', n
    if wf is None:
        if joblib_memory is None:
            func = generate_wavelet_fourier
        else:
            func = joblib_memory.cache(generate_wavelet_fourier)
        wf = func(n, f_start, f_stop, delta_freq, 
                            tfr_sampling_rate, f0, normalisation)
    
    assert wf.shape[0] == n
    
    wt = convolve_scalogram(sig2, wf)
    wt=wt[:n_init,:]
    
    freqs = np.arange(f_start,f_stop,delta_freq)
    times = np.arange(n_init)/tfr_sampling_rate + t_start
    return wt, times, freqs, tfr_sampling_rate


def ridge_map(ampl_map, threshold=70.):
    max_power = np.max(ampl_map) #Max power observed in frequency spectrum
    freq_power_threshold = float(threshold) #The threshold range for power detection of the ridge 
    cut_off_power = max_power/100.0*freq_power_threshold #Computes power above trheshold
    
    boolean_map = ampl_map >= cut_off_power #For plot 
    
    value_map = ampl_map
    
    for i,j in np.ndenumerate(ampl_map):
        if j <= cut_off_power:
            value_map[i] = 0.0 #For computation, all freq < trhesh = 0.0
            
    return boolean_map, value_map


def ridge_line(ampl_map, tfr_sampling_rate, delta_freq=0.1, t0=None, t1=None, f0=4, f1=12, rescale=False):
    freq0 = int(f0/delta_freq)
    freq1 = int(f1/delta_freq)
    if t1 is None and t0 is None:
        theta = ampl_map[:,freq0:freq1]
    else:
        time0 = int(tfr_sampling_rate*t0)
        time1 = int(tfr_sampling_rate*t1)
        theta = ampl_map[time0:time1,freq0:freq1]
    ridge = np.empty(len(theta))
    ridge[:] = np.nan
    y = np.empty(len(ridge))
    y[:] = np.nan
    for i in range(theta.shape[0]):
        ridge[i] = np.max(theta[i,:])
        y[i] = (np.where(theta[i,:] == ridge[i]))[0]
    if rescale:
        y[:] = y*delta_freq+f0
    x = np.arange(0,len(theta),1)  
    return ridge,theta,x,y
