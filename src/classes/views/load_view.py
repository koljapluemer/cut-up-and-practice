from tkinter import ttk 
from tkinter import filedialog
import os


class LoadView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Load Snippets From a Folder on Your Device").pack()
        ttk.Button(self, text="Select Folder", command=self.open_folder).pack()

        # back
        ttk.Button(self, text="Back To Start", command=lambda: parent.go_to("start")).pack()


    def load_images_from_folder(self, folder_path):
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

    def confirm_images(self):
            if self.image_list:

                for image in self.image_list:
                    print(image[0], image[1])
                    