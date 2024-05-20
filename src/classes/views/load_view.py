from tkinter import ttk 

class LoadView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Load Snippets From a Folder on Your Device").pack()
        ttk.Button(self, text="Select Folder", command=self.destroy).pack()

        # back
        ttk.Button(self, text="Back To Start", command=lambda: parent.go_to("start")).pack()
