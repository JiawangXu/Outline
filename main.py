import argparse
import os
from utils import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import pydicom
import cv2

class Main(ttk.Window):
    def __init__(self, title, *args, **kwargs) -> None:
        super().__init__(title=title, *args, **kwargs)
        # parameters
        self.geometry(f"{int(opt.width)}x{int(opt.height)}")
        self.all_data = {}
        self.save_path = opt.save
        if not os.path.exists(opt.save):
            os.mkdir(opt.save)
            
        self.grid_columnconfigure(0, weight=1)
        # style = ttk.Style()
        # style.theme_use('superhero')

        self.filename = ttk.StringVar(value='DICOM')
        self.change = ttk.IntVar(value=0)

        self.dicom_all_ = ttk.Frame(self)
        self.dicom_all_.grid(row=1, column=0, sticky="nsew")
        self.create_thumbnail_frame()
        self.create_dicom_frame()
        self.create_menu_frame()
        
        # 设置行和列的权重
        self.grid_rowconfigure(1, weight=1)

        # trace variable ###
        self.filename.trace_add('write', self.viewer.openserie)
        # self.change.trace_add("write", self.lframe.change_style)

        # buttons
        self.bind("<KeyPress>", self.on_press)
        self.bind("<Configure>", self.on_configure)
        self.bind("<KeyRelease>", self.release_press)

        self.opendirectory([r"datas"])

    ### create frames ###
    def create_menu_frame(self):
        from menu_frame import Menu_Frame
        self.Menu = Menu_Frame(self, self)
        self.Menu.grid(row=0, column=0, sticky="nsew")

    def create_thumbnail_frame(self):
        from thumbnail_frame import Thumbnail_Frame
        self.Thumbnail = Thumbnail_Frame(self.dicom_all_, self)
        self.Thumbnail.pack(side=LEFT, fill=Y)

    def create_dicom_frame(self):
        from dicom_frame import Dicom_Frame
        self.Dicom = Dicom_Frame(self.dicom_all_, self)
        self.Dicom.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self.viewer = self.Dicom.viewer
        self.annotation = self.Dicom.annotation

        self.viewer.save_path = self.save_path
        self.binds(self.viewer.buttons())

    ### buttton function ###
    def on_press(self, event):
        if event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            self.viewer.canvas.bind('<Motion>', self.Menu.outline_page.show_cross)
            self.viewer.canvas.bind('<Button-1>', self.Menu.outline_page.drag_tap)
            self.viewer.canvas.bind('<Button-3>', self.Menu.outline_page.zoom_tap)
            self.viewer.canvas.bind('<MouseWheel>', self.Menu.outline_page.zoom_wheel)
        elif event.keysym == 'Control_L' or event.keysym == 'Control_R':
            self.viewer.canvas.bind('<Button-1>', self.Menu.outline_page.add_tap)
            self.viewer.canvas.bind('<Button-3>', self.Menu.outline_page.del_tap)
        self.unbind("<KeyPress>")
            
    def release_press(self, event):
        if event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            self.viewer.canvas.unbind('<Motion>')
            self.viewer.canvas.unbind('<Button-1>')
            self.viewer.canvas.unbind('<Button-3>')
            self.viewer.canvas.bind('<MouseWheel>', self.viewer.move_slider)
        elif event.keysym == 'Control_L' or event.keysym == 'Control_R':
            self.viewer.canvas.unbind('<Button-1>')
            self.viewer.canvas.unbind('<Button-3>')
        self.bind("<KeyPress>", self.on_press)
        self.viewer.show_image()
        
    def on_configure(self, event, *args):
        if event.widget == self:
            if self.viewer.dicom_paths is not None:
                self.viewer.show_image()

    ### utilitarian function ###
    def binds(self, buttons: list):
        for target, key, func in buttons:
            if target is None:
                target = self
            target.bind(key, func)
            
    def unbinds(self, buttons: list):
        for target, key, func in buttons:
            if target is None:
                target = self
            target.unbind(key)

    def opendirectory(self, filepath=None):
        # 打开一张图片并显示

        if filepath is None:
            filepath = filedialog.askdirectory()
            if not os.path.exists(filepath):
                return
            filepath = [filepath]
        if not isinstance(filepath, list):
            filepath = list(filepath)

        self.all_data = self.get_paths(filepath)
        self.Thumbnail.set_thumbnail()

    def get_paths(self, father_paths: str, ext=['dcm', 'DCM']):
        files = []
        paths = {}

        father_paths = father_paths if isinstance(father_paths, list) else os.listdir(father_paths)
        for p in father_paths:
            files += get_files(p, ext=ext)
        
        for file in files:
            pdcm = pydicom.dcmread(file, force=True)
            paths[file] = [str(pdcm[0x0020000e].value), int(pdcm[0x00200013].value)]

        files = {}
        for k, v in paths.items():
            v, _ = v
            if v not in files:
                files[v] = {'dicom': [k], 'mask': None}
            else:
                files[v]['dicom'].append(k)
        
        for k in files:
            files[k]['dicom'] = sorted(files[k]['dicom'], key=lambda x: paths[x][1])
        
        def get_common_parent(p):
            for base_father in father_paths:
                try: 
                    return os.path.relpath(p, base_father)
                except ValueError:
                    continue

        for k, v in files.items():
            parent = os.path.commonpath(v['dicom'])
            files[k]['common_parent'] = get_common_parent(parent)
            parents = [parent]
            while True:
                parent, folder = os.path.split(parent)
                if folder == '':
                    break
                parents.append(parent)
            for parent in parents:
                masks = [fr'{parent}/{i}' for i in os.listdir(parent) if i.split('.')[-1].lower() in ['tar', 'nii', 'nrrd', 'gz']]
                if len(masks) > 0:
                    break
            if len(masks) == 1:
                files[k]['mask'] = masks[0]
            elif len(masks) > 1:
                files[k]['mask'] = masks

        files = dict(sorted(files.items(), key=lambda item: (item[1]["common_parent"], item[0])))
        for idx, k in enumerate(files.keys()):
            files[k]['index'] = idx+1

        for k, v in files.items():
            v = v['dicom']
            thumbnail = self.viewer.get_raw_image(v[len(v)//2])
            files[k]['thumbnail'] = thumbnail

        return files

    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str,
                        default=r'dcm_data')
    parser.add_argument('--save', type=str,
                        default=r'msk_data')
    parser.add_argument('--height', type=int, default=1200)
    parser.add_argument('--width', type=int, default=1500)
    opt = parser.parse_args()

    # window generate
    os.system("cls")
    app = Main("dicom reader v0.4")

    app.mainloop()