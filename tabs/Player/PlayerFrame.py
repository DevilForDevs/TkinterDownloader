import threading
import tkinter as tk
from tkinter import Label, X, BOTH
from typing import Optional, Callable

from tabs.Player.utils.hlseditro import create_resolution_playlists_py
from tabs.Player.utils.streamingInfoFetcher import get_ios_player_response
from tabs.Player.widgets.VideoPlayer import VideoPlayer
from tabs.utils.Filenameutils import txt2filename


class PlayerFrame(tk.Frame,):


    def __init__(
            self,
            master=None,
            fullScreenCallBack: Optional[Callable] = None,
            **kwargs
    ):
        super().__init__(master, **kwargs)
        self.videoTitle = tk.StringVar()

        Label(
            self,
            textvariable=self.videoTitle,
            anchor="w"
        ).pack(fill=X, padx=10, pady=5)

        self.player = VideoPlayer(self,fullScreenCallBack)

        self.player.pack(
            fill=BOTH,
            expand=True,
            padx=10,
            pady=5
        )

    def playYtVideo(self, videoId):
        def backThread():
            player_response = get_ios_player_response(videoId)

            if "streamingData" not in player_response:
                self.after(
                    0,
                    lambda: self.videoTitle.set(
                        "Streaming Data Not Found"
                    )
                )

                return

            print(player_response["streamingData"])
            hls_url = (
                player_response["streamingData"]
                ["hlsManifestUrl"]
            )
            if hls_url is None:
                self.after(
                    0,
                    lambda: self.videoTitle.set("Hls Url Missing")
                )


            video_filename = txt2filename(
                player_response["videoDetails"]["title"]
            )
            print(player_response["videoDetails"]["title"])
            print(video_filename)

            self.after(
                0,
                lambda: self.videoTitle.set(video_filename)
            )

            resolutions = create_resolution_playlists_py(
                hls_url,
                video_id=videoId,
                files_dir="tempFiles"
            )

            playlist_path = (
                f"tempFiles/{videoId}"
                f"({resolutions[0]}).m3u8"
            )

            self.after(
                0,
                lambda: self.player.set_video_id(
                    videoId,
                    resolutions
                )
            )

            self.after(
                0,
                lambda: self.player.play(
                    playlist_path
                )
            )

        threading.Thread(
            target=backThread,
            daemon=True
        ).start()








