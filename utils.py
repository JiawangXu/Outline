
import pydicom
import SimpleITK as sitk

import numpy as np
import ttkbootstrap as ttk

from PIL import Image, ImageTk, ImageSequence
import imageio
import cv2

import nrrd
import nibabel as nib
import json
import tempfile
import tarfile

from pydicom.charset import convert_encodings
import os
import shutil
import re
import io

import warnings
warnings.filterwarnings("error")

def create_folder(path: str, empty: bool = True):
    if empty and os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)

def print_progress_bar(current, max_value, length=50):
    percent = (current / max_value)
    arrow = '=' * int(length * percent)
    spaces = ' ' * (length - len(arrow))
    progress = f"{current}/{max_value} [{arrow}{spaces}] {percent*100:.2f}%"
    return progress

def get_files(path, ext=None):
    paths = []
    for file in [fr'{path}/{i}' for i in os.listdir(path)]:
        if os.path.isdir(file):
            paths += get_files(file, ext=ext)
        else:
            if ext is not None:
                if isinstance(ext, str):
                    ext = [ext]
                if file.split('.')[-1] not in ext:
                    continue
            paths.append(file)
    return paths

def get_value(v):
    if isinstance(v, list) or isinstance(v, tuple):
        v = v[0]
    v = str(v)
    div_char = list(set(re.findall(r'[^0-9\-.]', v)))
    for div in div_char:
        v = v.split(div)[0]
    return round(float(v))


def annotation_decode(text, encodetype):
    if isinstance(text, pydicom.multival.MultiValue) or isinstance(text, list):
        return [annotation_decode(i, encodetype) for i in text]
    elif isinstance(text, pydicom.valuerep.DSfloat):
        return float(text)
    elif isinstance(text, int) or isinstance(text, float):
        return text
    elif isinstance(text, bytes):
        try:
            return text.decode('GBK')
        except UnicodeDecodeError:
            return ''
    else:
        try:
            return text.encode(convert_encodings(encodetype)[0]).decode('GBK')
        except UnicodeDecodeError:
            return ''
    
def get_annotation(s: pydicom.FileDataset, encodetype=None, not_save_tag=[]):
    datas = {}
    for i in s:
        tag, name, value = i.tag, i.name, i.value
        if value == '' or name in not_save_tag or value is None:
            continue
        data = {
            'tag': tag,
            'name': name,
            'value': value,
        }
        if isinstance(value, pydicom.Sequence):
            data['value'] = ''
            data['children'] = {}
            for item in value:
                data['children'].update(get_annotation(item, encodetype, not_save_tag))
        else:
            # if str(tag) == "(0028, 1050)":
            #     print(1)
            data['value'] = annotation_decode(data['value'], encodetype)
            if data['value'] == '':
                continue
        tag = "".join([i for i in str(tag) if i.isdigit()])
        datas[tag] = data
    return(datas)

def read_nrrd_ori(mask_path: str):
    mask, _ = nrrd.read(mask_path)
    mask = np.rot90(mask, k=3)
    mask = np.fliplr(mask)
    mask = np.transpose(mask, [2, 0, 1])
    mask[mask > 0] = 1
    return np.squeeze(np.array(mask, dtype=np.uint8))

def read_nrrd_new(mask_path: str):
    # temp_dir = r'temp'
    # create_folder(temp_dir)
    with tarfile.open(mask_path, 'r') as tar:
        record = json.load(tar.extractfile('mask.json'))

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(tar.extractfile('mask.nrrd').read())
        temp_file.close()
        mask, _ = nrrd.read(temp_file.name)
        mask[mask > 0] = 1
        os.remove(temp_file.name)
    # shutil.rmtree(temp_dir)
    return np.squeeze(np.array(mask, dtype=np.uint8)), record

def read_nii(mask_path: str):
    temp_dir = r'temp'
    create_folder(temp_dir)
    with tarfile.open(mask_path, 'r') as tar:
        tar.extractall(temp_dir)
    for mask_path in os.listdir(temp_dir):
        if mask_path[-2:] == 'gz':
            break
    mask = nib.load(fr"{temp_dir}\{mask_path}").get_fdata()
    mask = np.moveaxis(mask, np.argmin(mask.shape), -1)
    mask = np.rot90(mask, k=3)
    mask = np.fliplr(mask)
    mask = np.transpose(mask, [2, 0, 1])
    mask[mask > 0] = 1
    shutil.rmtree(temp_dir)
    return np.squeeze(np.array(mask, dtype=np.uint8))

def get_mask_range(mask):
    whether_mask = [np.sum(mask[i]) for i in range(mask.shape[0])]
    whether_mask = [next((i for i, x in enumerate(whether_mask) if x != 0), -1), len(
        mask)-next((i for i, x in enumerate(whether_mask[::-1]) if x != 0), -1)]
    whether_mask = [max(0, whether_mask[0]),
                    min(whether_mask[1], mask.shape[0])]
    
    return whether_mask[0], whether_mask[1]


def create_tar_file(folder_path, tar_file_name):
    with tarfile.open(tar_file_name, 'w') as tar:
        for file in os.listdir(folder_path):
            file = fr'{folder_path}/{file}'
            tar.add(file, arcname=os.path.basename(file))


def read_nrrd_new(mask_path: str):
    with tarfile.open(mask_path, 'r') as tar:
        record = json.load(tar.extractfile('mask.json'))

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(tar.extractfile('mask.nrrd').read())
        temp_file.close()
        mask, _ = nrrd.read(temp_file.name)
        mask[mask > 0] = 1
        os.remove(temp_file.name)

    return np.squeeze(np.array(mask, dtype=np.uint8)), record

            
def read_mask(path):
    record = {}
    
    _, ext = os.path.splitext(path)
    if ext == '.tar':
        temp_dir = r'temp'
        create_folder(temp_dir)
        with tarfile.open(path, 'r') as tar:
            tar.extractall(temp_dir)
        for mask_path in os.listdir(temp_dir):
            if mask_path[-2:] == 'gz':
                break
        ext = '.nii'
        path = fr"{temp_dir}\{mask_path}"

    if ext == ".nrrd":
        mask, _ = nrrd.read(path)
    elif ext == ".nii":
        mask = nib.load(path).get_fdata()
        mask = np.moveaxis(mask, np.argmin(mask.shape), -1)
            
    mask = np.rot90(mask, k=3)
    mask = np.fliplr(mask)
    mask = np.transpose(mask, [2, 0, 1])
    mask[mask > 0] = 1

    if os.path.exists(r'temp'):
        shutil.rmtree(r'temp')

    return np.squeeze(np.array(mask[::-1], dtype=np.uint8)), record


def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=5): 
        dist = ((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5 
        pts = [] 
        for i in np.arange(0, dist, gap): 
            r = i/dist 
            x = int((pt1[0]*(1-r)+pt2[0]*r)+.5) 
            y = int((pt1[1]*(1-r)+pt2[1]*r)+.5) 
            p = (x,y) 
            pts.append(p) 
    
        if style == 'dotted': 
            for p in pts: 
                cv2.circle(img, p, thickness, color, -1) 
        else: 
            s = pts[0] 
            e = pts[0] 
            i = 0 
            for p in pts: 
                s = e 
                e = p 
                if i%2 == 1: 
                    cv2.line(img, s, e, color, thickness) 
                i += 1


def rearrange_numbers(input_string):
    # 使用正则表达式提取字符串中的数字
    numbers = re.findall(r'[0-9a-fA-F]', str(input_string))

    # 重新按原来的顺序组成新的字符串
    result_string = ''.join(numbers)

    return result_string

class Button(ttk.Button):
    def __init__(self, master, icons, annotation, pic_size=(48, 48), active=True, *args, **kwargs):
        self.pic_size = pic_size
        self.annotation = annotation
        self.tooltip = None
        self.start_update_frame = None

        style = ttk.Style()
        style.configure("Custom.TButton", background="white", bordercolor="white", foreground='blue', padding=2, relief='flat')
        style.map("Custom.TButton",
                background=[("active", "white")],
                relief=[("active", "solid")],
                bordercolor=[("active", "#17a2b8")],)
        
        self.image = [self.create_png(fr'{icons}\0.png')]
        if os.path.exists(fr'{icons}\1.gif'):
            self.create_animation(fr'{icons}\1.gif')

        super().__init__(master=master, image=self.image[0], style = "Custom.TButton", *args, **kwargs)

        if active:
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)
    
    def active(self, ):
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def disactive(self, ):
        self.unbind("<Enter>")
        self.unbind("<Leave>")

    def on_enter(self, event):
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + self.pic_size[0]
        y += self.winfo_rooty() + self.pic_size[1]

        # 创建 Tooltip 窗口
        self.tooltip = ttk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.bind("<Enter>", self.on_enter)

        # 显示 Tooltip 文本
        label = ttk.Label(self.tooltip, text=" " + self.annotation, background="lightyellow", relief="solid", borderwidth=1)
        label.pack(ipadx=2)
        
        if len(self.image) == 2:
            if self.start_update_frame is None:
                self.update_frame(0)

    def on_leave(self, event):
        if self.start_update_frame:
            self.after_cancel(self.start_update_frame)
            self.start_update_frame = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        if len(self.image) == 2:
            self.configure(image=self.image[0])
        

    def create_png(self, path):
        image = Image.open(path)
        image = image.resize(self.pic_size, resample=Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def create_animation(self, path):
        with Image.open(path) as image:
            frames = [ImageTk.PhotoImage(frame.resize(self.pic_size, resample=Image.LANCZOS)) for frame in ImageSequence.Iterator(image)]
        self.image.append(frames)

    def update_frame(self, frame_index):
        self.configure(image=self.image[1][frame_index])
        next_frame_index = (frame_index + 1) % len(self.image[1])
        self.start_update_frame = self.after(60, self.update_frame, next_frame_index)
    

