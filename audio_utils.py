import numpy as np
from scipy.fft import fft, fftfreq


def audio_fft(signal, sample_rate, samples=None):
    """
    Performs Fast Fourier Transform on audio signal

    :param signal: the input audio signal in numpy array format
    :param sample_rate: the sample rate of the audio signal
    :param samples: the number of samples to consider
    :return: a tuple with dictionary with frequencies as keys and amplitudes as values, xf and yf and loudest frequency
    """

    if samples is None:
        samples = len(signal)
    yf = fft(signal)
    xf = fftfreq(samples, 1 / sample_rate)[:samples // 2]

    frequencies = dict(zip(xf, samples * np.abs(yf[0:samples // 2])))
    return frequencies, xf, yf, max(frequencies, key=frequencies.get)
