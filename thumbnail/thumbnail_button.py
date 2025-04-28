
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np
import cv2
from PIL import Image, ImageTk

class Thumbnail_Button(ttk.Button):
    """
    Initializes a thumbnail button with image preview and metadata display.

    Args:
        master: Parent widget
        root: Main application window
        canvas: Canvas for display
        key: Unique identifier for the thumbnail
        value: Dictionary containing thumbnail data
        type: Type of thumbnail (default: 'filepath')
    """
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
        """
        Handles thumbnail selection with unsaved changes verification.
        Updates button styling and loads selected DICOM series.
        """
        if self.root.change.get():
            self.check_save()
        if not self.root.change.get():
            try:
                old_filename = self.root.filename.get()
                self.root.Thumbnail.buttons[old_filename].configure(style="Hover.TButton")
            except:
                pass
            self.root.filename.set(self.filename)
            self.config(style="Chosen.TButton")

    def check_save(self):
        """
        Displays save confirmation dialog when unsaved changes exist.
        Provides options to save, discard, or cancel the operation.
        """
        new_window = ttk.Toplevel(self.root)
        new_window.grab_set()
        new_window.title()
        x = self.root.winfo_rootx() + self.root.winfo_reqwidth() // 2 - new_window.winfo_reqwidth() // 2
        y = self.root.winfo_rooty() + self.root.winfo_reqheight() // 2 - new_window.winfo_reqheight() // 2
        new_window.geometry(f"+{x}+{y}")

        ttk.Label(new_window, text='File not saved').grid(row=0, column=1, pady=10)

        def confirm():
            self.root.viewer.save_msk()
            new_window.destroy()
            new_window.grab_release()
                    
        def refuse():
            self.root.change.set(0)
            new_window.destroy()
            new_window.grab_release()

        def cancel():
            new_window.destroy()
            new_window.grab_release()

        confirm_button = ttk.Button(new_window, text="confirm", command=confirm)
        confirm_button.grid(row=1, column=0, padx=10, pady=10)

        confirm_button = ttk.Button(new_window, text="refuse", command=refuse)
        confirm_button.grid(row=1, column=1, padx=10, pady=10)

        confirm_button = ttk.Button(new_window, text="Cancel", command=cancel)
        confirm_button.grid(row=1, column=2, padx=10, pady=10)
        
        self.root.wait_window(new_window)