import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from tkinter import filedialog
from utils import get_files, Button
import pydicom


class File_Menu(ttk.Frame):
    def __init__(
            self, 
            master: ttk.Frame, 
            root: ttk.Frame,
            ) -> None:
        super().__init__(master=master)
        
        self.root = root
        self.master = master
        # self.canvas = root.viewer

        Button(
            master=self, 
            icons=r'icons\open_folder',
            annotation='打开文件', 
            command=self.root.opendirectory
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