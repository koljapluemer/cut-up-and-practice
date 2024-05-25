from tkinter import ttk 
from pony.orm import *

class StartView(ttk.Frame):
    @db_session
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Welcome to Cut Up and Practice").pack()
        self.db = parent.db
        self.parent = parent

        # only if state.CURRENT_MUSIC_PIECE_EXISTS
        if parent.current_state == parent.states.CURRENT_MUSIC_PIECE_EXISTS:
            ttk.Button(self, text="Continue Last Session", command=lambda: parent.go_to("practice")).pack()

        btn_new = ttk.Button(self, text="Practice New Music Piece", command=lambda: parent.go_to("load")).pack()
        ttk.Separator(self, orient="horizontal").pack(fill="x")
        # make button for every music piece in the database
        ttk.Label(self, text="Continue with a previous piece:").pack()
        for music_piece in parent.db.MusicPiece.select():
            id = music_piece.id
            ttk.Button(self, text=music_piece.title, command=lambda: self.go_to_practice_of_piece(id)).pack()
    
    
    def load(self):
        pass

    @db_session
    def go_to_practice_of_piece(self, music_piece_id):
        music_piece = self.db.MusicPiece[music_piece_id]
        # set db settings current_music_piece
        settings = self.db.GlobalSettings.get()
        settings.current_music_piece = music_piece
        self.parent.go_to("practice")