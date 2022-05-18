import numpy as np
from scipy.fft import fft, fftfreq
import math


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


def frequency_to_note(input_frequency, input_frequency_amplitude, f_0=440.0):
    """
    Returns the closest note and it's frequency, given an input frequency

    :param input_frequency: the loudest input frequency (fundamental)
    :param input_frequency_amplitude: the amplitude of the input frequency
    :param f_0: the frequency of A4 note (default: 440.0)
    :return: a tuple with closest note frequency and closest note name
    """

    # source: http://techlib.com/reference/musical_note_frequencies.htm
    # note_frequencies = {
    #     'A': [55.0, 110.0, 220.0, 440.0, 880.0],
    #     'A#': [58.27, 116.54, 233.08, 466.16, 932.32],
    #     'B': [61.74, 123.48, 246.96, 493.92, 987.84],
    #     'C': [65.41, 130.82, 261.64, 523.28, 1046.56],
    #     'C#': [69.30, 138.60, 277.20, 554.40, 1108.80],
    #     'D': [73.42, 146.84, 293.68, 587.36, 1174.72],
    #     'D#': [77.78, 155.56, 311.12, 622.24, 1244.48],
    #     'E': [82.41, 164.82, 329.64, 659.28, 1318.56],
    #     'F': [87.31, 174.62, 349.24, 698.48, 1396.96],
    #     'F#': [92.50, 185.00, 370.00, 740.00, 1480.00],
    #     'G': [98.00, 196.00, 392.00, 784.00, 1568.00],
    #     'G#': [103.83, 207.66, 415.32, 830.64, 1661.28]
    # }

    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    frequency_threshold = 15
    amplitude_threshold = 1000000  # TODO: play with threshold on different devices
    min_frequency = 80
    max_frequency = 1000

    if input_frequency <= min_frequency or input_frequency >= max_frequency or \
            input_frequency_amplitude < amplitude_threshold:
        return None, None

    closest_frequency = None
    closest_note = None

    a = 2 ** (1 / 12)
    for n in range(-37, 23):
        frequency = f_0 * a ** (n + 1)  # source: https://pages.mtu.edu/~suits/NoteFreqCalcs.html

        if closest_frequency is not None and abs(frequency - input_frequency) > closest_frequency:
            break

        if abs(input_frequency - frequency) < frequency_threshold and (closest_frequency is None or (
                abs(input_frequency - frequency) < abs(input_frequency - closest_frequency))):
            closest_frequency = frequency
            closest_note = notes[(n + 1) % 12]

    return closest_frequency, closest_note


def neighbour_note_frequency(note_frequency, frequency, f_0=440.0):
    """

    :param note_frequency: the closest note frequency
    :param frequency: the input
    :param f_0: the frequency of A4 note (default: 440.0)
    :return: returns the frequency of the second closest note
    """
    a = 2 ** (1 / 12)

    n = math.log(note_frequency / f_0, a)

    if frequency > note_frequency:
        return f_0 * a ** (n + 1)
    elif frequency < note_frequency:
        return f_0 * a ** (n - 1)

    return None


if __name__ == '__main__':
    print(neighbour_note_frequency(440, 441))
