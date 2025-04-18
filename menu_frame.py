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
        self.add(self.check_page, text='文件')

        from menu import Dicom_Menu
        self.file_page = Dicom_Menu(self, self.master)
        self.file_page.pack()
        self.add(self.file_page, text='Dicom')

        
        from menu import Outline_Menu
        self.outline_page = Outline_Menu(self, self.master)
        self.outline_page.pack()
        self.add(self.outline_page, text='勾画')


        # ### magnification notebook ###
        # self.fix = ttk.Notebook(self)
        # self.fix.pack(fill=X, side=TOP, pady=10)
        # self.fix.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # # magnify
        # from l_mag_page import Mag_Page
        # self.mag_page = Mag_Page(self.fix, self.master)
        # self.mag_page.pack()
        # self.fix.add(self.mag_page, text='缩放')
        
        # ### bottom ###
        # self.save_button = ttk.Button(
        #     master=self,
        #     text='已保存',
        #     command=self.save_msk,
        #     bootstyle=(INFO, OUTLINE)
        # )
        # self.save_button.pack(fill=X, side=TOP, pady=4)

        # ttk.Button(
        #     master=self,
        #     text='重新载入',
        #     command=self.reload_pic,
        #     bootstyle=(INFO, OUTLINE)
        # ).pack(fill=X, side=TOP, pady=4)


    ### buttons function ###
    def save_msk(self, *args):
        self.canvas.save_msk(*args)
    
    def reload_pic(self,):
        page = self.canvas.crt_index.get()
        self.canvas.change.set(0)
        self.canvas.openserie(self.canvas.path)
        self.canvas.crt_index.set(page)
        self.canvas.show_image()
        
    def change_style(self, *args):
        if self.canvas.change.get():
            self.save_button.config(text='有修改', bootstyle=(DANGER, OUTLINE))
        else:
            self.save_button.config(text='已保存', bootstyle=(INFO, OUTLINE))

    ### trace function ###
    def change_style(self, *args):
        if self.canvas.change.get():
            self.save_button.config(text='有修改', bootstyle=(DANGER, OUTLINE))
        else:
            self.save_button.config(text='已保存', bootstyle=(INFO, OUTLINE))
    