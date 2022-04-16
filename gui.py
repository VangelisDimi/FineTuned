import tkinter as tk
import os

#Window
app = tk.Tk()
app.title("PyTuner")
winimg = tk.PhotoImage(file='./Assets/icon_128.png')
app.tk.call('wm', 'iconphoto', app._w, winimg)

width = app.winfo_screenwidth()
height = app.winfo_screenheight()

app.mainloop()