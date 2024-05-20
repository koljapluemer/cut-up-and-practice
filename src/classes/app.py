from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
import tkinter as tk

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.title("Cut up and practice")
        self.geometry("700x500")
        # self.create_widgets()


        ttk.Button(self, text="Quit", command=self.destroy).pack()


        self.mainloop()