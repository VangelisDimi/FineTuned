import tkinter as tk
from PIL import ImageTk, Image
import winsound
import pyglet

from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note,neighbour_note_frequency

pyglet.font.add_file('Assets/LcdSolid-VPzB.ttf')


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PyTuner")
        self.iconbitmap("Assets/icon_128.ico")
        self.geometry("550x400")
        self.minsize(550, 400)

        # Note Display
        self.Note_label = tk.Label(self, text='*', font=("LCD Solid", 70, 'bold'), width=5)
        self.grid_columnconfigure(4, weight=6)
        self.Note_label.grid(row=0, column=4)


        # frequency display
        self.freq_label = tk.Label(self, text='* Hz ()', font=('LCD Solid', 25))
        self.freq_label.grid(row=1, columnspan=9)

        # Indicators
        i_w = 7
        i_h = 24
        scaling_factor = 3

        self.i_empty = ImageTk.PhotoImage(
            Image.open("Assets/Indicators/indicator_empty.png").resize((i_w * scaling_factor, i_h * scaling_factor),
                                                                       resample=Image.NEAREST))
        self.indicator_img = []
        for i in range(4):
            self.indicator_img.append(
                ImageTk.PhotoImage(Image.open("Assets/Indicators/indicator_{}.png".format(i)).resize(
                    (i_w * scaling_factor, i_h * scaling_factor), resample=Image.NEAREST)))

        # Left
        self.left_indicators = []
        for i in range(4):
            self.left_indicators.append(tk.Label(self, image=self.i_empty))
            self.grid_columnconfigure(i, weight=1)
            self.left_indicators[i].grid(row=0, column=i)
        # Right
        self.right_indicators = []
        for i in range(4):
            self.right_indicators.append(tk.Label(self, image=self.i_empty))
            self.grid_columnconfigure(i + 5, weight=1)

            self.right_indicators[i].grid(row=0, column=i + 5)


        #Row configure
        for i in range(2):
            self.rowconfigure(i, weight=1)


        self.no_update_count = 0
        self.updated_indicator = None
        self.last_direction = None
        self.previous_note = None

    def clear_indicator(self):
        if self.last_direction == None: return

        if self.last_direction == '✓':
            self.Note_label.configure(fg="black")
        else:
            self.updated_indicator.configure(image=self.i_empty)

        self.last_direction = None
        self.updated_indicator = None

    def clear_labels(self):
        # remove text from all labels
        self.clear_indicator()
        self.Note_label.configure(text='*')
        self.freq_label.configure(text='* Hz ()')

    def update_labels(self, Note, frequency, tune_direction, tune_level, tune_amount):
        # update all labels
        self.clear_indicator()
        self.Note_label.configure(text=Note)
        self.freq_label.configure(
            text=(round(frequency, 1), "Hz", "({}{})".format(tune_direction, round(tune_amount, 2))))

        # Update indicators
        if tune_direction == '✓':
            self.Note_label.configure(fg="#00ff1b")
            if Note != self.previous_note:
                winsound.PlaySound('Assets/tune_sound.wav', winsound.SND_FILENAME + winsound.SND_ASYNC)
                self.previous_note=Note
        elif tune_direction == '↓':
            self.right_indicators[tune_level].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.right_indicators[tune_level]
            self.previous_note=None
        elif tune_direction == '↑':
            self.left_indicators[abs(tune_level - 3)].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.left_indicators[abs(tune_level - 3)]
            self.previous_note=None
        self.last_direction = tune_direction


def main_gui():
    app = main_window()
    audio_generator = read_real_time_audio()
    no_update_count = 0

    def update_labels():
        sample_rate, signal = next(audio_generator)
        _, _, _, loudest_frequency, loudest_frequency_amplitude = audio_fft(signal, sample_rate)
        closest_frequency, closest_note = frequency_to_note(loudest_frequency, loudest_frequency_amplitude)
        tune_direction = None
        tune_level = None

        if closest_frequency is not None and closest_note is not None:
            # Find tune direction
            if abs(loudest_frequency - closest_frequency) > 0.5:
                if loudest_frequency < closest_frequency:
                    tune_direction = '↑'
                else:
                    tune_direction = '↓'
            else:
                tune_direction = '✓'

            # Find tune level
            if tune_direction != '✓':
                neighbor = neighbour_note_frequency(closest_frequency,loudest_frequency)
                distance = abs(closest_frequency - neighbor)/2

                if abs(loudest_frequency - closest_frequency) > 0.8 * distance:
                    tune_level = 3
                elif abs(loudest_frequency - closest_frequency) > 0.6 * distance:
                    tune_level = 2
                elif abs(loudest_frequency - closest_frequency) > 0.3 * distance:
                    tune_level = 1
                elif abs(loudest_frequency - closest_frequency) > 0.5:
                    tune_level = 0

            app.update_labels(closest_note, loudest_frequency, tune_direction, tune_level,
                              abs(loudest_frequency - closest_frequency))
            app.no_update_count = 0
        else:
            app.no_update_count += 1
            if app.no_update_count == 3:
                app.clear_labels()
                app.no_update_count = 0

        app.after(1000, update_labels)

    update_labels()
    app.mainloop()
    audio_generator.close()
