import tkinter as tk
from tkinter import font

from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note

import pyglet

pyglet.font.add_file('Assets/LcdSolid-VPzB.ttf')


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PyTuner")
        self.iconbitmap("Assets/icon_128.ico")
        self.geometry("400x400")

        # Note Display
        self.Note_label = tk.Label(self, text='', font=("LCD Solid", 50, 'bold'))
        self.Note_label.pack()

        # frequency display
        self.freq_label = tk.Label(self, text='', font=('LCD Solid', 50, 'bold'))
        self.freq_label.pack()

    def clear_labels(self):
        # remove text from all labels
        self.Note_label['text'] = ""

    def update_labels(self, Note, frequency):
        # update all labels
        self.Note_label.configure(text=Note)
        self.freq_label.configure(text=frequency)



def main_gui():
    app = main_window()

    audio_generator = read_real_time_audio()

    def update_labels():
        sample_rate, signal = next(audio_generator)
        _, _, _, loudest_frequency, loudest_frequency_amplitude = audio_fft(signal, sample_rate)
        closest_frequency, closest_note = frequency_to_note(loudest_frequency, loudest_frequency_amplitude)
        tune_direction = None

        if closest_frequency is not None and closest_note is not None:
            app.update_labels(closest_note, loudest_frequency)

        app.after(500, update_labels)

    update_labels()
    app.mainloop()
    audio_generator.close()
