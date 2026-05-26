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
    busy = False
    videoId = ""
    visitorData = ""
    clientVersion = ""
    loadingSuggestions=False

    def __init__(
        self,
        master=None,
        fullScreenCallBack: Optional[Callable] = None,
        visitorId: Optional[tk.StringVar] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.continuationToken = tk.StringVar(value="")
        self.keep_widgets = set()
        self.visitorId = visitorId
        self._request_id = 0
        self._lock = threading.Lock()

        # ---------------- UI ROOT ----------------
        self.scroll = ScrollableFrame(self, on_scroll_end=self.reachedBottom)
        self.scroll.pack(fill=BOTH, expand=True)

        self.container = self.scroll.scrollable_frame

        # Title
        self.videoTitle = tk.StringVar(value="")
        self.titleLabel = Label(
            self.container,
            textvariable=self.videoTitle,
            anchor="w"
        )
        self.titleLabel.pack(fill=X, padx=10, pady=5)
        self.keep_widgets.add(self.titleLabel)

        # Player
        self.player = VideoPlayer(
            self.container,
            fullScreenCallBack,
            height=650
        )
        self.player.pack(fill=X, padx=10, pady=5)
        self.player.pack_propagate(False)
        self.player.configure(height=650)
        self.keep_widgets.add(self.player)

    # ---------------- SAFE UI ----------------
    def _ui(self, fn):
        self.after(0, fn)

    # ---------------- MAIN PLAY ----------------
    def playYtVideo(self, videoId: str):
        self.videoId = videoId

        for child in self.container.winfo_children():
            if child not in self.keep_widgets:
                try:
                    child.destroy()
                except:
                    pass

        self.player.toggle_play()

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
                    print(f"Try {i}")
                    self.busy = True
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
                self.busy = False

                self.loadSuggestions(videoId, req_id)

            except Exception as e:
                if not outdated():
                    self._ui(lambda: self.videoTitle.set(f"Error: {e}"))
                print("Error:", e)

        threading.Thread(target=worker, daemon=True).start()

    # ---------------- SUGGESTIONS ----------------
    def loadSuggestions(self, videoId: str, req_id: int):

        def outdated():
            return req_id != self._request_id

        def worker():
            try:
                if not self.visitorData:
                    visitor_data, client_version, _ = get_web_visitor_and_client_from_html()
                    self.visitorData = visitor_data      # ← was never stored before
                    self.clientVersion = client_version

                if outdated():
                    return
                self.loadingSuggestions=True

                result = get_suggestions(
                    video_id=videoId,
                    continuation=None,
                    visitor_data=self.visitorData,
                    client_version=self.clientVersion
                )

                if outdated():
                    return

                parsed = parse_watch_json(result, "watchInitial")
                self.continuationToken.set(parsed["continuation"])

                os.makedirs("thumbnail", exist_ok=True)

                for vid in parsed["videos"]:
                    if vid["title"]=="shorts":
                        continue
                    if vid["playlistId"] is not None:
                        continue
                    if outdated() or self.busy:
                        break

                    vid_id = vid["videoId"]
                    thumb = f"thumbnail/{vid_id}.jpg"

                    if not os.path.exists(thumb):
                        try:
                            urllib.request.urlretrieve(
                                f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                                thumb
                            )
                        except Exception as e:
                            print("Thumbnail skip:", vid_id)

                    if outdated():
                        break

                    self._ui(lambda v=vid: self._addSuggestion(v))

                self.loadingSuggestions = False
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
        if self.loadingSuggestions:
            return
        if self.busy:
            return
        if self.continuationToken.get() == "":
            return

        with self._lock:
            req_id = self._request_id

        def outdated():
            return req_id != self._request_id

        def worker():
            try:
                if outdated():
                    return
                # currently this block causing removal of player and title
                # self.loadingSuggestions=True
                # result = get_suggestions(
                #     video_id=self.videoId,
                #     continuation=self.continuationToken.get(),
                #     visitor_data=self.visitorData,
                #     client_version=self.clientVersion
                # )
                #
                # if outdated():
                #     return
                #
                # parsed = parse_watch_json(result, "watchContinuation")
                # if parsed["continuation"] is not None:
                #     self.continuationToken.set(parsed["continuation"])
                #
                # os.makedirs("thumbnail", exist_ok=True)
                #
                # for vid in parsed["videos"]:
                #     if vid["title"]=="shorts":
                #         continue
                #     if vid["playlistId"] is not None:
                #         continue
                #     if outdated() or self.busy:
                #         return
                #
                #     vid_id = vid["videoId"]
                #     thumb = f"thumbnail/{vid_id}.jpg"
                #     if not os.path.exists(thumb):
                #         urllib.request.urlretrieve(
                #             f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                #             thumb
                #         )
                #
                #     if outdated():
                #         return
                #
                #     self._ui(lambda v=vid: self._addSuggestion(v))
                # self.loadingSuggestions=False
            except Exception as e:
                print("Suggestion error:", e)

        threading.Thread(target=worker, daemon=True).start()
        print("scroll bottom reached")

    def askResolution(self):
        print("download purpose")

    def playHls(self, videoId):
        self.playYtVideo(videoId)