import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from tkinter import filedialog
from utils import get_files, Button
import pydicom
import numpy as np


class Dicom_Menu(ttk.Frame):
    def __init__(
            self, 
            master: ttk.Frame, 
            root: ttk.Frame,
            ) -> None:
        super().__init__(master=master)
        
        self.root = root
        self.master = master
        self.viewer = root.viewer

        Button(
            master=self, 
            icons=r'icons\flip-horizontal',
            annotation='Flip Horizontal',
            command=self.flip_horizontal
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\flip-vertical',
            annotation='Flip Vertical',
            command=self.flip_vertical
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\reverse',
            annotation='Reverse',
            command=self.reverse
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\counterclockwise',
            annotation='Counterclockwise',
            command=self.counterclockwise
        ).pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)
        

    ### button function ###
        

    ### utilitarian fuction ###
    
    def check_save(self, filepath):
        """
        Displays a warning window when attempting to load new files without saving current changes.

        Parameters:
        - filepath: Path to the file being loaded
        """
        new_window = ttk.Toplevel()
        new_window.grab_set()
        new_window.title('Loading Progress')
        x = self.master.winfo_masterx() + self.master.winfo_reqwidth() // 2 - new_window.winfo_reqwidth() // 2
        y = self.master.winfo_mastery() + self.master.winfo_reqheight() // 2 - new_window.winfo_reqheight() // 2
        new_window.geometry(f"+{x}+{y}")

        ttk.Label(new_window, text='File not saved').grid(row=0, column=1, pady=10)
    
    def flip_horizontal(self):
        """
        Flips the image horizontally (left-right) and updates the display.
        """
        self.viewer.mask = self.viewer.mask[:, ::-1]
        self.viewer.show_image()

    def flip_vertical(self):
        """
        Flips the image vertically (up-down) and updates the display.
        """
        self.viewer.mask = self.viewer.mask[:, :, ::-1]
        self.viewer.show_image()

    def reverse(self):
        """
        Reverses the image order and adjusts the current slice index accordingly.
        """
        self.viewer.mask = self.viewer.mask[::-1]
        page = self.viewer.crt_index.get()
        self.viewer.crt_index.set(len(self.viewer.dicom_paths)-1-page)
        self.viewer.show_image()

    def counterclockwise(self):
        """
        Rotates the image 90 degrees counterclockwise and updates the display.
        """
        self.viewer.mask = np.rot90(self.viewer.mask, k=1, axes=(1, 2))
        self.viewer.show_image()