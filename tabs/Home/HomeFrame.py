import os
import threading
import tkinter as tk
import urllib.request
from tkinter import X, BOTH
from typing import Optional, Callable

from tabs.Home.utils.searchEndpoint import send_youtube_search_request
from tabs.Home.widgets.SearchBar import SearchFrame
from tabs.Home.widgets.SearchItem import SearchItem
from tabs.Home.widgets.SyncedProgressBar import SyncedProgressBar
from tabs.commanWidgets.ScrollableFrame import ScrollableFrame


class HomeFrame(tk.Frame,):
    scrollFrame: Optional[ScrollableFrame] = None
    query = ""
    busy = False  # <-- New flag
    syncList=[]
    playHls=None
    appDestroyed: Optional[tk.BooleanVar] = None
    def __init__(self, master=None,collectedVideos: Optional[list] = None,playVideo: Optional[Callable]=None,
                 continuationvar: Optional[tk.StringVar] = None,appDestroyed:Optional[tk.BooleanVar]=None,**kwargs):
        super().__init__(master, **kwargs)
        SearchFrame(self, on_search=self.handleQuery).pack(fill=X, pady=5)

        self.progressFrame = tk.Frame(self, pady=5)
        self.progressFrame.pack(fill=X)
        self.resultsFor = tk.Label(self.progressFrame, anchor="w")
        self.progress_var = tk.IntVar()
        self.progressBar = SyncedProgressBar(self.progressFrame, progress_var=self.progress_var)
        self.scrollFrame = ScrollableFrame(self, on_scroll_end=self.reachedBottom)
        self.scrollFrame.pack(fill=BOTH, expand=True)

        self.playHls=playVideo
        self.appDestroyed = appDestroyed or tk.BooleanVar(master=self, value=False)
        self.syncList=collectedVideos
        self.continuationvar = continuationvar or tk.StringVar(master=self, value="")

        if collectedVideos:
            self.render_existing_videos(collectedVideos)

    def showProgres(self):
        self.progressBar.pack(fill=X, padx=10)
        self.progress_var.set(50)

    def hideProgress(self):
        if self.appDestroyed.get():
            return
        self.progressBar.pack_forget()

    def render_existing_videos(self,collectedVideos):
        dir_path = "thumbnail"
        os.makedirs(dir_path, exist_ok=True)

        for vid in collectedVideos:
            videoId = vid["videoId"]
            thumb_path = f"{dir_path}/{videoId}.jpg"

            if not os.path.exists(thumb_path):
                urllib.request.urlretrieve(
                    f"https://img.youtube.com/vi/{videoId}/hqdefault.jpg",
                    thumb_path
                )

            SearchItem(
                self.scrollFrame.scrollable_frame,
                bd=2, relief="groove",
                vid=videoId, title=vid["title"], duration=vid["duration"], formatSelect=self.askResolution,
                playhls=self.playHls
            ).pack(fill=X, pady=5)

    def reset_search(self):
        self.query = ""

        self.busy = False
        # clear old result widgets
        for child in self.scrollFrame.scrollable_frame.winfo_children():
            child.destroy()

        self.resultsFor.configure(text="")
    def handleQuery(self,query):
        if query != self.query:
            self.reset_search()

            self.query = query

        if self.busy:
            return

        self.busy = True
        self.showProgres()
        os.makedirs("thumbnail", exist_ok=True)

        def task():
            try:
                if self.appDestroyed.get():
                    return

                if "http" in query:
                    print("download")
                else:
                    results = send_youtube_search_request(
                        query, self.continuationvar.get(), "EgIQAQ%3D%3D"
                    )

                    if self.appDestroyed.get():
                        return

                    self.continuationvar.set(results["continuation"])

                    self.hideProgress()
                    self.resultsFor.pack(fill=X)
                    self.resultsFor.configure(text=query[0].upper() + query[1:])

                    videos = results["videos"]

                    for v in videos:
                        if self.appDestroyed.get():
                            return

                        if v["videoId"] not in [x["videoId"] for x in self.syncList]:
                            vid = v["videoId"]
                            self.syncList.append(v)

                            urllib.request.urlretrieve(
                                f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
                                f"thumbnail/{vid}.jpg"
                            )
                            SearchItem(
                                self.scrollFrame.scrollable_frame,
                                bd=2, relief="groove",
                                vid=vid,
                                title=v["title"],
                                duration=v["duration"],
                                formatSelect=self.askResolution,
                                playhls=self.playHls
                            ).pack(fill=X, pady=5)

            except Exception as e:
                self.hideProgress()
            finally:
                self.busy = False

        threading.Thread(target=task).start()


    def reachedBottom(self):
        print("reachedbottom")
    def askResolution(self):
        print("asking")
    def playHls(self):
        print("playing")

   