import threading
import tkinter as tk
from tkinter import Label, X, BOTH
from typing import Optional, Callable

from tabs.Player.utils.createresolutionlist import get_videos_by_codec
from tabs.Player.utils.get_audio_by_itag import get_audio_by_itag
from tabs.Player.utils.streamingInfoFetcher import (
    get_visitor_id, android_player_response
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
                self._ui(lambda: self.videoTitle.set("Fetching streaming data..."))

                retries = 3
                resolutions = []

                for attempt in range(retries):

                    player_response = android_player_response(
                        video_id=videoId
                    )
                    self._ui(lambda: self.videoTitle.set("Parsing streaming data..."))

                    streaming_data = player_response["playerResponse"]["streamingData"]

                    mp4Resolutions = get_videos_by_codec(
                        streaming_data["adaptiveFormats"],
                        ["avc1"],
                        fallback_codecs=["vp9"]
                    )

                    # Retry if empty
                    if not mp4Resolutions:
                        print(f"No video formats found. Retry {attempt + 1}/{retries}")
                        continue

                    audio140 = get_audio_by_itag(
                        streaming_data["adaptiveFormats"],
                        140,
                        251
                    )

                    for res in mp4Resolutions:
                        resolutions.append(
                            {
                                "height": res["height"],
                                "video": res["url"],
                                "selected": False,
                                "audio": audio140["url"]
                            }
                        )
                    self._ui(lambda: self.videoTitle.set(txt2filename(player_response["playerResponse"]["videoDetails"]["title"])))

                    break  # stop retry loop if successful

                if not resolutions:
                    self._ui(lambda: self.videoTitle.set("No playable formats found"))
                    raise Exception("No playable video formats found")

                if resolutions:
                    if len(resolutions) >= 3:
                        resolutions[2]["selected"] = True
                    else:
                        resolutions[-1]["selected"] = True

                self.player.play(resolutions)



            except Exception as e:
                if is_outdated():
                    return

                self._ui(lambda: self.videoTitle.set(f"Error: {str(e)}"))
                print("Player thread error:", e)

        threading.Thread(target=backThread, daemon=True).start()