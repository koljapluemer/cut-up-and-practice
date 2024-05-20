from tkinter import ttk 
from pony.orm import *
import tkinter as tk


class PracticeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Practicing....").pack()
        ttk.Button(self, text="End Session", command=lambda: parent.go_to("start")).pack()

        self.db = parent.db
        self.load_snippets()


        # GUI Setup
        self.current_snippet = None
        self.current_snippet_frame = None
        self.current_snippet_name = None

        self.last_snippet = None
        self.last_snippet_name = None

        self.image_list = []
        self.snippets = []

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=5)
        self.main_frame.rowconfigure(1, weight=1)

        self.main_practice_frame = ttk.Frame(self.main_frame )
        self.main_practice_frame.grid(row=0, column=0, sticky="ewns")

        self.main_heading = ttk.Label(self.main_practice_frame, text="Practice:")
        self.main_heading.pack()

        self.current_snippet_frame = ttk.Frame(self.main_practice_frame)
        self.current_snippet_frame.pack(fill=tk.BOTH, expand=True)

        self.current_snippet_label = ttk.Label(self.current_snippet_frame)
        self.current_snippet_label.pack()

        self.difficulty_buttons_frame = ttk.Frame(self.main_practice_frame)
        self.difficulty_buttons_frame.pack()

        self.difficulty_levels = ["Very Hard", "Hard", "Medium", "Easy", "Very Easy"]
        self.codified_difficulty_levels_dict = {level: i for i, level in enumerate(self.difficulty_levels)}
        self.codified_difficulty_levels_dict["Just Displayed"] = -1
        self.difficulty_buttons = []
        for level in self.difficulty_levels:
            button = ttk.Button(self.difficulty_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l, self.current_snippet_name))
            button.pack(side=tk.LEFT, padx=5)

        # Footer 

        self.main_footer_frame = ttk.Frame(self.main_frame)
        self.main_footer_frame.grid(row=1, column=0, sticky="nsew")

        self.main_footer_buttons_frame = ttk.Frame(self.main_footer_frame, borderwidth=2, relief="groove" )
        self.main_footer_buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.back_button = ttk.Button(self.main_footer_buttons_frame, text="End Session", command=lambda: parent.go_to("start"))
        self.back_button.pack( expand=True, fill=tk.X)

        self.main_footer_rating_frame = ttk.Frame(self.main_footer_frame, borderwidth=2, relief="groove" )
        self.main_footer_rating_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.main_footer_rating_label = ttk.Label(self.main_footer_rating_frame, text="Rate the difficulty of the last snippet:")
        self.main_footer_rating_label.pack()

        self.main_footer_rating_buttons_frame = ttk.Frame(self.main_footer_rating_frame)

        for level in self.difficulty_levels:
            button = ttk.Button(self.main_footer_rating_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l, self.last_snippet_name))
            button.pack(side=tk.LEFT)

        self.main_footer_rating_buttons_frame.pack(side=tk.BOTTOM)

        self.main_footer_rating_frame = ttk.Frame(self.main_footer_rating_frame)
        self.main_footer_rating_frame.pack()

    @db_session
    def load_snippets(self):
        # get all snippets
        self.snippets = select(s for s in self.db.SnippetImage)[:]