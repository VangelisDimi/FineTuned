import numpy as np
from scipy.fft import fft, fftfreq


def audio_fft(signal, sample_rate, samples=None):
    """
    Performs Fast Fourier Transform on audio signal

    :param signal: the input audio signal in numpy array format
    :param sample_rate: the sample rate of the audio signal
    :param samples: the number of samples to consider
    :return: a tuple with dictionary with frequencies as keys and amplitudes as values, xf and yf, loudest frequency and
    loudest frequency amplitude
    """

    if samples is None:
        samples = len(signal)
    yf = fft(signal)
    xf = fftfreq(samples, 1 / sample_rate)[:samples // 2]

    frequencies = dict(zip(xf, samples * np.abs(yf[0:samples // 2])))
    loudest_frequency = max(frequencies, key=frequencies.get)
    return frequencies, xf, yf, loudest_frequency, frequencies[loudest_frequency]


# TODO: find a more efficient way to calculate closest frequency
# TODO: support more tunings (not only 440 Hz)
# TODO: find octave of closest note
def frequency_to_note(input_frequency, input_frequency_amplitude):
    """

    :param input_frequency: the loudest input frequency (fundamental)
    :param input_frequency_amplitude: the amplitude of the input frequency
    :return: a tuple with closest note frequency and closest note name
    """

    # source: http://techlib.com/reference/musical_note_frequencies.htm
    note_frequencies = {
        'A': [55.0, 110.0, 220.0, 440.0, 880.0],
        'A#': [58.27, 116.54, 233.08, 466.16, 932.32],
        'B': [61.74, 123.48, 246.96, 493.92, 987.84],
        'C': [65.41, 130.82, 261.64, 523.28, 1046.56],
        'C#': [69.30, 138.60, 277.20, 554.40, 1108.80],
        'D': [73.42, 146.84, 293.68, 587.36, 1174.72],
        'D#': [77.78, 155.56, 311.12, 622.24, 1244.48],
        'E': [82.41, 164.82, 329.64, 659.28, 1318.56],
        'F': [87.31, 174.62, 349.24, 698.48, 1396.96],
        'F#': [92.50, 185.00, 370.00, 740.00, 1480.00],
        'G': [98.00, 196.00, 392.00, 784.00, 1568.00],
        'Ab': [103.83, 207.66, 415.32, 830.64, 1661.28]
    }
    frequency_threshold = 15
    amplitude_threshold = 2000000  # TODO: play with threshold on different devices
    min_frequency = 80
    max_frequency = 1000

    if input_frequency <= min_frequency or input_frequency >= max_frequency or \
            input_frequency_amplitude < amplitude_threshold:
        return None, None

    closest_frequency = None
    closest_note = None
    for note in note_frequencies.keys():
        for frequency in note_frequencies[note]:
            if abs(input_frequency - frequency) < frequency_threshold and (closest_frequency is None or (
                    abs(input_frequency - frequency) < abs(input_frequency - closest_frequency))):
                closest_frequency = frequency
                closest_note = note

    return closest_frequency, closest_note


if __name__ == '__main__':
    pass
