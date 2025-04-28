import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils import Button


class File_Menu(ttk.Frame):
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
            icons=r'icons\open_folder',
            annotation='Open Folder',
            command=self.root.opendirectory
        ).pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)

        Button(
            master=self, 
            icons=r'icons\save',
            annotation='Save (CTRL + s)',
            command=self.viewer.save_msk
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