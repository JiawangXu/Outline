import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class Menu_Frame(ttk.Notebook):
    def __init__(
            self, 
            master, 
            root,
            ) -> None:
        super().__init__(master=master)

        self.master = master
        self.root = root
        # self.canvas = master.canvas

        from menu import File_Menu
        self.check_page = File_Menu(self, self.root)
        self.add(self.check_page, text='File')

        from menu import Dicom_Menu
        self.file_page = Dicom_Menu(self, self.master)
        self.file_page.pack()
        self.add(self.file_page, text='Dicom')

        
        from menu import Outline_Menu
        self.outline_page = Outline_Menu(self, self.master)
        self.outline_page.pack()
        self.add(self.outline_page, text='Outline')



    ### buttons function ###
    def save_msk(self, *args):
        """
        Triggers mask saving operation through the canvas controller.
        """
        self.canvas.save_msk(*args)
    
    def reload_pic(self,):
        """
        Reloads current DICOM series while preserving the current slice position.
        """
        page = self.canvas.crt_index.get()
        self.canvas.change.set(0)
        self.canvas.openserie(self.canvas.path)
        self.canvas.crt_index.set(page)
        self.canvas.show_image()
        
    def change_style(self, *args):
        """
        Updates save button appearance based on modification state.
        Shows 'Modified' (red) or 'Saved' (blue) visual indicators.
        """
        if self.canvas.change.get():
            self.save_button.config(text='Modified', bootstyle=(DANGER, OUTLINE))
        else:
            self.save_button.config(text='Saved', bootstyle=(INFO, OUTLINE))

    