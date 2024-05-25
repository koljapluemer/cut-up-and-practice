from tkinter import ttk 

class StartView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Welcome to Cut Up and Practice").pack()

        # only if state.CURRENT_MUSIC_PIECE_EXISTS
        if parent.current_state == parent.states.CURRENT_MUSIC_PIECE_EXISTS:
            ttk.Button(self, text="Continue Last Session", command=lambda: parent.go_to("ready")).pack()

        btn_new = ttk.Button(self, text="Practice New Music Piece", command=lambda: parent.go_to("load")).pack()
    
    
    def load(self):
        pass