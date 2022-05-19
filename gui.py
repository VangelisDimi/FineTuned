import tkinter as tk
from PIL import ImageTk, Image
import winsound
import pyglet
from configparser import ConfigParser

from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note, neighbour_note_frequency

pyglet.font.add_file('Assets/LcdSolid-VPzB.ttf')


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PyTuner")
        self.iconbitmap("Assets/icon_128.ico")
        self.color_mode = 'light'
        self.geometry("550x400")
        self.minsize(550, 400)

        # Note Display
        self.Note_label = tk.Label(self, text='*', font=("LCD Solid", 70, 'bold'), width=5)
        self.columnconfigure(4, weight=6)
        self.Note_label.grid(row=0, column=4)

        # frequency display
        self.freq_label = tk.Label(self, text='* Hz ()', font=('LCD Solid', 25))
        self.freq_label.grid(row=1, columnspan=9)

        # Indicators
        i_w = 7
        i_h = 24
        scaling_factor = 3

        i_empty = Image.open("Assets/Indicators/indicator_empty.png")
        i_empty = i_empty.resize((i_empty.width * scaling_factor, i_empty.height * scaling_factor),
                                 resample=Image.NEAREST)
        self.i_empty = ImageTk.PhotoImage(i_empty)

        self.indicator_img = []
        for i in range(4):
            indicator_img = Image.open("Assets/Indicators/indicator_{}.png".format(i))
            indicator_img = indicator_img.resize(
                (indicator_img.width * scaling_factor, indicator_img.height * scaling_factor),
                resample=Image.NEAREST)
            self.indicator_img.append(ImageTk.PhotoImage(indicator_img))

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
            self.columnconfigure(i + 5, weight=1)

            self.right_indicators[i].grid(row=0, column=i + 5)

        # Row configure
        for i in range(2):
            self.rowconfigure(i, weight=1)

        self.settings_frame = tk.Frame(self)
        self.settings_frame.grid(row=2, columnspan=9)

        self.color_mode_dark = tk.PhotoImage(file="Assets/buttons/color_mode_dark.png")
        self.color_mode_light = tk.PhotoImage(file="Assets/buttons/color_mode_light.png")

        self.color_mode_button = tk.Button(self, bd=0, image=self.color_mode_dark,
                                           command=self.switch_color_mode)

        self.color_mode_button.grid(row=2, column=5, columnspan=4)

        # App settings
        self.config = ConfigParser()
        try:
            with open('settings.ini') as f:
                self.config.read_file(f)
        except:
            self.config['sound'] = {'sound_on': 'True'}
            with open('settings.ini', 'w') as configfile:
                self.config.write(configfile)

        self.config.read('setting.ini')
        self.sound_on = self.config.getboolean('sound', 'sound_on')

        # Sound control button
        i_sound_on = Image.open("Assets/sound.png")
        i_sound_on = i_sound_on.resize((i_sound_on.width * scaling_factor, i_sound_on.height * scaling_factor),
                                       resample=Image.NEAREST)
        self.i_sound_on = ImageTk.PhotoImage(i_sound_on)
        i_sound_off = Image.open("Assets/mute.png")
        i_sound_off = i_sound_off.resize((i_sound_off.width * scaling_factor, i_sound_off.height * scaling_factor),
                                         resample=Image.NEAREST)
        self.i_sound_off = ImageTk.PhotoImage(i_sound_off)

        if self.sound_on:
            self.sound_mute_b = tk.Button(image=self.i_sound_on, command=self.sound_button_pressed)
        else:
            self.sound_mute_b = tk.Button(image=self.i_sound_off, command=self.sound_button_pressed)
        self.sound_mute_b.grid(row=2, column=0, columnspan=4)

        self.no_update_count = 0
        self.updated_indicator = None
        self.last_direction = None
        self.previous_note = None

    def sound_button_pressed(self):
        if self.sound_on:
            self.sound_mute_b.configure(image=self.i_sound_off)
        else:
            self.sound_mute_b.configure(image=self.i_sound_on)
        self.sound_on = not self.sound_on

    def on_exit(self):
        # Write settings to file
        self.config['sound']['sound_on'] = str(self.sound_on)
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)

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
        if self.color_mode == 'light':
            self.Note_label.configure(text='*', fg='#262b2f')
            self.freq_label.configure(text='* Hz ()', fg='#262b2f')
        else:
            self.Note_label.configure(text='*', fg='white')
            self.freq_label.configure(text='* Hz ()', fg='white')

    def update_labels(self, Note, frequency, tune_direction, tune_level, tune_amount):
        # update all labels
        self.clear_indicator()
        self.Note_label.configure(text=Note)
        self.freq_label.configure(
            text=(round(frequency, 1), "Hz", "({}{})".format(tune_direction, round(tune_amount, 2))))

        if self.color_mode == 'light':
            self.Note_label.configure(fg='#262b2f')
            self.freq_label.configure(fg='#262b2f')
        else:
            self.Note_label.configure(fg='white')
            self.freq_label.configure(fg='white')

        # Update indicators
        if tune_direction == '✓':
            self.Note_label.configure(fg="#00ff1b")
            if Note != self.previous_note:
                if self.sound_on:
                    winsound.PlaySound('Assets/tune_sound.wav', winsound.SND_FILENAME + winsound.SND_ASYNC)
                self.previous_note = Note
        elif tune_direction == '↓':
            self.right_indicators[tune_level].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.right_indicators[tune_level]
            self.previous_note = None
        elif tune_direction == '↑':
            self.left_indicators[abs(tune_level - 3)].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.left_indicators[abs(tune_level - 3)]
            self.previous_note = None
        self.last_direction = tune_direction

    def switch_color_mode(self):
        light_color = 'white'
        dark_color = '#262b2f'

        if self.color_mode == 'light':
            self.color_mode_button.configure(image=self.color_mode_light, bg=dark_color, activebackground=dark_color)
            self.color_mode = 'dark'
            self['bg'] = dark_color
            self.Note_label.configure(background=dark_color, foreground=light_color)
            self.freq_label.configure(background=dark_color, foreground=light_color)

            for i in self.left_indicators:
                i.configure(bg=dark_color, fg=light_color)

            for i in self.right_indicators:
                i.configure(bg=dark_color, fg=light_color)

        else:
            self.color_mode_button.configure(image=self.color_mode_dark, bg=light_color, activebackground=light_color)
            self.color_mode = 'light'
            self['bg'] = light_color
            self.Note_label.configure(background=light_color, foreground=dark_color)
            self.freq_label.configure(background=light_color, foreground=dark_color)

            for i in self.left_indicators:
                i.configure(bg=light_color, fg=dark_color)

            for i in self.right_indicators:
                i.configure(bg=light_color, fg=dark_color)


def main_gui():
    app = main_window()
    audio_generator = read_real_time_audio()

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
                neighbor = neighbour_note_frequency(closest_frequency, loudest_frequency)
                distance = abs(closest_frequency - neighbor) / 2

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
    app.on_exit()
