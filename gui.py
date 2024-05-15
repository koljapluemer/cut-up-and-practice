import tkinter as tk
from tkinter import filedialog
import os
import random
from PIL import Image, ImageTk

import logging

class ImageSnippetApp:
    def __init__(self, master):
        logging.basicConfig(level=logging.INFO)
        logging.info('Init')
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

        self.open_folder_button = tk.Button(self.start_frame, text="Open Folder", command=self.open_folder)
        self.open_folder_button.pack(pady=10)

        self.load_example_button = tk.Button(self.start_frame, text="Load Example", command=self.load_example)
        self.load_example_button.pack(pady=10)

        self.current_image = None
        self.image_index = 0
        self.image_list = []

    def start_main_screen(self):
        logging.info('Starting Main Loop')
        self.start_frame.pack_forget()
        self.main_frame.pack()

        self.show_next_image()

    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            logging.info(f'Selected folder: {folder_path}')
            self.image_list = self.load_images_from_folder(folder_path)
            logging.info(f'Loaded {len(self.image_list)} images')
            if self.image_list:
                self.start_main_screen()

    def load_example(self):
        example_folder = os.path.join("assets", "example", "song-1")
        self.image_list = self.load_images_from_folder(example_folder)
        if self.image_list:
            self.start_main_screen()

    def load_images_from_folder(self, folder_path):
        image_list = []
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(filepath)
                image_list.append(image)
        return image_list

    def show_next_image(self):
        if self.current_image:
            self.current_image.pack_forget()

        if self.image_index < len(self.image_list):
            logging.info(f'Showing image {self.image_index + 1}')
            image = self.image_list[self.image_index]
            tk_image = self.convert_to_tkimage(image)
            self.current_image = tk.Label(self.main_frame, image=tk_image)
            self.current_image.image = tk_image  # Store a reference to the image
            logging.info(f'Image size: {image.size}')
            self.current_image.pack(pady=20)

            self.image_index += 1
            self.master.after(30000, self.show_next_image)
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
