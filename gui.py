import tkinter as tk
from PIL import ImageTk, Image
import winsound
import pyglet
from configparser import ConfigParser

from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note, neighbour_note_frequency

pyglet.font.add_file('Assets/LcdSolid-VPzB.ttf')


def open_image(path,scaling_factor=1,scaling_method=None,resample=None):
    if scaling_method == None :
        image = ImageTk.PhotoImage(file=path)
    if scaling_method == 'resize':
        image = Image.open(path)
        image = image.resize((int(image.width * scaling_factor), int(image.height * scaling_factor)),
                                    resample)
        image = ImageTk.PhotoImage(image)
    elif scaling_method == 'subsample':
        image = ImageTk.PhotoImage(file=path)
        image = image._PhotoImage__photo.subsample(int(scaling_factor))
    else:
        raise ValueError('Invalid scaling_method.')
    return image


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        # App settings
        try:
            self.config = ConfigParser()
            with open('settings.ini') as f:
                self.config.read_file(f)
            if not self.config.has_option('sound', 'sound_on') or \
                not self.config.has_option('color', 'color_mode') or \
                not self.config.has_option('a4_tuning', 'frequency') or \
                not self.config.has_option('window','geometry') or \
                not self.config.has_option('window','zoomed') :
                raise ValueError('Configuration file has missing options.')
        except:
            self.config = ConfigParser()
            self.config['sound'] = {'sound_on': 'True'}
            self.config['color'] = {'color_mode' : 'light'}
            self.config['a4_tuning'] = {'frequency' : '440'}
            self.config['window'] = {'geometry' : '550x400',
                                     'zoomed' : 'False'}
            with open('settings.ini', 'w') as configfile:
                self.config.write(configfile)
        self.config.read('setting.ini')
        self.sound_on = self.config.getboolean('sound', 'sound_on')
        self.color_mode = self.config['color']['color_mode']
        self.geometry(self.config['window']['geometry'])
        if self.config.getboolean('window', 'zoomed') == True :
            self.state("zoomed")

        #Window options
        self.title("FineTuned")
        self.iconbitmap("Assets/icon_32.ico")
        self.minsize(470, 200)

        self.light_color = 'white'
        self.dark_color = '#262b2f'
        self.bg = None
        self.fg = None

        # Note Display frame
        self.Note_frame = tk.Frame(self)
        for i in range(2):
            self.Note_frame.columnconfigure(i, weight=1)

        self.Note_label = tk.Label(self.Note_frame, text='*', font=("LCD Solid", 70, 'bold'), width=2)
        self.Note_label.grid(row=0,column=0)
        self.octave_label = tk.Label(self.Note_frame, text='*', font=("LCD Solid", 45, 'bold'), width=2,padx=1)
        self.octave_label.grid(row=0,column=1)
        self.columnconfigure(4, weight=6)
        self.Note_frame.grid(row=0, column=4)

        # Frequency display
        self.freq_label = tk.Label(self, text='* Hz ()', font=('LCD Solid', 25))
        self.freq_label.grid(row=1, columnspan=9)

        # Indicators
        scaling_factor = 3

        self.i_empty_l = open_image("Assets/Indicators/light/indicator_empty.png",scaling_factor,'resize',Image.NEAREST)
        self.i_empty_d = open_image("Assets/Indicators/dark/indicator_empty.png",scaling_factor,'resize',Image.NEAREST)

        self.indicator_img_l = []
        self.indicator_img_d = []
        for i in range(4):
            self.indicator_img_l.append(open_image("Assets/Indicators/light/indicator_{}.png".format(i),scaling_factor,'resize',Image.NEAREST))
            self.indicator_img_d.append(open_image("Assets/Indicators/dark/indicator_{}.png".format(i),scaling_factor,'resize',Image.NEAREST))

        if self.color_mode == 'light':
            self.indicator_img=self.indicator_img_l
            self.i_empty = self.i_empty_l
        else:
            self.indicator_img=self.indicator_img_d
            self.i_empty = self.i_empty_d

        # Left
        self.left_indicators = []
        for i in range(4):
            self.left_indicators.append(tk.Label(self, image=self.i_empty))
            self.columnconfigure(i, weight=1)
            self.left_indicators[i].grid(row=0, column=i)
        # Right
        self.right_indicators = []
        for i in range(4):
            self.right_indicators.append(tk.Label(self, image=self.i_empty))
            self.columnconfigure(i + 5, weight=1)

            self.right_indicators[i].grid(row=0, column=i + 5)

        # Row configure
        for i in range(3):
            self.rowconfigure(i, weight=1)

        #Color mode button
        self.color_mode_dark = open_image("Assets/buttons/color_mode_dark.png",0.9,'resize')
        self.color_mode_light = open_image("Assets/buttons/color_mode_light.png",0.9,'resize')
        
        if self.color_mode == 'light':
            self.color_mode_icon = self.color_mode_dark
        else:
            self.color_mode_icon = self.color_mode_light
        self.color_mode_button = tk.Button(self, bd=0, image=self.color_mode_icon,
                                            command=self.switch_color_mode)
        self.color_mode_button.grid(row=2, column=5, columnspan=4)

        if self.color_mode == 'light':
            self.bg = self.light_color
            self.fg = self.dark_color
        else:
            self.bg = self.dark_color
            self.fg = self.light_color

        # Sound control button
        self.i_sound_on_l = open_image("Assets/buttons/sound_light.png",scaling_factor,'resize',Image.NEAREST)
        self.i_sound_off_l = open_image("Assets/buttons/mute_light.png",scaling_factor,'resize',Image.NEAREST)
        self.i_sound_on_d = open_image("Assets/buttons/sound_dark.png",scaling_factor,'resize',Image.NEAREST)
        self.i_sound_off_d = open_image("Assets/buttons/mute_dark.png",scaling_factor,'resize',Image.NEAREST)

        if self.color_mode == 'light':
            self.i_sound_on = self.i_sound_on_l
            self.i_sound_off = self.i_sound_off_l
        else:
            self.i_sound_on = self.i_sound_on_d
            self.i_sound_off = self.i_sound_off_d

        if self.sound_on:
            self.sound_mute_b = tk.Button(image=self.i_sound_on,bd=0, command=self.sound_button_pressed)
        else:
            self.sound_mute_b = tk.Button(image=self.i_sound_off,bd=0, command=self.sound_button_pressed)
        self.sound_mute_b.grid(row=2, column=0, columnspan=4)

        # A4 frequency tuning
        self.A4_freq = tk.StringVar()
        self.A4_freq.set(self.config['a4_tuning']['frequency'])

        self.A4_freq_frame = tk.Frame()
        for i in range(4):
            self.A4_freq_frame.columnconfigure(i, weight=1)
        self.A4_label_1 = tk.Label(self.A4_freq_frame,text="A4=",font=("LCD Solid", 20))
        self.A4_label_1.grid(row=0,column=0)
        self.A4_freq_spinbox = tk.Spinbox(self.A4_freq_frame,font=("LCD Solid", 20),from_=300,to=500,textvariable=self.A4_freq, width=4,state='readonly')
        self.A4_freq_spinbox.grid(row=0,column=1)
        self.A4_label_2 = tk.Label(self.A4_freq_frame,text="Hz",font=("LCD Solid", 20),padx=10)
        self.A4_label_2.grid(row=0,column=2)

        self.i_reset_l = open_image("Assets/buttons/reset_icon_light.png",3,'subsample')
        self.i_reset_d = open_image("Assets/buttons/reset_icon_dark.png",3,'subsample')
        if self.color_mode == 'light':
            self.i_reset = self.i_reset_l
        else:
            self.i_reset = self.i_reset_d
        self.A4_reset_b = tk.Button(self.A4_freq_frame,image=self.i_reset,bd=0,command=self.reset_a4_frequency)
        self.A4_reset_b.grid(row=0,column=3)

        self.A4_freq_frame.grid(row=2,column=4)

        #Variables for gui updates        
        self.no_update_count = 0
        self.updated_indicator = None
        self.last_direction = None
        self.previous_note = None
        self.last_tune_level = None

        self.last_state = self.state()

        self.protocol("WM_DELETE_WINDOW",self.on_exit)
        self.bind( "<Configure>", self.on_config)
        self.update_color()
    
    def on_config(self,event):
        #Used to restore window if it's closed while minimized
        if self.state() == 'zoomed' or self.state() == 'normal':
            self.last_state = self.state()

    def reset_a4_frequency(self):
        self.A4_freq.set('440')

    def sound_button_pressed(self):
        if self.sound_on:
            self.sound_mute_b.configure(image=self.i_sound_off)
        else:
            self.sound_mute_b.configure(image=self.i_sound_on)
        self.sound_on = not self.sound_on

    def on_exit(self):
        # Write settings to file
        self.config['sound']['sound_on'] = str(self.sound_on)
        self.config['color']['color_mode'] = self.color_mode
        self.config['a4_tuning']['frequency'] = self.A4_freq.get()
        self.config['window']['geometry'] = self.geometry()
        if self.state() == 'zoomed':
            self.config['window']['zoomed'] = 'True'
        elif self.state() == 'normal':
            self.config['window']['zoomed'] = 'False'
        elif self.state() == 'iconic':
            self.config['window']['zoomed'] = 'False'
            if self.last_state == 'zoomed':
                self.config['window']['geometry'] = '550x400'
        with open('settings.ini', 'w') as configfile:
            self.config.write(configfile)
        #Close window
        self.destroy()

    def clear_indicator(self):
        if self.last_direction == None: return

        if self.last_direction == '✓':
            self.Note_label.configure(fg=self.fg)
        else:
            self.updated_indicator.configure(image=self.i_empty)

        self.last_direction = None
        self.updated_indicator = None

    def clear_labels(self):
        # remove text from all labels
        self.clear_indicator()
        self.Note_label.configure(text='*', fg=self.fg)
        self.octave_label.configure(text='*',fg=self.fg)
        self.freq_label.configure(text='* Hz ()', fg=self.fg)

    def update_labels(self, Note, octave, frequency, tune_direction, tune_level, tune_amount):
        # update all labels
        self.clear_indicator()
        self.Note_label.configure(text=Note)
        self.octave_label.configure(text=octave)
        self.freq_label.configure(
            text=(round(frequency, 1), "Hz", "({}{})".format(tune_direction, round(tune_amount, 2))))

        # Update indicators
        if tune_direction == '✓':
            self.Note_label.configure(fg="#00ff1b")
            self.octave_label.configure(fg="#00ff1b")
            if Note != self.previous_note:
                if self.sound_on:
                    winsound.PlaySound('Assets/tune_sound.wav', winsound.SND_FILENAME + winsound.SND_ASYNC)
                self.previous_note = Note
        elif tune_direction == '↓':
            self.Note_label.configure(fg=self.fg)
            self.octave_label.configure(fg=self.fg)
            self.freq_label.configure(fg=self.fg)

            self.right_indicators[tune_level].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.right_indicators[tune_level]
            self.previous_note = None
        elif tune_direction == '↑':
            self.Note_label.configure(fg=self.fg)
            self.octave_label.configure(fg=self.fg)
            self.freq_label.configure(fg=self.fg)

            self.left_indicators[abs(tune_level - 3)].configure(image=self.indicator_img[tune_level])
            self.updated_indicator = self.left_indicators[abs(tune_level - 3)]
            self.previous_note = None
        self.last_direction = tune_direction
        self.last_tune_level = tune_level

    def update_color(self):
        self.color_mode_button.configure(image=self.color_mode_icon, bg=self.bg, activebackground=self.bg)

        self['bg'] = self.bg
        if self.last_direction == '✓':
            self.Note_label.configure(background=self.bg)
            self.octave_label.configure(background=self.bg)
        else :
            self.Note_label.configure(background=self.bg,foreground=self.fg)
            self.octave_label.configure(background=self.bg,foreground=self.fg)
        self.freq_label.configure(background=self.bg, foreground=self.fg)
        self.Note_frame.configure(background=self.bg)

        self.sound_mute_b.configure(bg=self.bg, activebackground=self.bg)
        if self.sound_on:
            self.sound_mute_b.configure(image=self.i_sound_on)
        else:
            self.sound_mute_b.configure(image=self.i_sound_off)

        for i in range(4):
            self.left_indicators[i].configure(image=self.i_empty,bg=self.bg, fg=self.fg)
            self.right_indicators[i].configure(image=self.i_empty,bg=self.bg, fg=self.fg)
        
        if self.last_direction == '↓':
            self.right_indicators[self.last_tune_level].configure(image=self.indicator_img[self.last_tune_level])
        elif self.last_direction == '↑':
            self.left_indicators[abs(self.last_tune_level - 3)].configure(image=self.indicator_img[self.last_tune_level])

        self.A4_freq_frame['bg'] = self.bg
        self.A4_label_1.configure(background=self.bg,foreground=self.fg)
        self.A4_label_2.configure(background=self.bg,foreground=self.fg)
        self.A4_reset_b.configure(image=self.i_reset,background=self.bg,activebackground=self.bg)

    def switch_color_mode(self):
        if self.color_mode == 'light':
            self.color_mode = 'dark'
            self.bg = self.dark_color
            self.fg = self.light_color

            self.indicator_img=self.indicator_img_d
            self.i_empty = self.i_empty_d

            self.color_mode_icon = self.color_mode_light

            self.i_sound_on = self.i_sound_on_d
            self.i_sound_off = self.i_sound_off_d

            self.i_reset = self.i_reset_d
        else:
            self.color_mode = 'light'
            self.bg = self.light_color
            self.fg = 'black'

            self.indicator_img=self.indicator_img_l
            self.i_empty = self.i_empty_l

            self.color_mode_icon = self.color_mode_dark

            self.i_sound_on = self.i_sound_on_l
            self.i_sound_off = self.i_sound_off_l

            self.i_reset = self.i_reset_l

        self.update_color()


def main_gui():
    app = main_window()
    audio_generator = read_real_time_audio()

    def update_labels():
        f_0 = int(app.A4_freq.get())
        sample_rate, signal = next(audio_generator)
        _, _, _, loudest_frequency, loudest_frequency_amplitude = audio_fft(signal, sample_rate)
        closest_frequency, closest_note, octave = frequency_to_note(loudest_frequency, loudest_frequency_amplitude , f_0)
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
                neighbor = neighbour_note_frequency(closest_frequency, loudest_frequency , f_0)
                distance = abs(closest_frequency - neighbor) / 2

                if abs(loudest_frequency - closest_frequency) > 0.8 * distance:
                    tune_level = 3
                elif abs(loudest_frequency - closest_frequency) > 0.6 * distance:
                    tune_level = 2
                elif abs(loudest_frequency - closest_frequency) > 0.3 * distance:
                    tune_level = 1
                elif abs(loudest_frequency - closest_frequency) > 0.5:
                    tune_level = 0

            app.update_labels(closest_note, octave, loudest_frequency, tune_direction, tune_level,
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