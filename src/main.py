from tkinter import ttk  # Normal Tkinter.* widgets are not themed!
from ttkthemes import ThemedTk
import tkinter as tk

from classes.app import App


# window = ThemedTk(theme="arc")
# ttk.Button(window, text="Quit", command=window.destroy).pack()
# window.mainloop()

def main():
    app = App()


if __name__ == "__main__":
    main()