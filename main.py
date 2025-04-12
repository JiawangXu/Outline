import argparse
import os
from utils import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import pydicom
import cv2



class Main(ttk.Window):
    """
    The main application window that manages the layout and functionality of the DICOM reader.

    Parameters:
    - title: The title of the main window.
    - opt: An object containing various configuration options.
    - *args, **kwargs: Additional arguments for the ttk.Window class.
    """
    def __init__(self, title, opt, *args, **kwargs) -> None:
        super().__init__(title=title, *args, **kwargs)
        # parameters
        self.geometry(f"{int(opt.width)}x{int(opt.height)}")
        self.all_data = {}
        self.save_path = opt.save
        if not os.path.exists(opt.save):
            os.mkdir(opt.save)
            
        self.grid_columnconfigure(0, weight=1)

        self.filename = ttk.StringVar(value='DICOM')
        self.change = ttk.IntVar(value=0)

        self.dicom_all_ = ttk.Frame(self)
        self.dicom_all_.grid(row=1, column=0, sticky="nsew")
        self.create_thumbnail_frame()
        self.create_dicom_frame()
        self.create_menu_frame()
