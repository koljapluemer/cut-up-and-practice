from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
import tkinter as tk

from views.start_view import StartView
from views.practice_view import PracticeView
from views.load_view import LoadView

import time, datetime

from pony.orm import *

import ebisu
import datetime

from enum import Enum

import os

import sv_ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.states = Enum("States", ["NO_CURRENT_MUSIC_PIECE",  "CURRENT_MUSIC_PIECE_EXISTS"])
        self.current_state = self.states.NO_CURRENT_MUSIC_PIECE

        self.title("Cut up and practice")
        self.geometry("15000x800")

        # init database
        self.db = Database()
        self.db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
        self.define_entities(self.db)

        self.check_state_and_settings()

        # init views
        self.views = {
            "start": StartView(self),
            "practice": PracticeView(self),
            "load": LoadView(self),
        }

        self.current_view = None
        self.go_to("start")

        self.run()

    @db_session
    def check_state_and_settings(self):
        # make GlobalSettings a cheap singleton: if there is no object, create one
        if len(self.db.GlobalSettings.select()) == 0:
            self.db.GlobalSettings(interval=45)
        # if we have last_folder set and the folder exist, set state to last song exists
        settings = self.db.GlobalSettings.get()
        if settings.current_music_piece:
            self.current_state = self.states.CURRENT_MUSIC_PIECE_EXISTS
        
    @db_session
    def run(self):
        sv_ttk.set_theme("light")
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
    
            useless_setting_prop = Optional("GlobalSettings")


        class Snippet(db.Entity):
            music_piece = Required(MusicPiece)
            snippet_name = Required(str)
            snippet_images = Set("SnippetImage")
            logs = Set("SnippetLog")
            # ebisu
            alpha = Optional(float)
            beta = Optional(float)
            t = Optional(float)
            last_seen = Optional(datetime.datetime)

            prerequisite_snippets = Set("Snippet", reverse="prerequisite_snippets")

            def get_predicted_recall(self):
                if self.alpha is None or self.beta is None or self.t is None:
                    return None
                else:
                    prior_model = (self.alpha, self.beta, self.t)
                    time_elapsed = datetime.datetime.now() - self.last_seen
                    time_elapsed_in_seconds = time_elapsed.total_seconds()
                    return ebisu.predictRecall(prior_model, time_elapsed_in_seconds, exact=True)


        class SnippetImage(db.Entity):
            path = Required(str)
            snippet = Set(Snippet)

        class SnippetLog(db.Entity):
            snippet = Required(Snippet)
            timestamp = Required(datetime.datetime, default=datetime.datetime.now)
            log_type = Required(str)
            difficulty = Optional(int)

        class GlobalSettings(db.Entity):
            current_music_piece = Optional("MusicPiece")
            interval = Required(int)
        
        db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    app = App()

