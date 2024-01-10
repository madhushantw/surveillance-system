import tkinter as tk
from tkinter import *
from tkinter import ttk
import threading
import subprocess
from tkinter.ttk import Progressbar
import os
from tkinter import PhotoImage
import random
import textwrap

root = Tk()
root.wm_attributes("-topmost", 1)
# root.attributes('-alpha', 0.9)
assets_folder = "_internal/assets/assest"
# List all files in the "assets" folder
asset_files = os.listdir(assets_folder)
# Select a random file from the list
random_file = random.choice(asset_files)
# Create a PhotoImage with the random file
image = PhotoImage(file=os.path.join(assets_folder, random_file))

color = image.get(30, 285)
red, green, blue = color
hex_color = f'#{red:02X}{green:02X}{blue:02X}'


height = 396
width = 700
# image = image.subsample(int(image.width() / 530), int(image.height() /298))

x = (root.winfo_screenwidth()//2)-(width//2)
y = (root.winfo_screenheight()//2)-(height//2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
root.overrideredirect(True)

bg_lable = Label(root, image=image)
bg_lable.pack()

progress_label = Label(root, text="Loading...",font=("Trebuchet Ms", 5 ,"bold"), fg="#FFFFFF", bg=hex_color, wraplength=200, anchor="w", justify="left")
progress_label.place(x=20, y=280)
# progress_label.pack()

progress = ttk.Style()
progress.theme_use("clam")
progress.configure("red.Horizontal.TProgressbar",troughcolor=hex_color, bordercolor=hex_color, background="#FFFFFF", lightcolor="#FFFFFF", darkcolor=hex_color)

# TROUGH_COLOR = '#FFFFFF'
# BAR_COLOR = '#10BCFF'

progress = ttk.Progressbar(root, style="red.Horizontal.TProgressbar", length=660, mode='indeterminate')
progress.place(x=20, y=360)
# progress.pack(pady=0)


# Function to run the config_ui.py script
def run_config_ui():
    subprocess.run(["python", "main.py"])
    # subprocess.run(["_internal/main.exe"])
    
    
def top():
    root.withdraw()
    root.destroy()

i = 0
def load():
    global i
    if i <= 15:
        txt = 'Loading.' + '.'*(i%3)
        txt = textwrap.fill(txt, width=30)
        progress_label.config(text=txt)
        progress_label.after(600, load)
        progress.start()
        i += 1

    else:
        top()
        
config_ui_thread = threading.Thread(target=run_config_ui)
config_ui_thread.start()
load()

root.resizable(False, False)
root.mainloop()
