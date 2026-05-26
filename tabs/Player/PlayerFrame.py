import os
import threading
import tkinter as tk
import urllib.request
from tkinter import Label, X, BOTH
from typing import Optional, Callable

from tabs.Home.widgets.SearchItem import SearchItem
from tabs.Player.utils.WatchNextBrowse import get_suggestions
from tabs.Player.utils.createresolutionlist import get_videos_by_codec
from tabs.Player.utils.get_audio_by_itag import get_audio_by_itag
from tabs.Player.utils.parseWatchJson import parse_watch_json
from tabs.Player.utils.streamingInfoFetcher import android_player_response
from tabs.Player.utils.webClientInfo import get_web_visitor_and_client_from_html
from tabs.Player.widgets.VideoPlayer import VideoPlayer
from tabs.commanWidgets.ScrollableFrame import ScrollableFrame
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

        self.fullscreen_mode = False
        self.suggestions_frame = None
        
        self.visitorId = visitorId
        self._request_id = 0
        self._lock = threading.Lock()

        # ---------------- UI ROOT ----------------
        self.scroll = ScrollableFrame(self, on_scroll_end=self.reachedBottom)
        self.scroll.pack(fill=BOTH, expand=True)

        self.container = self.scroll.scrollable_frame

        # Title
        self.videoTitle = tk.StringVar(value="")
        Label(
            self.container,
            textvariable=self.videoTitle,
            anchor="w"
        ).pack(fill=X, padx=10, pady=5)

        # Player
        self.player = VideoPlayer(
            self.container,
            fullScreenCallBack,
            height=650
        )
        self.player.pack(fill=X, padx=10, pady=5)
        self.player.pack_propagate(False)
        self.player.configure(height=650)

    # ---------------- SAFE UI ----------------
    def _ui(self, fn):
        self.after(0, fn)

    # ---------------- MAIN PLAY ----------------
    def playYtVideo(self, videoId: str):

        with self._lock:
            self._request_id += 1
            req_id = self._request_id

        def outdated():
            return req_id != self._request_id

        def worker():
            try:
                self._ui(lambda: self.videoTitle.set("Loading..."))

                resolutions = []
                retries = 3

                for i in range(retries):

                    player = android_player_response(videoId)
                    streaming = player["playerResponse"]["streamingData"]

                    self._ui(lambda: self.videoTitle.set("Processing streams..."))

                    mp4 = get_videos_by_codec(
                        streaming["adaptiveFormats"],
                        ["avc1"],
                        fallback_codecs=["vp9"]
                    )

                    if not mp4:
                        continue

                    audio = get_audio_by_itag(
                        streaming["adaptiveFormats"],
                        140,
                        251
                    )

                    for r in mp4:
                        resolutions.append({
                            "height": r["height"],
                            "video": r["url"],
                            "audio": audio["url"],
                            "selected": False
                        })

                    title = player["playerResponse"]["videoDetails"]["title"]
                    self._ui(lambda: self.videoTitle.set(txt2filename(title)))

                    break

                if outdated():
                    return

                if not resolutions:
                    self._ui(lambda: self.videoTitle.set("No playable formats"))
                    return

                if len(resolutions) >= 3:
                    resolutions[2]["selected"] = True
                else:
                    resolutions[-1]["selected"] = True

                self.player.play(resolutions)

                self.loadSuggestions(videoId)

            except Exception as e:
                if not outdated():
                    self._ui(lambda: self.videoTitle.set(f"Error: {e}"))
                print("Error:", e)

        threading.Thread(target=worker, daemon=True).start()

    # ---------------- SUGGESTIONS ----------------
    def loadSuggestions(self, videoId: str):

        def worker():
            try:
                self._ui(lambda: self.videoTitle.set("Loading suggestions..."))

                visitor_id, client_version, _ = get_web_visitor_and_client_from_html()

                result = get_suggestions(
                    video_id=videoId,
                    continuation=None,
                    visitor_data=visitor_id,
                    client_version=client_version
                )

                parsed = parse_watch_json(result, "watchInitial")

                os.makedirs("thumbnail", exist_ok=True)

                for vid in parsed["videos"]:
                    vid_id = vid["videoId"]
                    thumb = f"thumbnail/{vid_id}.jpg"

                    if not os.path.exists(thumb):
                        urllib.request.urlretrieve(
                            f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                            thumb
                        )

                    self._ui(lambda v=vid: self._addSuggestion(v))

                self._ui(lambda: self.videoTitle.set(""))

            except Exception as e:
                print("Suggestion error:", e)

        threading.Thread(target=worker, daemon=True).start()

    # ---------------- UI ADD ITEM ----------------
    def _addSuggestion(self, vid):
        SearchItem(
            self.container,
            bd=2,
            relief="groove",
            vid=vid["videoId"],
            title=vid["title"],
            duration=vid.get("duration"),
            formatSelect=self.askResolution,
            playhls=self.playHls
        ).pack(fill=X, pady=5)

    # ---------------- EVENTS ----------------
    def reachedBottom(self):
        print("scroll bottom reached")

    def askResolution(self):
        print("download purpose")

    def playHls(self, videoId):
        self.playYtVideo(videoId)