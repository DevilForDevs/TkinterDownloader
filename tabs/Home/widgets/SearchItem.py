import os
import tkinter
import tkinter as tk
from tkinter import Label, Button
from tkinter.constants import X, RIGHT, LEFT

from PIL import Image, ImageTk


class SearchItem(tk.Frame):

    def __init__(self, master=None, vid=None, title=None, duration=None,
                 formatSelect=None, playhls=None, **kwargs):
        super().__init__(master, **kwargs)

        dir_path = "thumbnail"
        self.formatSelected = formatSelect

        os.makedirs(dir_path, exist_ok=True)

        thumbnail_img = Image.open(f"{dir_path}/{vid}.jpg")
        thumbnail_img = thumbnail_img.resize((100, 100))
        thumbnail_photo = ImageTk.PhotoImage(thumbnail_img)

        thumbnail = tk.Label(self, image=thumbnail_photo) if thumbnail_photo else tk.Label(
            self, text="No Image", width=15
        )

        if thumbnail_photo:
            thumbnail.image = thumbnail_photo

        thumbnail.pack(side=RIGHT)

        # Title section
        info = tk.Frame(self)
        Label(info, text=title, anchor="w").pack(fill=X, pady=5)
        info.pack(fill=X, padx=10)

        # Sub info section (reordered)
        subINfo = tk.Frame(self)

        def playHlsVideo():
            playhls(vid)

        # ---- Row 1: main actions ----
        actions = tk.Frame(subINfo)

        play_btn = Button(actions, text="Play", width=20, command=playHlsVideo)
        copy_btn = Button(actions, text="Copy Link", width=20)

        play_btn.pack(side=LEFT, padx=5)
        copy_btn.pack(side=LEFT, padx=5)

        actions.pack(fill=X)

        # ---- Row 2: info + download ----
        bottom = tk.Frame(subINfo)

        duration_lbl = Label(bottom, text=duration,width=19)

        download_btn = Button(
            bottom,
            text="Download Mp4",
            width=20,
            command=lambda: self.formatSelected(vid, "video/mp4")
        )

        duration_lbl.pack(side=LEFT, padx=10)
        download_btn.pack(side=LEFT, padx=5)

        bottom.pack(fill=X, pady=5)

        subINfo.pack(fill=X, pady=10, padx=10)















