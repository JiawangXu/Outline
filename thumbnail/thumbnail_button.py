
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np
import cv2
from PIL import Image, ImageTk

class Thumbnail_Button(ttk.Button):
    def __init__(  
            self,
            master,
            root,
            canvas: ttk.Canvas,
            key,  
            value, 
            type='filepath',   
    ):
        
        self.style = ttk.Style()
        self.style.configure("Hover.TButton", background="white", bordercolor="white", padding=2, relief='flat')
        self.style.map("Hover.TButton",
                background=[("active", "white")],
                relief=[("active", "solid")],
                bordercolor=[("active", "#17a2b8")],)
        self.style.configure("Chosen.TButton", background="white", bordercolor="#17a2b8", padding=2, relief="solid")
        
        self.master = master
        self.root = root
        canvas.update()
        self.canvas = canvas
        width = 210

        self.filename = key
        img = np.ones((width-10, width-10, 3), dtype=np.uint8) * 255
        thumbnail, text = value['thumbnail'], ['common_parent']
        thumbnail = cv2.resize(thumbnail, (width-70, width-70))
        img[15:width-55, 30:width-40] = thumbnail

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = .3
        font_thickness = 1

        index = fr'{value["index"]}/{len(root.all_data)}'
        text_size, _ = cv2.getTextSize(index, font, font_scale, font_thickness)
        cv2.putText(img, index, (2, text_size[1]+2), font, .3, (249, 120, 140), font_thickness)

        font_scale = .4
        text = value['common_parent']
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        cv2.putText(img, text, ((width-text_size[0])//2, width-40), font, font_scale, (0, 0, 0), font_thickness)
        
        self.img = ImageTk.PhotoImage(Image.fromarray(img))

        super().__init__(master=master, image=self.img, style="Hover.TButton", command=self.chosen_command)


    def chosen_command(self,):
        try:
            old_filename = self.root.filename.get()
            self.root.Thumbnail.buttons[old_filename].configure(style="Hover.TButton")
        except:
            pass
        self.root.filename.set(self.filename)
        self.config(style="Chosen.TButton")
