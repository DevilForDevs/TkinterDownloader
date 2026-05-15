import os
import shutil
import tkinter as tk
from tkinter.constants import RIGHT, BOTH, Y

from tabs.Home.HomeFrame import HomeFrame
from tabs.Player.PlayerFrame import PlayerFrame
from widgets.SidebarFrame import SidebarFrame


class DownloaderApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("TkinterDownloader")
        self.continuationToken = tk.StringVar()
        self.collectedVideos = []
        # container for all pages
        self.body_container = tk.Frame(self,bg="red")
        self.body_container.pack(
            side=RIGHT,
            fill=BOTH,
            expand=True,

        )
        self.appDestroyed = tk.BooleanVar()
        self.appDestroyed.set(False)

        # store frames (important improvement)
        self.frames = {}
        self.current_frame = None

        # sidebar with real navigation
        self.sidebar = SidebarFrame(
            self,
            home_cmd=lambda: self.switch("home"),
            downloads_cmd=lambda: self.switch("downloads"),
            player_cmd=lambda: self.switch("player"),
        )

        self.sidebar.pack(
            side="left",
            fill=Y,
            padx=10,
            pady=10
        )

        # create placeholder frames (replace later with real ones)
        self.frames["home"] = HomeFrame(self.body_container,self.collectedVideos,
                                        continuationvar=self.continuationToken,playVideo=self.playVideo,
                                        appDestroyed=self.appDestroyed)
        self.frames["downloads"] = tk.Frame(self.body_container, bg="gray")
        self.frames["player"] = PlayerFrame(self.body_container,fullScreenCallBack=self.toggleFullScreen)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        if os.path.exists("thumbnail"):
            shutil.rmtree("thumbnail")


        # default screen
        self.switch("home")

    def toggleFullScreen(self):

        is_fullscreen = self.attributes("-fullscreen")

        self.attributes(
            "-fullscreen",
            not is_fullscreen
        )

        if not is_fullscreen:

            # hide sidebar
            self.sidebar.pack_forget()

        else:

            # show sidebar
            self.sidebar.pack(
                side="left",
                fill=Y,
                padx=10,
                pady=10
            )



    def switch(self, name: str):

        if self.current_frame:
            self.current_frame.pack_forget()

        frame = self.frames.get(name)
        if frame is None:
            return

        self.current_frame = frame
        self.current_frame.pack(
            fill=BOTH,
            expand=True,
        )
    def playVideo(self,videoId):
        self.switch("player")
        frame = self.frames.get("player")
        frame.playYtVideo(videoId)


    def on_close(self):
        self.appDestroyed.set(True)
        self.destroy()  # actually close the window



if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()