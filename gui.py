import tkinter as tk
from tkinter import PhotoImage
from tkinter import filedialog
import os
import random
import json
from PIL import Image, ImageTk
import re
from datetime import datetime

import logging

INTRODUCTION_RATE = 10

class ImageSnippetApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cut Up Your Music!")
        self.master.geometry("1000x800")

        self.start_frame = tk.Frame(self.master)

        self.label = tk.Label(self.start_frame, text="Let's Cut Up Some Music", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.options_menu = tk.Menu(self.master)
        self.master.config(menu=self.options_menu)

        self.start_menu_frame = tk.Frame(self.start_frame, borderwidth=2, relief="groove", padx=10, pady=10)
        self.start_menu_frame.pack()

        self.start_menu_label = tk.Label(self.start_menu_frame, text="Practice Mode:")
        self.start_menu_label.pack()

        self.last_folder_path = None
        self.load_last_folder_path()

        self.load_last_button = tk.Button(self.start_menu_frame, text="Continue Last Practice", command=self.load_last_snippet_collection, bg="#c0dbf1")

        self.open_folder_button = tk.Button(self.start_menu_frame, text="Load Snippets from Local Folder", command=self.open_folder)
        self.open_folder_button.pack(pady=5, expand=True, fill=tk.X)

        # Main Screen Setup

        self.current_snippet = None
        self.current_snippet_frame = None
        self.current_snippet_name = None

        self.last_snippet = None
        self.last_snippet_name = None

        self.image_list = []
        self.snippets = []

        self.main_frame = tk.Frame(self.master, padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=5)
        self.main_frame.rowconfigure(1, weight=1)

        self.main_practice_frame = tk.Frame(self.main_frame, bg="white", borderwidth=2, relief="groove", padx=10, pady=10)
        self.main_practice_frame.grid(row=0, column=0, sticky="ewns")

        self.main_heading = tk.Label(self.main_practice_frame, text="Practice:", font=("Helvetica", 28), bg="white")
        self.main_heading.pack(pady=10)

        self.current_snippet_frame = tk.Frame(self.main_practice_frame, bg="white")
        self.current_snippet_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.current_snippet_label = tk.Label(self.current_snippet_frame, bg="white")
        self.current_snippet_label.pack()

        self.difficulty_buttons_frame = tk.Frame(self.main_practice_frame, bg="white")
        self.difficulty_buttons_frame.pack(pady=10)

        self.difficulty_levels = ["Very Hard", "Hard", "Medium", "Easy", "Very Easy"]
        self.codified_difficulty_levels_dict = {level: i for i, level in enumerate(self.difficulty_levels)}
        self.codified_difficulty_levels_dict["Just Displayed"] = -1
        self.difficulty_buttons = []
        for level in self.difficulty_levels:
            button = tk.Button(self.difficulty_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l, self.current_snippet_name), font=("Helvetica", 12), height="2", bg="#c0dbf1")
            button.pack(side=tk.LEFT, padx=5)

        # Main Screen Footer 

        # give it quite a bit of top margin
        self.main_footer_frame = tk.Frame(self.main_frame)
        self.main_footer_frame.grid(row=1, column=0, sticky="nsew")

        self.main_footer_buttons_frame = tk.Frame(self.main_footer_frame, borderwidth=2, relief="groove", padx=10, pady=10)
        self.main_footer_buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.back_button = tk.Button(self.main_footer_buttons_frame, text="End Session", command=self.start_start_screen)
        self.back_button.pack(padx=5, expand=True, fill=tk.X)

        self.main_footer_rating_frame = tk.Frame(self.main_footer_frame, borderwidth=2, relief="groove", padx=10, pady=10)
        self.main_footer_rating_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.main_footer_rating_label = tk.Label(self.main_footer_rating_frame, text="Rate the difficulty of the last snippet:")
        self.main_footer_rating_label.pack()

        self.main_footer_rating_buttons_frame = tk.Frame(self.main_footer_rating_frame)

        for level in self.difficulty_levels:
            button = tk.Button(self.main_footer_rating_buttons_frame, text=level, command=lambda l=level: self.set_difficulty(l, self.last_snippet_name))
            button.pack(side=tk.LEFT, padx=5)

        self.main_footer_rating_buttons_frame.pack(pady=10, side=tk.BOTTOM)

        self.main_footer_rating_frame = tk.Frame(self.main_footer_rating_frame)
        self.main_footer_rating_frame.pack()

        self.start_start_screen()



 
    def load_last_folder_path(self):
        try:
            with open("last_folder.json", "r") as file:
                data = json.load(file)
                self.last_folder_path = data.get("last_folder_path")
        except FileNotFoundError:
            pass

    def save_last_folder_path(self, folder_path):
        self.last_folder_path = folder_path
        data = {"last_folder_path": folder_path}
        with open("last_folder.json", "w") as file:
            json.dump(data, file)

    def start_main_screen(self):
        self.start_frame.pack_forget()
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.load_next_snippet()

    def start_start_screen(self):
        self.main_frame.pack_forget()
        self.start_frame.pack()
        if self.last_folder_path:
            self.load_last_button.pack(pady=5, expand=True, fill=tk.X, side=tk.TOP)
        

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

    def load_images_from_folder(self, folder_path):
        image_list = []
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_list.append(filepath)
        return image_list

    def load_next_snippet(self):
        # if we have a current snippet, clone it to the bottom section (main_footer_rating_frame)
        if self.current_snippet:
            self.clear_frame(self.main_footer_rating_frame)
            self.display_snippet_images(self.current_snippet, self.main_footer_rating_frame, True)

        if self.snippets:
            # load the feedback file
            # check if the feedback file exists
            snippets_to_choose_from = []
            if self.last_folder_path:
                folder_name = os.path.basename(self.last_folder_path)
                safe_folder_name = re.sub(r'[^\w\s-]', '', folder_name)
                json_filename = f"{safe_folder_name}.json"
                json_path = os.path.join("feedback", json_filename)
                if os.path.exists(json_path):
                    with open(json_path, "r") as file:
                        data = json.load(file)
                    # for each snippet, get the average difficulty level (ignore -1 values)
                    # and sort the snippets by difficulty
                    snippet_difficulty = {}
                    for snippet in self.snippets:
                        name = self.name_from_snippet(snippet)
                        snippet_difficulty[name] = self.get_trailing_difficulty(name)

                    # add the 3 snippets with the lowest difficulty to the snippets_to_choose_from list:
                    # sort by difficulty, take the first 3
                    snippet_names_to_choose_from = sorted(snippet_difficulty, key=snippet_difficulty.get)[:3]
                    # loop snippets to get matching name
                    for snippet in self.snippets:
                        snippet_name = self.name_from_snippet(snippet)
                        if snippet_name in snippet_names_to_choose_from:
                            snippets_to_choose_from.append(snippet)

            # append the rest of the snippets to the end of snippets_to_choose_from
            rest_of_snippets_shuffled = self.snippets.copy()
            random.shuffle(rest_of_snippets_shuffled)
            snippets_to_choose_from += rest_of_snippets_shuffled

            self.last_snippet = self.current_snippet
            self.last_snippet_name = self.current_snippet_name
            # find random new one out of the first 5 snippets_to_choose_from
            found_snippet_not_equivalent_to_last = False
            found_snippet_not_blocked_by_children = False
            while not found_snippet_not_equivalent_to_last or not found_snippet_not_blocked_by_children:
                random_index = random.randint(0, min(INTRODUCTION_RATE - 1 + 3, len(snippets_to_choose_from) - 1))
                random_snippet = snippets_to_choose_from[random_index]
                if random_snippet != self.last_snippet:
                    found_snippet_not_equivalent_to_last = True
                # if it's a compound snippet ("—" in name), check if all children have difficulty > 2.5
                if "—" in self.name_from_snippet(random_snippet):
                    found_snippet_not_blocked_by_children = True
                    for child_name in self.name_from_snippet(random_snippet).split("—"):
                        difficulty = self.get_trailing_difficulty(child_name)
                        if difficulty < 2.5:
                            found_snippet_not_blocked_by_children = False
                            break
                else:
                    found_snippet_not_blocked_by_children = True
            self.clear_frame(self.current_snippet_frame)
            self.display_snippet_images(random_snippet, self.current_snippet_frame)
            self.master.after(self.next_snippet_duration * 1000, self.load_next_snippet)
            self.current_snippet_name = self.name_from_snippet(random_snippet)
            self.current_snippet = random_snippet
            # store feedback level with difficulty -1 
            # so we now that this snippet showed up
            self.store_feedback("Just Displayed", self.current_snippet_name)
        else:
            # if it's not a compound, it cannot be blocked, and we still have to escape the while loop
            logging.warning('No snippets available.')

    def get_trailing_difficulty(self, snippet_name):
        # we want the average difficulty of the last 10 ratings
        # if there are less than 10 ratings, we want the average of all ratings

        if self.last_folder_path:
            folder_name = os.path.basename(self.last_folder_path)
            safe_folder_name = re.sub(r'[^\w\s-]', '', folder_name)
            json_filename = f"{safe_folder_name}.json"
            json_path = os.path.join("feedback", json_filename)

            if os.path.exists(json_path):
                with open(json_path, "r") as file:
                    data = json.load(file)
                image_feedback = next((item for item in data if snippet_name in item), None)
                if image_feedback is not None:
                    # get the last 10 feedbacks
                    feedbacks = image_feedback[snippet_name][-10:]
                    # get the average of the feedbacks
                    # note that difficulty_property may be missing or none, so check for that
                    feedbacks = [feedback.get("difficulty_level") for feedback in feedbacks]
                    feedbacks = [feedback for feedback in feedbacks if feedback is not None]
                    # ignore -1 values
                    feedbacks = [feedback for feedback in feedbacks if feedback != -1]
                    feedback = sum(feedbacks) / len(feedbacks) if len(feedbacks) > 0 else 2
                    return feedback
        return 2

    def clear_frame(self, frame):
        # Check if current_snippet_frame exists and contains widgets
        if frame:
            # Destroy all child widgets in current_snippet_frame
            for widget in frame.winfo_children():
                widget.destroy()


    def display_snippet_images(self, snippet, target, use_small_images=False):
        for image_path in snippet:
            image = Image.open(image_path)
            if use_small_images:
                image.thumbnail((100, 100))
            tk_image = ImageTk.PhotoImage(image)
            label = tk.Label(target, image=tk_image, bg="white", borderwidth=2, relief="ridge", padx=5, pady=5)
            label.image = tk_image
            # put in frame
            label.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
                

    def set_difficulty(self, level, snippet_name):
        self.store_feedback(level, snippet_name)


    def store_feedback(self, difficulty_level, snippet_name):
        if self.last_folder_path:
            folder_name = os.path.basename(self.last_folder_path)
            safe_folder_name = re.sub(r'[^\w\s-]', '', folder_name)
            json_filename = f"{safe_folder_name}.json"
            json_path = os.path.join("feedback", json_filename)

            feedback_data = {
                "timestamp": datetime.now().isoformat(),
                "difficulty_level": self.codified_difficulty_levels_dict[difficulty_level]
            }

            if not os.path.exists("feedback"):
                os.makedirs("feedback")

            if os.path.exists(json_path):
                with open(json_path, "r") as file:
                    data = json.load(file)
            else:
                data = []

            image_feedback = next((item for item in data if snippet_name in item), None)
            if image_feedback is not None:
                image_feedback[snippet_name].append(feedback_data)
            else:
                image_feedback = {snippet_name: [feedback_data]}
                data.append(image_feedback)

            with open(json_path, "w") as file:
                json.dump(data, file)

    # Sessions Settings Screen
    def open_session_settings(self):
        # Forget any existing frames to ensure only settings frame is visible
        self.start_frame.pack_forget()
        self.main_frame.pack_forget()

        # Create the settings frame
        self.settings_frame = tk.Frame(self.master, borderwidth=2, relief="groove", padx=10, pady=10)
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

        back_button = tk.Button(self.settings_frame, text="Start", command=self.save_settings_and_redirect, bg="#c0dbf1")
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
            sorted_image_list = sorted(self.image_list)
            for i in range(len(sorted_image_list)):
                self.snippets.append([sorted_image_list[i], sorted_image_list[(i+1) % len(sorted_image_list)]])
            # append the last snippet combi
            self.snippets.append([sorted_image_list[-1], sorted_image_list[0]])
            # generate triplets, also in order
            for i in range(len(sorted_image_list)):
                self.snippets.append([sorted_image_list[i], sorted_image_list[(i+1) % len(sorted_image_list)], sorted_image_list[(i+2) % len(sorted_image_list)]])
            # generate the last two, that are wrapping around
            self.snippets.append([sorted_image_list[-1], sorted_image_list[0], sorted_image_list[1]])
            self.snippets.append([sorted_image_list[-2], sorted_image_list[-1], sorted_image_list[0]])

    def name_from_snippet(self, snippet):
        return '—'.join([f'\'{image.split("/")[-1]}\'' for image in snippet])

def main():
    root = tk.Tk()
    app = ImageSnippetApp(root)
    root.configure()
    root.mainloop()

if __name__ == "__main__":
    main()


