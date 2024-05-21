from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
import tkinter as tk

from .views.start_view import StartView
from .views.ready_view import ReadyView
from .views.practice_view import PracticeView
from .views.stats_view import StatsView
from .views.load_view import LoadView

import time, datetime

from pony.orm import *

import ebisu
import datetime

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Cut up and practice")
        self.geometry("15000x800")

        # init database
        self.db = Database()
        self.db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
        self.define_entities(self.db)

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

        self.run()
        
    @db_session
    def run(self):
        self.mainloop()

    @db_session
    def go_to(self, target):
        # hide current view
        if self.current_view:
            self.current_view.pack_forget()
        
        # show target view
        self.current_view = self.views[target]
        self.current_view.load()
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def define_entities(self, db):
        class MusicPiece(db.Entity):
            title = Required(str)
            folder_path = Required(str)
            snippets = Set("Snippet")

        class Snippet(db.Entity):
            music_piece = Required(MusicPiece)
            snippet_name = Required(str)
            snippet_images = Set("SnippetImage")
            logs = Set("SnippetLog")
            # ebisu
            alpha = Optional(float)
            beta = Optional(float)
            t = Optional(int)

            def get_predicted_recall(self):
                if self.alpha is None or self.beta is None or self.t is None:
                    return None
                else:
                    return ebisu.predictRecall(self.alpha, self.beta, self.t, datetime.datetime.now().timestamp())


        class SnippetImage(db.Entity):
            path = Required(str)
            snippet = Set(Snippet)

        class SnippetLog(db.Entity):
            snippet = Required(Snippet)
            timestamp = Required(datetime.datetime, default=datetime.datetime.now)
            log_type = Required(str)
            difficulty = Optional(int)
        
        db.generate_mapping(create_tables=True)