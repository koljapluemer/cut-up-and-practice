from tkinter import ttk 
from pony.orm import *
import tkinter as tk

import random

from PIL import Image, ImageTk
from tkinter import PhotoImage


class PracticeView(ttk.Frame):
    @db_session
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
    def load(self):
        self.load_snippets()
        self.load_random_snippet()
        self.render_current_snippet()

    @db_session
    def load_snippets(self):
        # get last created MusicPiece
        self.music_piece = select(m for m in self.db.MusicPiece).order_by(desc(self.db.MusicPiece.id)).first()
        # load all snippets of that MusicPiece
        self.snippets = select(s for s in self.db.Snippet if s.music_piece == self.music_piece)[:]
        # for every snippet, preload the SnippetImages
        for snippet in self.snippets:
            snippet.snippet_images
        print("loaded snippets", self.snippets)

    @db_session
    def load_random_snippet(self):
        if self.snippets:
            self.last_snippet = self.current_snippet
            self.last_snippet_name = self.current_snippet_name

            self.current_snippet = random.choice(self.snippets)
            self.clear_snippet_renderer()
            self.render_current_snippet()

            # in 5 s, render next snippet
            self.after(5000, self.load_random_snippet)

    @db_session
    def render_current_snippet(self, use_small_images=False):
        images = self.current_snippet.snippet_images
        for img_obj in images:
            image = Image.open(img_obj.path)
            if use_small_images:
                image.thumbnail((100, 100))
            tk_image = ImageTk.PhotoImage(image)
            label = ttk.Label(self.current_snippet_label, image=tk_image)
            label.image = tk_image
            # put in frame
            label.pack(side=tk.LEFT, expand=True, fill=tk.X)

    @db_session
    def clear_snippet_renderer(self):
        for widget in self.current_snippet_label.winfo_children():
            widget.destroy()
