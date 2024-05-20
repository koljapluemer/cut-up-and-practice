from tkinter import ttk 

class ReadyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Ready to start?").pack()
        ttk.Button(self, text="Start Session", command=lambda: parent.go_to("practice")).pack()
