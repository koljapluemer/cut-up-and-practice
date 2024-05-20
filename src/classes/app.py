from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
import tkinter as tk

from .views.start_view import StartView
from .views.ready_view import ReadyView
from .views.practice_view import PracticeView
from .views.stats_view import StatsView
from .views.load_view import LoadView

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Cut up and practice")
        self.geometry("700x500")

        # init views

        self.views = {
            "start": StartView(self),
            "ready": ReadyView(self),
            "practice": PracticeView(self),
            "stats": StatsView(self),
            "load": LoadView(self),
        }

        self.current_view = None
        self.go_to("start")

        self.mainloop()

    def go_to(self, target):
        print(f"Going to {target}")
        # hide current view
        if self.current_view:
            self.current_view.pack_forget()
        
        # show target view
        self.current_view = self.views[target]
        self.current_view.pack(fill=tk.BOTH, expand=True)
        