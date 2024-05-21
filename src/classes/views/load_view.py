from tkinter import ttk 
from tkinter import filedialog
import os

from pony.orm import *


import ebisu
import datetime

class LoadView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = parent.db
        self.selected_folder_path = None

        ttk.Label(self, text="Load Snippets From a Folder on Your Device").pack()
        ttk.Button(self, text="Select Folder", command=self.open_folder).pack()
        ttk.Button(self, text="Back To Start", command=lambda: parent.go_to("start")).pack()

    def load(self):
        pass

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
            # label with nr of img
            self.label = ttk.Label(self, text=f"Found {len(self.image_list)} images in {folder_path}").pack()
            # buttons to confirm and cancel
            ttk.Button(self, text="Create Snippets", command=self.confirm_images).pack()

    @db_session
    def confirm_images(self):
            if self.image_list:
                # MusicPiece based on folder name
                music_piece = self.db.MusicPiece(title=self.selected_folder_path.split("/")[-1], folder_path=self.selected_folder_path)
                snippet_images = []
                for image in self.image_list:
                    img_obj = self.db.SnippetImage(path=image[1])
                    snippet_images.append(img_obj)
                
                # create Snippet objects
                # first: Snippets with 1 SnippetImage each
                for img_obj in snippet_images:
                    self.db.Snippet(snippet_images=[img_obj], music_piece=music_piece, snippet_name=img_obj.path.split("/")[-1])
                
                # second: Snippets with 2 SnippetImages each
                # order by filename and only connect direct neighbors
                snippet_images.sort(key=lambda x: x.path)
                for i in range(0, len(snippet_images)-1, 2):
                    self.db.Snippet(snippet_images=[snippet_images[i], snippet_images[i+1]], music_piece=music_piece, snippet_name=f"{snippet_images[i].path.split('/')[-1]} and {snippet_images[i+1].path.split('/')[-1]}")

                # third: Snippets with 3 SnippetImages each
                # also, only connect direct neighbors
                for i in range(0, len(snippet_images)-2, 3):
                    self.db.Snippet(snippet_images=[snippet_images[i], snippet_images[i+1], snippet_images[i+2]], music_piece=music_piece, snippet_name=f"{snippet_images[i].path.split('/')[-1]}, {snippet_images[i+1].path.split('/')[-1]} and {snippet_images[i+2].path.split('/')[-1]}")

                # ebisu default values
                for snippet in music_piece.snippets:
                    snippet.alpha, snippet.beta, snippet.t = ebisu.defaultModel(10)
                    snippet.last_seen = datetime.datetime.now()