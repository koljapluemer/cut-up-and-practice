from tkinter import ttk 

class PracticeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Practicing....").pack()
        ttk.Button(self, text="End Session", command=lambda: parent.go_to("start")).pack()
