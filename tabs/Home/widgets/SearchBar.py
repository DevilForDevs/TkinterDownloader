import tkinter
import tkinter as tk
from tkinter import Button
from tkinter.constants import X, RIGHT


class SearchFrame(tk.Frame):

    def __init__(self, master=None, on_search=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_search = on_search

        Button(
            self,
            text="Go",
            command=self._handle_search
        ).pack(side=RIGHT, padx=20)

        self.entry = tkinter.Entry(self)

        self.entry.pack(
            fill=X,
            pady=5
        )

        self.entry.bind(
            "<Return>",
            self._handle_search_event
        )

    def _handle_search_event(self, event):
        self._handle_search()

    def _handle_search(self):

        text = self.entry.get().strip()

        if text and self.on_search:
            self.on_search(text)

        # Clear textbox
        self.entry.delete(0, tk.END)