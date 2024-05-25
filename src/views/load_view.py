from tkinter import ttk 
from tkinter import filedialog
import os

from pony.orm import *


import ebisu
import datetime

from enum import Enum

class LoadView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = parent.db
        self.selected_folder_path = None

        self.local_states = Enum("LocalStates", ["NO_FOLDER_SELECTED", "FOLDER_SELECTED", "FOLDER_SELECTED_NO_IMAGES", "SNIPPETS_LOADED"])
        self.current_local_state = self.local_states.NO_FOLDER_SELECTED

        self.reload()

    def load(self):
        pass

    def reload(self):
        # remove all widgets
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Load Snippets From a Folder on Your Device").pack(padx=5, pady=5)
        
        if self.current_local_state == self.local_states.NO_FOLDER_SELECTED:
            ttk.Button(self, text="Select Folder", command=self.open_folder).pack(padx=5, pady=5)

        if self.current_local_state == self.local_states.FOLDER_SELECTED:
            ttk.Button(self, text="Select Another Folder", command=self.open_folder).pack(padx=5, pady=5)
            ttk.Label(self, text=f"Selected Folder: {self.selected_folder_path}").pack(padx=5, pady=5)
            ttk.Label(self, text=f"Found {len(self.image_list)} images.").pack(padx=5, pady=5)
            ttk.Button(self, text="Create Snippets", command=self.confirm_images).pack(padx=5, pady=5)
            ttk.Button(self, text="Select Another Folder", command=self.open_folder).pack(padx=5, pady=5)

        if self.current_local_state == self.local_states.FOLDER_SELECTED_NO_IMAGES:
            ttk.Label(self, text=f"Selected Folder: {self.selected_folder_path}").pack(padx=5, pady=5)
            ttk.Label(self, text="No images found in folder").pack(padx=5, pady=5)
            ttk.Button(self, text="Select Another Folder", command=self.open_folder).pack(padx=5, pady=5)

        if self.current_local_state == self.local_states.SNIPPETS_LOADED:
            ttk.Label(self, text=f"Selected Folder: {self.selected_folder_path}").pack(padx=5, pady=5)
            ttk.Label(self, text="Snippets created :)").pack(padx=5, pady=5)
            ttk.Button(self, text="Start Practice", command=self.start_practice).pack(padx=5, pady=5)
            # allow selecting another folder
            ttk.Button(self, text="Select Another Folder", command=self.open_folder).pack(padx=5, pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x")
        ttk.Button(self, text="Back To Start", command=lambda: self.parent.go_to("start")).pack(padx=5, pady=5)
        

    def load_images_from_folder(self, folder_path):
        self.selected_folder_path = folder_path
        image_list = []
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_list.append([filename, filepath])
        return image_list

    def open_folder(self):
        # initialdir=self.last_folder_path
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.image_list = self.load_images_from_folder(folder_path)
            if len(self.image_list) == 0:
                self.current_local_state = self.local_states.FOLDER_SELECTED_NO_IMAGES
            else:
                self.current_local_state = self.local_states.FOLDER_SELECTED
            self.reload()


    @db_session
    def confirm_images(self):
            # MusicPiece based on folder name
            self.music_piece = self.db.MusicPiece(title=self.selected_folder_path.split("/")[-1], folder_path=self.selected_folder_path)
            snippet_images = []
            for image in self.image_list:
                img_obj = self.db.SnippetImage(path=image[1])
                snippet_images.append(img_obj)

            snippets_and_images = {}
            
            # create Snippet objects
            # first: Snippets with 1 SnippetImage each
            for img_obj in snippet_images:
                snippet = self.db.Snippet(snippet_images=[img_obj], music_piece=self.music_piece, snippet_name=img_obj.path.split("/")[-1])
                snippets_and_images[img_obj] = snippet
            
            # second: Snippets with 2 SnippetImages each
            # order by filename and only connect direct neighbors
            snippet_images.sort(key=lambda x: x.path)
            for i in range(0, len(snippet_images)-1, 2):
                snippet = self.db.Snippet(snippet_images=[snippet_images[i], snippet_images[i+1]], music_piece=self.music_piece, snippet_name=f"{snippet_images[i].path.split('/')[-1]} and {snippet_images[i+1].path.split('/')[-1]}")
                # for each of the images, find the Snippet object which contains it and ass as prerequsite
                snippet.prerequisite_snippets.add(snippets_and_images[snippet_images[i]])
                snippet.prerequisite_snippets.add(snippets_and_images[snippet_images[i+1]])

            # third: Snippets with 3 SnippetImages each
            # also, only connect direct neighbors
            for i in range(0, len(snippet_images)-2, 3):
                snippet = self.db.Snippet(snippet_images=[snippet_images[i], snippet_images[i+1], snippet_images[i+2]], music_piece=self.music_piece, snippet_name=f"{snippet_images[i].path.split('/')[-1]}, {snippet_images[i+1].path.split('/')[-1]} and {snippet_images[i+2].path.split('/')[-1]}")
                snippet.prerequisite_snippets.add(snippets_and_images[snippet_images[i]])
                snippet.prerequisite_snippets.add(snippets_and_images[snippet_images[i+1]])
                snippet.prerequisite_snippets.add(snippets_and_images[snippet_images[i+2]])

            # ebisu default values
            for snippet in self.music_piece.snippets:
                snippet.alpha, snippet.beta, snippet.t = ebisu.defaultModel(10)
                snippet.last_seen = datetime.datetime.now()

            self.current_local_state = self.local_states.SNIPPETS_LOADED
            self.parent.current_state = self.parent.states.CURRENT_MUSIC_PIECE_EXISTS

            self.reload()

    @db_session
    def start_practice(self):
        settings = self.db.GlobalSettings.get()
        settings.current_music_piece = self.music_piece
        self.parent.go_to("practice")