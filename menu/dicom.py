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
            annotation='水平翻转', 
            command=self.flip_horizontal
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\flip-vertical',
            annotation='垂直翻转', 
            command=self.flip_vertical
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\reverse',
            annotation='前后调换', 
            command=self.reverse
        ).pack(side=LEFT, padx=5, pady=5)
        
        Button(
            master=self, 
            icons=r'icons\counterclockwise',
            annotation='逆时针旋转', 
            command=self.counterclockwise
        ).pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)
        

    ### button function ###
        

    ### utilitarian fuction ###
    
    def check_save(self, filepath):
        
        new_window = ttk.Toplevel()
        new_window.grab_set()
        new_window.title('加载进度')
        # 计算居中位置
        x = self.master.winfo_masterx() + self.master.winfo_reqwidth() // 2 - new_window.winfo_reqwidth() // 2
        y = self.master.winfo_mastery() + self.master.winfo_reqheight() // 2 - new_window.winfo_reqheight() // 2
        new_window.geometry(f"+{x}+{y}")

        ttk.Label(new_window, text='文件未保存').grid(row=0, column=1, pady=10)
    
    def flip_horizontal(self):
        self.viewer.mask = self.viewer.mask[:, ::-1]
        self.viewer.show_image()

    def flip_vertical(self):
        self.viewer.mask = self.viewer.mask[:, :, ::-1]
        self.viewer.show_image()

    def reverse(self):
        self.viewer.mask = self.viewer.mask[::-1]
        page = self.viewer.crt_index.get()
        self.viewer.crt_index.set(len(self.viewer.dicom_paths)-1-page)
        self.viewer.show_image()

    def counterclockwise(self):
        self.viewer.mask = np.rot90(self.viewer.mask, k=1, axes=(1, 2))
        self.viewer.show_image()