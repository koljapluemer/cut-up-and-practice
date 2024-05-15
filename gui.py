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

        self.current_snippet_frame = tk.Frame(self.main_frame)
        self.current_snippet_frame.pack(pady=20)

        self.current_snippet_label = tk.Label(self.current_snippet_frame)
        self.current_snippet_label.pack()

        self.difficulty_buttons_frame = tk.Frame(self.main_frame)
        self.difficulty_buttons_frame.pack()

        self.difficulty_levels = ["Very Hard", "Hard", "Medium", "Easy", "Very Easy"]
        self.difficulty_buttons = []
        for level in self.difficulty_levels:
            button = tk.Button(self.difficulty_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l))
            button.pack(side=tk.LEFT, padx=5)

        self.current_image_frame = None
        self.current_snippet_name = None
        self.image_list = []
        self.snippets = []
        

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
        self.start_frame.pack_forget()
        self.main_frame.pack()

        self.load_next_snippet()

    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder", initialdir=self.last_folder_path)
        if folder_path:
            self.image_list = self.load_images_from_folder(folder_path)
            if self.image_list:
                self.last_folder_path = folder_path
                self.save_last_folder_path(self.last_folder_path)
                self.open_session_settings()

    def load_last_snippet_collection(self):
        if self.last_folder_path:
            self.image_list = self.load_images_from_folder(self.last_folder_path)
            if self.image_list:
                self.open_session_settings()

    def load_example(self):
        example_folder = os.path.join("assets", "example", "song-1")
        self.image_list = self.load_images_from_folder(example_folder)
        if self.image_list:
            self.open_session_settings()

    def load_images_from_folder(self, folder_path):
        image_list = []
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(filepath)
                image_list.append(image)
        return image_list

    def load_next_snippet(self):
        if self.snippets:
            if not self.current_image_frame:
                self.current_image_frame = tk.Frame(self.main_frame)
                self.current_image_frame.pack()
            random_snippet = random.choice(self.snippets)
            # Clear existing images before displaying new ones
            self.clear_current_image_frame()
            self.display_snippet_images(random_snippet)
            self.master.after(self.next_snippet_duration * 1000, self.load_next_snippet)
            # save current snippet name: all image names, made filename safe, connected by —
            self.current_snippet_name = '—'.join([f'\'{image.filename.split("/")[-1]}\'' for image in random_snippet])
        else:
            logging.warning('No snippets available.')


    def clear_current_image_frame(self):
        # Check if current_image_frame exists and contains widgets
        if self.current_image_frame and self.current_image_frame.winfo_children():
            # Destroy all child widgets in current_image_frame
            for widget in self.current_image_frame.winfo_children():
                widget.destroy()


    def display_snippet_images(self, snippet):
        for image_path in snippet:

            tk_image = self.convert_to_tkimage(image_path)
            label = tk.Label(self.current_image_frame, image=tk_image)
            label.image = tk_image
            # put in frame
            label.pack(side=tk.LEFT, padx=5)
                

    def set_difficulty(self, level):
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

            image_feedback = next((item for item in data if self.current_snippet_name in item), None)
            if image_feedback is not None:
                image_feedback[self.current_snippet_name].append(feedback_data)
            else:
                image_feedback = {self.current_snippet_name: [feedback_data]}
                data.append(image_feedback)

            with open(json_path, "w") as file:
                json.dump(data, file)

    # Sessions Settings Screen
    def open_session_settings(self):
        # Forget any existing frames to ensure only settings frame is visible
        self.start_frame.pack_forget()
        self.main_frame.pack_forget()

        # Create the settings frame
        self.settings_frame = tk.Frame(self.master)
        self.settings_frame.pack()

        # Add widgets for session settings
        duration_label = tk.Label(self.settings_frame, text="Duration each snippet is shown (seconds):")
        duration_label.pack(pady=5)

        self.next_snippet_duration = tk.IntVar()
        self.next_snippet_duration.set(5)
        duration_entry = tk.Entry(self.settings_frame, textvariable=self.next_snippet_duration)
        duration_entry.pack(pady=5)

        # checkbox to set whether snippet combinations should be generated
        self.should_generate_combinations = tk.BooleanVar()
        self.should_generate_combinations.set(True)
        generate_combinations_checkbox = tk.Checkbutton(self.settings_frame, text="Generate snippet combinations", variable=self.should_generate_combinations)
        generate_combinations_checkbox.pack(pady=5)

        back_button = tk.Button(self.settings_frame, text="Start", command=self.save_settings_and_redirect)
        back_button.pack(pady=10)

    def save_settings_and_redirect(self):
        # delete the settings frame
        self.settings_frame.pack_forget()
        self.next_snippet_duration = self.next_snippet_duration.get()
        # if generate_combinations is checked, generate combinations
        if self.should_generate_combinations.get():
            self.generate_combinations(3)
        else:
            self.generate_combinations()


        self.start_main_screen()

    def generate_combinations(self, depth=0):
        # wrap each element of the image list in a list
        self.snippets = [[image] for image in self.image_list]
        if depth > 0:
            # generate pairs, in order
            # e.g. if we have snippets: 1.png, 2.png, 3.png
            # ...generate 1-2, 2-3, 3-1 and no more
            for i in range(len(self.image_list)):
                self.snippets.append([self.image_list[i], self.image_list[(i+1) % len(self.image_list)]])
            # append the last snippet
            self.snippets.append([self.image_list[-1], self.image_list[0]])


def main():
    root = tk.Tk()
    app = ImageSnippetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()


