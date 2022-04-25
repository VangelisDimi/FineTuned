from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from audio_utils import audio_fft, frequency_to_note


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


def read_real_time_audio():
    """
    Reads real time audio from audio input and yields audio signal in numpy array format

    :return: a tuple with the sample rate and audio signal in numpy array format
    """

    try:
        rate = 44100
        record_seconds = 20
        chunk_size = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, input=True, frames_per_buffer=chunk_size)

        # iteratively read from audio stream
        while True:
            data = stream.read(chunk_size)
            np_data = np.frombuffer(data, dtype=np.float32)
            yield rate, np_data

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def plot_audio_signal(signal, sample_rate, samples=None, plot_max_samples=5000, plot_max_freq=1000):
    """
    Plots an audio signal in audio and frequency domain

    :param signal: the audio signal in numpy array format
    :param sample_rate: the sample rate of the audio signal
    :param samples: the desired amount of samples in the signal
    :param plot_max_samples: the amount of samples to plot
    :param plot_max_freq: the maximum frequency in the frequency spectrum plot
    """
    fig, axes = plt.subplots(nrows=2, ncols=1, num='Audio Signal Plot')

    # Time Domain Plot
    axes[0].set_title('Time Domain')
    axes[0].set_xlim([0, plot_max_samples])
    axes[0].grid()
    axes[0].set_xlabel('Sample')
    axes[0].set_ylabel('Amplitude')
    axes[0].plot(signal)

    # Frequency Domain Plot

    # Fast Fourier Transform
    if samples is None:
        samples = len(signal)

    frequencies, xf, yf, loudest_frequency, _ = audio_fft(signal, sample_rate, samples)

    axes[1].set_title(
        'Frequency Domain (Fundamental Frequency: ' + str(round(loudest_frequency, 2)) + ' Hz)')
    axes[1].set_xlim([0, plot_max_freq])
    axes[1].grid()
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Amplitude')
    axes[1].plot(xf, 2.0 / samples * np.abs(yf[0:samples // 2]))

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    pass
