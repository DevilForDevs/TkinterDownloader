import platform
import tkinter as tk
from tkinter import ttk
import vlc

from tabs.Player.widgets.seekbar import CircleSeekbar


class VideoPlayer(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg="black", **kwargs)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.current_file = None
        self.current_video_id = None

        self.is_playing = False
        self.duration = 0
        self.updating_seekbar = False

        # Stores:
        # {
        #   "480x854": "tempFiles/abc(480x854).m3u8"
        # }
        self.available_resolutions = {}

        # Create video display frame
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(side="top", fill="both", expand=True)

        # Controls frame
        self.controls_frame = tk.Frame(self, bg="black")
        self.controls_frame.pack(side="bottom", fill="x")

        self._build_ui()

        self.after(500, self._update)

    def _embed_vlc_video(self):
        self.update_idletasks()

        win_id = self.video_frame.winfo_id()
        system = platform.system()

        if system == "Windows":
            self.player.set_hwnd(win_id)

        elif system == "Linux":
            self.player.set_xwindow(win_id)

        elif system == "Darwin":
            self.player.set_nsobject(win_id)

    def _build_ui(self):
        bottom = self.controls_frame
        bottom.configure(padx=10, pady=10)

        self.selectFileButton = ttk.Button(
            bottom,
            text="Resolution",
            command=self.show_resolution_menu
        )
        self.selectFileButton.pack(side="left", padx=(0, 15))

        self.play_btn = tk.Button(
            bottom,
            text="▶",
            command=self.toggle_play
        )
        self.play_btn.pack(side="left", padx=(0, 15))

        self.seekbar = CircleSeekbar(
            bottom,
            width=300,
            height=30,
            max_value=100,
            command=self._on_seek
        )

        self.seekbar.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 15)
        )

        self.duration_label = tk.Label(
            bottom,
            text="00:00 / 00:00",
            fg="white",
            bg="black",
            font=("Arial", 10)
        )

        self.duration_label.pack(side="right")

    # =========================
    # RESOLUTION LOGIC
    # =========================

    def set_video_id(self, video_id, resolutions):
        self.current_video_id = video_id
        self.available_resolutions.clear()

        for res in resolutions:
            path = f"tempFiles/{video_id}({res}).m3u8"
            self.available_resolutions[str(res)] = path

    def show_resolution_menu(self):

        if not self.available_resolutions:
            return

        menu = tk.Menu(self, tearoff=0)

        sorted_res = sorted(
            self.available_resolutions.keys(),
            key=lambda x: int(x.split("x")[0])
        )

        for resolution in sorted_res:

            menu.add_command(
                label=resolution,
                command=lambda r=resolution: self.switch_resolution(r)
            )

        x = self.selectFileButton.winfo_rootx()
        y = self.selectFileButton.winfo_rooty() + self.selectFileButton.winfo_height()

        menu.tk_popup(x, y)

    def switch_resolution(self, resolution):

        if resolution not in self.available_resolutions:
            return

        current_time = self.player.get_time()

        path = self.available_resolutions[resolution]

        media = self.instance.media_new(path)

        self.player.set_media(media)

        self._embed_vlc_video()

        self.player.play()

        # restore playback position
        def restore():
            self.player.set_time(current_time)

        self.after(1200, restore)

        self.is_playing = True
        self.play_btn.config(text="⏸")

    # =========================
    # PLAYBACK
    # =========================

    def play(self, path_or_url):
        self.current_file = path_or_url

        media = self.instance.media_new(path_or_url)

        self.player.set_media(media)

        self._embed_vlc_video()

        self.player.play()

        self.is_playing = True

        self.play_btn.config(text="⏸")

    def toggle_play(self):

        if self.is_playing:

            self.player.pause()

            self.is_playing = False

            self.play_btn.config(text="▶")

        else:

            self.player.play()

            self.is_playing = True

            self.play_btn.config(text="⏸")

    def _on_seek(self, value):

        if self.duration > 0:

            self.player.set_time(
                int(
                    (value / self.seekbar.max_value)
                    * self.duration
                    * 1000
                )
            )

    def _update(self):

        length_ms = self.player.get_length()

        if length_ms > 0:

            self.duration = length_ms / 1000

            self.seekbar.set_max(self.duration)

        current_time = (
            self.player.get_time() / 1000
            if self.player else 0
        )

        if self.duration > 0:

            self.updating_seekbar = True

            self.seekbar.set_value(current_time)

            self.updating_seekbar = False

        self.duration_label.config(
            text=f"{self._format_time(current_time)} / {self._format_time(self.duration)}"
        )

        self.after(500, self._update)

    def _format_time(self, seconds):

        if seconds is None or seconds < 0:
            return "00:00"

        m, s = divmod(int(seconds), 60)

        return f"{m:02}:{s:02}"