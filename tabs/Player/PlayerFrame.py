import threading
import tkinter as tk
from tkinter import Label, X, BOTH
from typing import Optional, Callable

from tabs.Player.utils.hlseditro import create_resolution_playlists_py
from tabs.Player.utils.streamingInfoFetcher import (
    get_ios_player_response,
    get_visitor_id
)
from tabs.Player.widgets.VideoPlayer import VideoPlayer
from tabs.utils.Filenameutils import txt2filename


class PlayerFrame(tk.Frame):

    def __init__(
            self,
            master=None,
            fullScreenCallBack: Optional[Callable] = None,
            visitorId: Optional[tk.StringVar] = None,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.videoTitle = tk.StringVar(value="")

        self.visitorId = visitorId

        Label(
            self,
            textvariable=self.videoTitle,
            anchor="w"
        ).pack(fill=X, padx=10, pady=5)

        self.player = VideoPlayer(
            self,
            fullScreenCallBack
        )

        self.player.pack(
            fill=BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        # Used to cancel outdated threads
        self._request_id = 0

        # Prevent simultaneous loads
        self._lock = threading.Lock()

    def _ui(self, func):
        """
        Safely execute UI updates on main thread
        """
        self.after(0, func)

    def playYtVideo(self, videoId):

        with self._lock:
            self._request_id += 1
            current_request = self._request_id

        self._ui(
            lambda: self.videoTitle.set("Loading...")
        )

        def is_outdated():
            return current_request != self._request_id

        def backThread():

            try:

                # NEVER access tkinter variables directly in worker thread
                visitor_id = self.visitorId.get()

                if visitor_id == "":
                    visitor_id = get_visitor_id()

                    if is_outdated():
                        return

                    self._ui(
                        lambda: self.visitorId.set(visitor_id)
                    )

                player_response = get_ios_player_response(
                    videoId,
                    visitor_id
                )

                if is_outdated():
                    return

                streaming_data = player_response.get("streamingData")

                if not streaming_data:
                    self._ui(
                        lambda: self.videoTitle.set(
                            "Streaming Data Not Found"
                        )
                    )
                    return

                hls_url = streaming_data.get("hlsManifestUrl")

                if not hls_url:
                    self._ui(
                        lambda: self.videoTitle.set(
                            "HLS URL Missing"
                        )
                    )
                    return

                title = (
                    player_response
                    .get("videoDetails", {})
                    .get("title", "Unknown Video")
                )

                video_filename = txt2filename(title)

                self._ui(
                    lambda: self.videoTitle.set(video_filename)
                )

                resolutions = create_resolution_playlists_py(
                    hls_url,
                    video_id=videoId,
                    files_dir="tempFiles"
                )

                if is_outdated():
                    return

                if not resolutions:
                    self._ui(
                        lambda: self.videoTitle.set(
                            "No Resolutions Found"
                        )
                    )
                    return

                playlist_path = (
                    f"tempFiles/{videoId}"
                    f"({resolutions[0]}).m3u8"
                )

                self._ui(
                    lambda: self.player.set_video_id(
                        videoId,
                        resolutions
                    )
                )

                self._ui(
                    lambda: self.player.play(
                        playlist_path
                    )
                )

            except Exception as e:

                if is_outdated():
                    return

                self._ui(
                    lambda: self.videoTitle.set(
                        f"Error: {str(e)}"
                    )
                )

                print("Player thread error:", e)

        threading.Thread(
            target=backThread,
            daemon=True
        ).start()