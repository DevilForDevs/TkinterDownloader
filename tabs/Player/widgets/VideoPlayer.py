import platform
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict

import vlc

from tabs.Player.widgets.seekbar import CircleSeekbar


class VideoPlayer(tk.Frame):
    """
    A Tkinter-based video player widget using VLC with custom seekbar
    and resolution switching.
    """
    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        fullScreenCallBack: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, bg="black", **kwargs)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Callback and state variables
        self.fullScreenIcon = tk.StringVar(value="<")
        self.fullScreenAction = fullScreenCallBack
        self.is_playing = False
        self.duration = 0.0  # seconds (float)
        self.updating_seekbar = False
        self.resolutions: List[Dict] = []

        # UI Elements
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(side="top", fill="both", expand=True)

        self.controls_frame = tk.Frame(self, bg="black")
        self.controls_frame.pack(side="bottom", fill="x")

        self._build_ui()
        self.after(500, self._update)

    def _embed_vlc_video(self):
        """Embeds the VLC video output inside the Tk frame."""
        self.update_idletasks()
        win_id = self.video_frame.winfo_id()
        system = platform.system()
        if system == "Windows":
            self.player.set_hwnd(win_id)
        elif system == "Linux":
            self.player.set_xwindow(win_id)
        elif system == "Darwin":
            self.player.set_nsobject(win_id)

    def toggleFullScreen(self):
        """Toggles fullscreen icon and calls the provided callback."""
        self.fullScreenIcon.set(">" if self.fullScreenIcon.get() == "<" else "<")
        if self.fullScreenAction:
            self.fullScreenAction()

    def _build_ui(self):
        """Initializes all UI controls."""
        bottom = self.controls_frame
        bottom.configure(padx=10, pady=10)

        self.fullScreenBtn = ttk.Button(
            bottom,
            textvariable=self.fullScreenIcon,
            width=2,
            command=self.toggleFullScreen
        )
        self.fullScreenBtn.pack(side="left", padx=(0, 5))

        self.selectFileButton = ttk.Button(
            bottom,
            text="Resolution",
            command=self.showResolutions
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
        self.seekbar.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.duration_label = tk.Label(
            bottom,
            text="00:00 / 00:00",
            fg="white",
            bg="black",
            font=("Arial", 10)
        )
        self.duration_label.pack(side="right")

    def showResolutions(self):
        """Shows a popup menu with available resolutions."""
        if not self.resolutions:
            return

        menu = tk.Menu(self, tearoff=0)

        for index, r in enumerate(self.resolutions):
            label = str(r.get("height", f"Option {index + 1}"))
            if r.get("selected"):
                label += " ✓"
            menu.add_command(
                label=label,
                command=lambda i=index: self.switchResolution(i)
            )

        x = self.selectFileButton.winfo_rootx()
        y = self.selectFileButton.winfo_rooty() + self.selectFileButton.winfo_height()
        menu.tk_popup(x, y)

    def switchResolution(self, index: int):
        """Switch to another resolution and restore playback position."""
        current_time = self.player.get_time()

        # Unselect all and select chosen resolution
        for r in self.resolutions:
            r["selected"] = False
        self.resolutions[index]["selected"] = True
        selected = self.resolutions[index]

        # Create and set new media
        media = self.instance.media_new(selected["video"])
        if selected.get("audio"):
            media.add_option(f':input-slave={selected["audio"]}')
        self.player.set_media(media)
        self._embed_vlc_video()
        self.player.play()
        self.is_playing = True
        self.play_btn.config(text="⏸")

        # Robustly restore playback position
        if current_time > 0:
            self._restore_playback_position(current_time)

    def _restore_playback_position(self, ts_ms: int):
        """
        Waits for player to be in playing or paused state,
        then restores time in milliseconds.
        """
        def poll_and_seek():
            state = self.player.get_state()
            if state in (vlc.State.Playing, vlc.State.Paused):
                self.player.set_time(ts_ms)
            else:
                self.after(100, poll_and_seek)
        poll_and_seek()

    def play(self, resolutions: Optional[list] = None):
        """Loads the given resolutions list and starts playback at the selected resolution."""
        if not resolutions:
            return
        self.resolutions = resolutions

        for r in self.resolutions:
            if r.get("selected"):
                media = self.instance.media_new(r["video"])
                if r.get("audio"):
                    media.add_option(f':input-slave={r["audio"]}')
                self.player.set_media(media)
                self._embed_vlc_video()
                self.player.play()
                self.is_playing = True
                self.play_btn.config(text="⏸")
                break  # Only play first selected

    def toggle_play(self):
        """Toggles between play and pause."""
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.play_btn.config(text="▶")
        else:
            self.player.play()
            self.is_playing = True
            self.play_btn.config(text="⏸")

    def _on_seek(self, value: float):
        """Seeks the player to the position corresponding to value."""
        if self.duration > 0:
            self.player.set_time(
                int((value / self.seekbar.max_value) * self.duration * 1000)
            )

    def _update(self):
        """Updates seekbar and duration label."""
        length_ms = self.player.get_length()
        if length_ms > 0:
            self.duration = length_ms / 1000  # seconds
            self.seekbar.set_max(self.duration)

        current_time = self.player.get_time() / 1000 if self.player else 0

        if self.duration > 0:
            # Prevent feedback loop during seek
            self.updating_seekbar = True
            self.seekbar.set_value(current_time)
            self.updating_seekbar = False

        self.duration_label.config(
            text=f"{self._format_time(current_time)} / {self._format_time(self.duration)}"
        )
        self.after(500, self._update)

    @staticmethod
    def _format_time(seconds: Optional[float]) -> str:
        """Formats time in seconds to MM:SS."""
        if seconds is None or seconds < 0:
            return "00:00"
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"