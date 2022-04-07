from scipy.io import wavfile
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import numpy as np


def read_audio_file(file_name):
    """
    Converts an audio file to an audio signal in numpy array format

    :param file_name: the name of the audio file to read
    :return: a tuple with the sample rate, the left channel and the right channel audio signal in numpy array format
    """

    if file_name.endswith('.wav'):
        sample_rate, signal = wavfile.read(file_name)
        left_channel_signal = signal[:, 0]
        right_channel_signal = signal[:, 1]

        return sample_rate, left_channel_signal, right_channel_signal
    else:
        raise Exception('Unsupported Audio Format')


def plot_audio_signal(signal, sample_rate, samples=10000, plot_max_samples=5000, plot_max_freq=1000):
    """
    Plots an audio signal in audio and frequency spectrum

    :param signal: the audio signal in numpy array format
    :param sample_rate: the sample rate of the audio signal
    :param samples: the desired amount of samples in the signal
    :param plot_max_samples: the amount of samples to plot
    :param plot_max_freq: the maximum frequency in the frequency spectrum plot
    """
    fig, axes = plt.subplots(nrows=2, ncols=1, num='Audio Signal Plot')

    # Audio Spectrum Plot
    axes[0].set_title('Time Domain')
    axes[0].set_xlim([0, plot_max_samples])
    axes[0].grid()
    axes[0].set_xlabel('Sample')
    axes[0].set_ylabel('Amplitude')
    axes[0].plot(signal)

    # Frequency Spectrum Plot

    # Fast Fourier Transform
    yf = fft(signal[:samples])
    xf = fftfreq(samples, 1 / sample_rate)[:samples // 2]

    frequencies = dict(zip(xf, samples * np.abs(yf[0:samples // 2])))

    axes[1].set_title('Frequency Domain (Fundamental Frequency: ' + str(max(frequencies, key=frequencies.get)) + ' Hz)')
    axes[1].set_xlim([0, plot_max_freq])
    axes[1].grid()
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Amplitude')
    axes[1].plot(xf, 2.0 / samples * np.abs(yf[0:samples // 2]))

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    sample_rate, left_channel, right_channel = read_audio_file('audio_samples/Guitar-E.wav')
    plot_audio_signal(left_channel, sample_rate)
