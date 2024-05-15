import tkinter as tk
from tkinter import filedialog
import os
import random
import json
from PIL import Image, ImageTk
import re
from datetime import datetime

import logging

class ImageSnippetApp:
    def __init__(self, master):
        logging.basicConfig(level=logging.INFO)
        logging.info('Init')
        self.master = master
        self.master.title("Image Snippets App")
        self.master.geometry("1000x800")

        self.start_frame = tk.Frame(self.master)
        self.start_frame.pack()

        self.main_frame = tk.Frame(self.master)

        self.label = tk.Label(self.start_frame, text="Welcome to Image Snippets App", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.options_menu = tk.Menu(self.master)
        self.master.config(menu=self.options_menu)

        self.load_last_button = tk.Button(self.start_frame, text="Load Last Snippet Collection", command=self.load_last_snippet_collection)
        self.load_last_button.pack(pady=10)

        self.open_folder_button = tk.Button(self.start_frame, text="Open Folder", command=self.open_folder)
        self.open_folder_button.pack(pady=10)

        self.load_example_button = tk.Button(self.start_frame, text="Load Example", command=self.load_example)
        self.load_example_button.pack(pady=10)

        self.current_image_frame = tk.Frame(self.main_frame)
        self.current_image_frame.pack(pady=20)

        self.current_image_label = tk.Label(self.current_image_frame)
        self.current_image_label.pack()

        self.difficulty_buttons_frame = tk.Frame(self.main_frame)
        self.difficulty_buttons_frame.pack()

        self.difficulty_levels = ["Very Hard", "Hard", "Medium", "Easy", "Very Easy"]
        self.difficulty_buttons = []
        for level in self.difficulty_levels:
            button = tk.Button(self.difficulty_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l))
            button.pack(side=tk.LEFT, padx=5)

        self.current_image = None
        self.current_image_name = None
        self.image_list = []
        

        self.last_folder_path = None
        self.load_last_folder_path()

    def load_last_folder_path(self):
        try:
            with open("last_folder.json", "r") as file:
                data = json.load(file)
                self.last_folder_path = data.get("last_folder_path")
        except FileNotFoundError:
            pass

    def save_last_folder_path(self, folder_path):
        data = {"last_folder_path": folder_path}
        with open("last_folder.json", "w") as file:
            json.dump(data, file)

    def start_main_screen(self):
        logging.info('Starting Main Loop')
        self.start_frame.pack_forget()
        self.main_frame.pack()

        self.show_next_image()

    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder", initialdir=self.last_folder_path)
        if folder_path:
            self.image_list = self.load_images_from_folder(folder_path)
            if self.image_list:
                self.last_folder_path = folder_path
                self.save_last_folder_path(self.last_folder_path)
                self.start_main_screen()

    def load_last_snippet_collection(self):
        if self.last_folder_path:
            self.image_list = self.load_images_from_folder(self.last_folder_path)
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

        if self.image_list:
            logging.info('Showing next random image')
            image = random.choice(self.image_list)
            self.current_image_name = os.path.basename(image.filename)
            tk_image = self.convert_to_tkimage(image)
            self.current_image = tk.Label(self.main_frame, image=tk_image)
            self.current_image.image = tk_image  # Store a reference to the image
            logging.info(f'Image size: {image.size}')
            self.current_image.pack(pady=20)


            self.master.after(30000, self.show_next_image)
        else:
            logging.warning('No image to display.')
            

    def set_difficulty(self, level):
        logging.info(f'Setting difficulty level to: {level}')
        self.store_feedback(level)

    def convert_to_tkimage(self, image):
        return ImageTk.PhotoImage(image)


    def store_feedback(self, difficulty_level):
        if self.last_folder_path:
            folder_name = os.path.basename(self.last_folder_path)
            safe_folder_name = re.sub(r'[^\w\s-]', '', folder_name)
            json_filename = f"{safe_folder_name}.json"
            json_path = os.path.join("feedback", json_filename)

            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "difficulty_level": difficulty_level
            }

            if not os.path.exists("feedback"):
                os.makedirs("feedback")

            if os.path.exists(json_path):
                with open(json_path, "r") as file:
                    data = json.load(file)
            else:
                data = []

            image_feedback = next((item for item in data if self.current_image_name in item), None)
            if image_feedback is not None:
                image_feedback[self.current_image_name].append(feedback_data)
            else:
                image_feedback = {self.current_image_name: [feedback_data]}
                data.append(image_feedback)

            with open(json_path, "w") as file:
                json.dump(data, file)

def main():
    root = tk.Tk()
    app = ImageSnippetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
