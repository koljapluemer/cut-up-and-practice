import tkinter as tk
from tkinter import filedialog
import os
import random
from PIL import Image, ImageTk

class ImageSnippetApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Snippets App")
        self.master.geometry("400x300")

        self.start_frame = tk.Frame(self.master)
        self.start_frame.pack()

        self.main_frame = tk.Frame(self.master)

        self.label = tk.Label(self.start_frame, text="Welcome to Image Snippets App", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.options_menu = tk.Menu(self.master)
        self.master.config(menu=self.options_menu)

        self.file_menu = tk.Menu(self.options_menu, tearoff=False)
        self.options_menu.add_cascade(label="Options", menu=self.file_menu)
        self.file_menu.add_command(label="Open Image Snippets", command=self.open_images)
        self.file_menu.add_command(label="Load Example", command=self.load_example)

        self.start_button = tk.Button(self.start_frame, text="Start", command=self.start_main_screen)
        self.start_button.pack(pady=10)

        self.current_image = None
        self.image_index = 0
        self.image_list = []

    def start_main_screen(self):
        self.start_frame.pack_forget()
        self.main_frame.pack()

        self.show_next_image()

    def open_images(self):
        file_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        self.image_list = [Image.open(path) for path in file_paths]

    def load_example(self):
        example_folder = os.path.join("assets", "example", "song-1")
        file_paths = [os.path.join(example_folder, file) for file in os.listdir(example_folder)]
        self.image_list = [Image.open(path) for path in file_paths]

    def show_next_image(self):
        if self.current_image:
            self.current_image.pack_forget()

        if self.image_index < len(self.image_list):
            image = self.image_list[self.image_index]
            self.current_image = tk.Label(self.main_frame, image=self.convert_to_tkimage(image))
            self.current_image.pack(pady=20)

            self.image_index += 1
            self.master.after(300, self.show_next_image)
        else:
            self.back_to_start_screen()

    def back_to_start_screen(self):
        self.main_frame.pack_forget()
        self.image_index = 0
        self.start_frame.pack()

    def convert_to_tkimage(self, image):
        return ImageTk.PhotoImage(image)

def main():
    root = tk.Tk()
    app = ImageSnippetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
