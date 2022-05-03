import tkinter as tk
from PIL import ImageTk,Image

from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note

import pyglet

pyglet.font.add_file('Assets/LcdSolid-VPzB.ttf')


class main_window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PyTuner")
        self.iconbitmap("Assets/icon_128.ico")
        self.geometry("550x400")
        self.minsize(550,400)

        # Note Display
        self.Note_label = tk.Label(self, text='*', font=("LCD Solid", 70, 'bold'))
        self.Note_label.grid(row=0,column=4)

        # frequency display
        self.freq_label = tk.Label(self, text='* Hz ()', font=('LCD Solid', 25))
        self.freq_label.grid(row=1,column=4)

        #Indicators
        i_w=7
        i_h=24
        scaling_factor=3
        
        self.i_empty = ImageTk.PhotoImage(Image.open("Assets/Indicators/indicator_empty.png").resize((i_w*scaling_factor,i_h*scaling_factor),resample=Image.NEAREST))
        #left
        self.il4 = tk.Label(self, image=self.i_empty)
        self.il4.grid(row=0,column=0)
        self.il3 = tk.Label(self, image=self.i_empty)
        self.il3.grid(row=0,column=1)
        self.il2 = tk.Label(self, image=self.i_empty)
        self.il2.grid(row=0,column=2)
        self.il1 = tk.Label(self, image=self.i_empty)
        self.il1.grid(row=0,column=3)
        #Right
        self.ir1 = tk.Label(self, image=self.i_empty)
        self.ir1.grid(row=0,column=5)
        self.ir2 = tk.Label(self, image=self.i_empty)
        self.ir2.grid(row=0,column=6)
        self.ir3 = tk.Label(self, image=self.i_empty)
        self.ir3.grid(row=0,column=7)
        self.ir4 = tk.Label(self, image=self.i_empty)
        self.ir4.grid(row=0,column=8)


        #Grid configure
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)
        self.grid_columnconfigure(6, weight=1)
        self.grid_columnconfigure(7, weight=1)
        self.grid_columnconfigure(8, weight=1)
        #Row configure
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


        self.no_update_count=0

    def clear_indicators(self):
        self.il4.configure(image=self.i_empty)
        self.il3.configure(image=self.i_empty)
        self.il2.configure(image=self.i_empty)
        self.il1.configure(image=self.i_empty)
        self.ir4.configure(image=self.i_empty)
        self.ir3.configure(image=self.i_empty)
        self.ir2.configure(image=self.i_empty)
        self.ir1.configure(image=self.i_empty)
        self.Note_label.configure(fg="black")

    def clear_labels(self):
        # remove text from all labels
        # self.clear_indicators()
        self.Note_label.configure(text='*')
        self.freq_label.configure(text='* Hz ()')

    def update_labels(self, Note, frequency,tune_direction,tune_level):
        # update all labels
        # self.clear_indicators()
        self.Note_label.configure(text=Note)
        self.freq_label.configure(text=(frequency,"Hz","({})".format(tune_direction)))

        if tune_direction == '✓':
            self.Note_label.configure(fg="#00ff1b")



def main_gui():
    app = main_window()
    audio_generator = read_real_time_audio()
    no_update_count=0

    def update_labels():
        sample_rate, signal = next(audio_generator)
        _, _, _, loudest_frequency, loudest_frequency_amplitude = audio_fft(signal, sample_rate)
        closest_frequency, closest_note = frequency_to_note(loudest_frequency, loudest_frequency_amplitude)
        tune_direction = None
        tune_level = None

        if closest_frequency is not None and closest_note is not None:
            #Find tune direction
            if abs(loudest_frequency - closest_frequency) > 0.5:
                if loudest_frequency < closest_frequency:
                    tune_direction = '↑'
                else:
                    tune_direction = '↓'
            else:
                tune_direction = '✓'

            #Find tune level
            if abs(loudest_frequency - closest_frequency) > 100:
                tune_level=4
            elif abs(loudest_frequency - closest_frequency) > 50:
                tune_level=3
            elif abs(loudest_frequency - closest_frequency) > 25:
                tune_level=2
            elif abs(loudest_frequency - closest_frequency) > 10:
                tune_level=1

            app.update_labels(closest_note, loudest_frequency , tune_direction , tune_level)
            app.no_update_count=0
        else:
            app.no_update_count+=1
            if app.no_update_count==3:
                app.clear_labels()
                app.no_update_count=0


        app.after(1000, update_labels)

    update_labels()
    app.mainloop()
    audio_generator.close()
