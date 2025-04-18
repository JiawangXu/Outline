
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from thumbnail import *

class Thumbnail_Frame(ttk.Frame):
    def __init__(
            self, 
            master,
            root,
            width=250,
            padding=5
            ):
        
        super().__init__(master=master, width=width, padding=padding)
        self.pack_propagate(False)  # 禁用对父容器的尺寸影响

        self.master=master
        self.root = root
        self.buttons = {}

        cover = ttk.LabelFrame(
            self,
            text=r'Dicom Index',
        )
        cover.pack(fill=BOTH, expand=True)

        self.canvas = ttk.Canvas(cover)

        self.index_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.index_frame, anchor="nw")

        def on_scroll(*args):
            self.canvas.yview(*args)
        vertical_scrollbar = ttk.Scrollbar(cover, orient="vertical", command=on_scroll, style=(SECONDARY, ROUND))
        vertical_scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.config(yscrollcommand=vertical_scrollbar.set)
        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(side=LEFT, fill=BOTH)
    
    def set_thumbnail(self, ):
        for button in self.buttons.values():
            button.pack_forget()
        self.buttons = {}
        for k, v in self.root.all_data.items():
            button = Thumbnail_Button(self.index_frame, self.root, self.canvas, k, v)
            button.pack(padx=5, pady=5)
            self.buttons[k] = button
        list(self.buttons.values())[0].chosen_command()

    