from tkinter import ttk 
from pony.orm import *
import tkinter as tk

import random

from PIL import Image, ImageTk
from tkinter import PhotoImage

import ebisu
import datetime

class PracticeView(ttk.Frame):
    @db_session
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Practicing....").pack()
        ttk.Button(self, text="End Session", command=lambda: parent.go_to("start")).pack()

        self.db = parent.db
        self.load_snippets()

        parent.current_state = parent.states.CURRENT_MUSIC_PIECE_EXISTS

        self.current_snippet = None
        self.last_snippet = None
        self.snippets = []
        self.current_countdown = None

        # GUI Setup
        self.current_snippet_frame = None
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
            button = ttk.Button(self.difficulty_buttons_frame, text=level, command=lambda l=level: self.save_feedback(l, self.current_snippet))
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
            button = ttk.Button(self.main_footer_rating_buttons_frame, text=level, command=lambda l=level: self.save_feedback(l, self.last_snippet))
            button.pack(side=tk.LEFT)

        self.main_footer_rating_buttons_frame.pack(side=tk.BOTTOM)

        self.last_snippet_label = ttk.Frame(self.main_footer_rating_frame)
        self.last_snippet_label.pack()


    @db_session
    def load(self):
        self.cancel_countdown()
        self.load_snippets()
        self.load_next_snippet()

    @db_session
    def load_snippets(self):
        # get current music piece from global settings
        self.music_piece = self.db.GlobalSettings.get().current_music_piece
        # load all snippets of that MusicPiece
        self.snippets = select(s for s in self.db.Snippet if s.music_piece == self.music_piece)[:]
        # for every snippet, preload the SnippetImages
        for snippet in self.snippets:
            snippet.snippet_images


    @db_session
    def load_next_snippet(self):
        # run get_predicted_recall for all snippets
        # lowest predicted recall is below 0.6, load that snippet!!
        # otherwise, load a snippet where predicted recall is Null (never shown before)
        # if all snippets have predicted recall above 60%, load a random snippet:
        lowest_predicted_recall = 1
        chosen_snippet = None
        unseen_snippets = []

        for snippet in self.snippets:
            if snippet.get_predicted_recall() < lowest_predicted_recall:
                # if snippet has prerequisits (because made from more than 1 img), check that they all have predicted recall that exists and is over 0.6
                disqualified_by_prerequisites = False
                if len(snippet.snippet_images) > 1:
                    for prereq in snippet.prerequisite_snippets:
                        if prereq.get_predicted_recall() is None or prereq.get_predicted_recall() < 0.6:
                            disqualified_by_prerequisites = True
                            break
                if not disqualified_by_prerequisites:
                    # also exclude if same as last snippet
                    if snippet != self.last_snippet:
                        lowest_predicted_recall = snippet.get_predicted_recall()
                        chosen_snippet = snippet

        # render last snippet
        self.clear_snippet_renderer()
        if self.last_snippet:
            self.render_snippet(self.last_snippet_label, self.last_snippet, use_small_images=True)

        self.last_snippet = self.current_snippet
        self.current_snippet = chosen_snippet
        self.render_snippet(self.current_snippet_label, self.current_snippet)

        interval = self.db.GlobalSettings.get().interval
        self.current_countdown = self.after(interval * 1000, self.load_next_snippet)


    @db_session
    def render_snippet(self, target, snippet, use_small_images=False):
        images = snippet.snippet_images
        for img_obj in images:
            image = Image.open(img_obj.path)
            if use_small_images:
                image.thumbnail((100, 100))
            tk_image = ImageTk.PhotoImage(image)
            label = ttk.Label(target, image=tk_image)
            label.image = tk_image
            # put in frame
            label.pack(side=tk.LEFT, expand=True, fill=tk.X)

    @db_session
    def clear_snippet_renderer(self):
        for widget in self.current_snippet_label.winfo_children():
            widget.destroy()
        for widget in self.last_snippet_label.winfo_children():
            widget.destroy()

    @db_session
    def save_feedback(self, difficulty, snippet):
        # create SnippetLog
        self.db.SnippetLog(snippet=snippet, difficulty=self.codified_difficulty_levels_dict[difficulty], log_type="feedback")

        a = snippet.alpha
        b = snippet.beta
        t = snippet.t
        max_score = 4
        score = self.codified_difficulty_levels_dict[difficulty]
        time_elapsed = datetime.datetime.now() - snippet.last_seen
        time_elapsed_in_seconds = time_elapsed.total_seconds()
        prior_model = (a, b, t)
        snippet.alpha, snippet.beta, snippet.t = ebisu.updateRecall(prior_model, score, max_score, time_elapsed_in_seconds)
        # if "Very Easy", go to next snippet and cancel countdown
        if difficulty == "Very Easy":
            self.cancel_countdown()
            self.load_next_snippet()

    def cancel_countdown(self):
        if self.current_countdown:
            self.after_cancel(self.current_countdown)
            self.current_countdown = None