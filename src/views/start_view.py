from tkinter import ttk 
from pony.orm import *

class StartView(ttk.Frame):
    @db_session
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Welcome to Cut Up and Practice").pack(padx=5, pady=5)
        self.db = parent.db
        self.parent = parent

    @db_session
    def save_settings(self):
        settings = self.db.GlobalSettings.get()
        settings.interval = int(self.interval_entry.get())
        commit()
    
    def load(self):
        # delete all widgets
        for widget in self.winfo_children():
            widget.destroy()
        # only if state.CURRENT_MUSIC_PIECE_EXISTS
        if self.parent.current_state == self.parent.states.CURRENT_MUSIC_PIECE_EXISTS:
            # add margin
            ttk.Button(self, text="Continue Last Session", command=lambda: self.parent.go_to("practice")).pack(padx=5, pady=5)

        btn_new = ttk.Button(self, text="Practice New Music Piece", command=lambda: self.parent.go_to("load")).pack(padx=5, pady=5)
        ttk.Separator(self, orient="horizontal").pack(fill="x")
        # make button for every music piece in the database
        if self.parent.current_state == self.parent.states.CURRENT_MUSIC_PIECE_EXISTS:

            ttk.Label(self, text="Continue with a previous piece:").pack(padx=5, pady=5)
            for music_piece in self.parent.db.MusicPiece.select():
                id = music_piece.id
                ttk.Button(self, text=music_piece.title, command=lambda: self.go_to_practice_of_piece(id)).pack(padx=5, pady=5)

            ttk.Separator(self, orient="horizontal").pack(fill="x")
        # Settings Section (for now, only the interval setting from GlobalSettings)
        ttk.Label(self, text="Settings:").pack(padx=5, pady=5)
        settings = self.db.GlobalSettings.get()
        # allow changing the interval!!!! xD
        self.interval_label = ttk.Label(self, text=f"Interval for each snippet:")
        self.interval_label.pack(padx=5, pady=5)
        self.interval_entry = ttk.Entry(self)
        self.interval_entry.insert(0, settings.interval)
        self.interval_entry.pack(padx=5, pady=5)
        ttk.Button(self, text="Save Settings", command=self.save_settings).pack(padx=5, pady=5)

    @db_session
    def go_to_practice_of_piece(self, music_piece_id):
        music_piece = self.db.MusicPiece[music_piece_id]
        # set db settings current_music_piece
        settings = self.db.GlobalSettings.get()
        settings.current_music_piece = music_piece
        self.parent.go_to("practice")