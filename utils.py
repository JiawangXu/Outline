import pydicom

import numpy as np
import ttkbootstrap as ttk

from PIL import Image, ImageTk, ImageSequence
import cv2

import nrrd
import nibabel as nib
import tarfile

from pydicom.charset import convert_encodings
import os
import shutil
import re

import warnings
warnings.filterwarnings("error")

def create_folder(path: str, empty: bool = True):
    """
    Creates a directory, optionally emptying existing directory.
    Args:
        path (str): Directory path to create
        empty (bool): Whether to clear existing directory (default: True)
    """
    if empty and os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)

def get_files(path, ext=None):
    """
    Recursively collects files from directory with optional extension filter.
    Args:
        path (str): Root directory path
        ext (str/list): File extension(s) to filter (e.g. '.dcm' or ['.png','.jpg'])
    Returns:
        list: Full paths of matching files
    """
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



def annotation_decode(text, encodetype):
    """
    Decodes DICOM text values using specified encoding (GBK fallback).
    Args:
        text: DICOM value (MultiValue/DSfloat/bytes/str)
        encodetype: DICOM encoding specifier (e.g. 'ISO_IR 100')
    Returns:
        Decoded text value
    """
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
    """
    Extracts structured metadata from DICOM dataset.
    Args:
        s: DICOM FileDataset object
        encodetype: Character encoding for text fields
        not_save_tag: List of tags to exclude
    Returns:
        dict: Hierarchical metadata structure
    """
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

def get_mask_range(mask):
    """
    Calculates first/last slices containing mask data.
    Args:
        mask (ndarray): 3D binary mask array (slices x height x width)
    Returns:
        tuple: (first_slice, last_slice) indices with mask content
    """
    whether_mask = [np.sum(mask[i]) for i in range(mask.shape[0])]
    whether_mask = [next((i for i, x in enumerate(whether_mask) if x != 0), -1), len(
        mask)-next((i for i, x in enumerate(whether_mask[::-1]) if x != 0), -1)]
    whether_mask = [max(0, whether_mask[0]),
                    min(whether_mask[1], mask.shape[0])]
    
    return whether_mask[0], whether_mask[1]

def read_mask(path):
    """
    Universal mask reader supporting multiple formats (.nrrd/.nii/.tar).
    Args:
        path (str): Path to mask file
    Returns:
        tuple: (mask_array, record_dict)
            mask_array: 3D binary mask (uint8)
            record_dict: Empty metadata dictionary
    """

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
    """
    Draws styled line (dotted/dashed) on image.
    Args:
        img (ndarray): Target image array
        pt1 (tuple): Start point (x,y)
        pt2 (tuple): End point (x,y)
        color: Line color (BGR tuple)
        thickness (int): Line thickness (default: 1)
        style (str): Line style ('dotted' or 'dashed', default: 'dotted')
        gap (int): Spacing between dots/dashes (default: 5)
    """
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
    """
    Filters and extracts alphanumeric characters from string.
    Args:
        input_string: Input string containing mixed characters
    Returns:
        str: String containing only alphanumeric characters
    """
    numbers = re.findall(r'[0-9]', str(input_string))

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
        """Enables button hover effects."""
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def disactive(self, ):
        """Disables button hover effects."""
        self.unbind("<Enter>")
        self.unbind("<Leave>")

    def on_enter(self, event):
        """Shows tooltip and starts animation on mouse enter."""
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + self.pic_size[0]
        y += self.winfo_rooty() + self.pic_size[1]


        self.tooltip = ttk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.bind("<Enter>", self.on_enter)


        label = ttk.Label(self.tooltip, text=" " + self.annotation, background="lightyellow", relief="solid", borderwidth=1)
        label.pack(ipadx=2)
        
        if len(self.image) == 2:
            if self.start_update_frame is None:
                self.update_frame(0)

    def on_leave(self, event):
        """Hides tooltip and stops animation on mouse leave."""
        if self.start_update_frame:
            self.after_cancel(self.start_update_frame)
            self.start_update_frame = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        if len(self.image) == 2:
            self.configure(image=self.image[0])
        

    def create_png(self, path):
        """
        Creates static button icon from PNG.
        Args:
            path (str): Image file path
        Returns:
            ImageTk.PhotoImage: Processed icon
        """
        image = Image.open(path)
        image = image.resize(self.pic_size, resample=Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def create_animation(self, path):
        """
        Preloads animated GIF frames.
        Args:
            path (str): GIF animation file path
        """
        with Image.open(path) as image:
            frames = [ImageTk.PhotoImage(frame.resize(self.pic_size, resample=Image.LANCZOS)) for frame in ImageSequence.Iterator(image)]
        self.image.append(frames)

    def update_frame(self, frame_index):
        """
        Cycles through animation frames.
        Args:
            frame_index (int): Current animation frame index
        """
        self.configure(image=self.image[1][frame_index])
        next_frame_index = (frame_index + 1) % len(self.image[1])
        self.start_update_frame = self.after(60, self.update_frame, next_frame_index)
    

