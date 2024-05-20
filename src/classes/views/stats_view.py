from tkinter import ttk 

class StatsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Your Statistics").pack()
        ttk.Button(self, text="Back To Start", command=lambda: parent.go_to("start")).pack()
