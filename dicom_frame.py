
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re
from tkinterdnd2.TkinterDnD import _require
from tkinterdnd2 import DND_FILES
import os
import dicom

class Dicom_Frame(ttk.Frame):
    def __init__(
            self, 
            master, 
            root,
            padding=5,
            ) -> None:
        super().__init__(master=master, padding=padding)
        # self.pack_propagate(False)

        self.master = master
        self.root = root

        _require(master) 
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.drop_inside_box)

        ### annotation tags ###
        tv = ttk.Labelframe(
            master=self,
            text="Dicom Tags",
            padding=10
        )
        tv.pack(fill=X, side=BOTTOM)

        # treeview
        self.annotation = ttk.Treeview(
            master=tv,
            columns=[0, 1, 2],
            show=HEADINGS,
            height=10,
        )
        self.annotation.heading(0, text='Tag ID')
        self.annotation.heading(1, text='Description')
        self.annotation.heading(2, text='Value')
        
        def update_column_width(event):
            self.set_column_width(0, .15, 120)
            self.set_column_width(1, .3, 140)
            self.set_column_width(2, .55, 250)
        self.annotation.bind("<Configure>", update_column_width)

        self.annotation.grid(row=0, column=0, sticky="nsew")
        def nothing(event):
            self.viewer.draw_contour()
        self.annotation.bind('<Up>', nothing)
        self.annotation.bind('<Down>', nothing)

        # 创建垂直滚动条并与文本框关联
        vertical_scrollbar = ttk.Scrollbar(tv, orient="vertical", command=self.annotation.yview, style=(INFO, ROUND))
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        self.annotation.config(yscrollcommand=vertical_scrollbar.set)

        # 创建水平滚动条并与文本框关联
        horizontal_scrollbar = ttk.Scrollbar(tv, orient="horizontal", command=self.annotation.xview, style=(INFO, ROUND))
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.annotation.config(xscrollcommand=horizontal_scrollbar.set)

        # 设置行和列的权重
        tv.grid_rowconfigure(0, weight=1)
        tv.grid_columnconfigure(0, weight=1)
        

        ### dicom show ###
        dicom_label = ttk.Labelframe(
            master=self,
            text="DICOM",
            padding=10,
        )
        dicom_label.pack(fill=BOTH, side=BOTTOM, expand=True)

        # pic show
        self.viewer = dicom.Viewer(dicom_label, self.root)
        self.viewer.pack(fill=BOTH, expand=True, pady=10)
        
    def drop_inside_box(self, event):
        filedirectory = [data for data in event.data.split(" ") if os.path.exists(data)]
        self.root.opendirectory(filepath=filedirectory)

    def set_column_width(self, column_id, percentage, min_width=None, max_width=None):
        # 计算列的宽度
        width = int(self.annotation.winfo_width() * float(percentage))
        if min_width is not None:
            width = max(width, min_width)
        if max_width is not None:
            width = min(width, max_width)
        self.annotation.column(column_id, width=width, stretch=False)
        