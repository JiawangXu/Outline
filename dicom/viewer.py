import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
from utils import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pydicom
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

class Viewer(ttk.Frame):
    def __init__(
            self, 
            master: ttk.Frame,
            root: ttk.Frame,
        ):
        super().__init__(master=master)
        
        self.root = root
        self.master = master
        self.change = root.change
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.red = (249, 120, 140)
        self.yellow = (255, 255, 40)

        self.dicom_paths = None
        
        # slider bar
        self.crt_index = ttk.IntVar()
        self.slider_para = {
            'master': self,
            'from_': 0,
            'to': 100,
            'variable': self.crt_index,
            'orient': ttk.VERTICAL,
            'command': self.move,
            'bootstyle': INFO,
        }
        self.slider = ttk.Scale(**self.slider_para)
        self.slider.grid(row=0, column=1, sticky="nsew")

        self.canvas_frame = ttk.Frame(
            master=self,
        )
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas = ttk.Label(
            master = self.canvas_frame,
        )
        self.canvas.pack(fill=BOTH, expand=True)

        # parameters
        self.data_path = None
        self.save_path = root.save_path
        self.mask_files = None
        self.e_x, self.e_y = None, None
        self.pic_ratio = None
        self.pic_range = [0, 0, -1,-1] # left, top, right, bottom
        self.mdf = {}

    ### button bind ###
    def buttons(self):
        return [
            [None, '<Up>', self.move_slider],
            [None, '<Down>', self.move_slider],
            [None, '<Control-s>', self.save_msk],
            [self.canvas, "<B2-Motion>", self.canvas_event],
            [self.canvas, "<ButtonRelease-2>", self.release_event],
            [self.canvas, "<MouseWheel>", self.move_slider],
        ]

    ### initial function ###
    def set_modify(self, page):
        self.modify_page = page
        
    def set_check(self, page):
        self.check_page = page


    ### button function ###
    def canvas_event(self, event):
        if self.e_x is not None:
            self.data['ww'] = max(self.data['ww'] + event.x - self.e_x, 1)
            self.data['wc'] += self.e_y - event.y
            self.show_image()
        self.e_x, self.e_y = event.x, event.y

    def release_event(self, event):
        self.mdf['wcww'] = 1
        self.change.set(1)
        self.e_x, self.e_y = None, None

    def move_slider(self, event):
        self.canvas.unbind("<MouseWheel>")
        current_value = self.crt_index.get()
        if event.keysym == 'Up':
            new_value = max(current_value - 1, 0)
        elif event.keysym == 'Down':
            new_value = min(current_value + 1, len(self.dicom_paths)-1)
        else:
            new_value = max(0, min(current_value-event.delta//120, len(self.dicom_paths)-1))
        self.slider.config(bootstyle=SUCCESS if self.img_range[0]<=new_value<=self.img_range[1] else DANGER)
        self.crt_index.set(new_value)
        self.show_image()
        self.canvas.bind("<MouseWheel>", self.move_slider)

    def move(self, value):
        value = round(float(value))
        self.slider.config(bootstyle=SUCCESS if self.img_range[0]<=value<=self.img_range[1] else DANGER)
        self.crt_index.set(value)
        self.show_image()

    def save_msk(self, *args):
        image = np.array([self.get_raw_image(i)[:, :, 0] for i in self.dicom_paths])
        np.savez(f"{self.save_path}/{self.data['name']}.npz", image=image, mask=self.mask, ww=self.data['ww'], wc=self.data['wc'])


    ### core function ###
    def get_raw_image(self, filepath=None):
        dicom_slice = pydicom.dcmread(self.dicom_paths[self.crt_index.get()] if filepath is None else filepath)
        
        not_save_tag = ['Pixel Data']
        encodetype = dicom_slice[0x00080005].value if 0x00080005 in dicom_slice else None
        self.annotation = get_annotation(dicom_slice, encodetype, not_save_tag)

        img = np.array(dicom_slice.pixel_array, dtype=np.float64)
        
        try:
            itcp = self.annotation['00281052']['value']
            slope = self.annotation['00281053']['value']
            img = img * slope + itcp
        except:
            pass

        if filepath is None:
            self.show_annotation(self.annotation)
            if 'ww' in self.data and 'wc' in self.data:
                ww, wc = self.data['ww'], self.data['wc']
            else:
                ww, wc = self.annotation['00281051']['value'], self.annotation['00281050']['value']
                ww, wc = ww[0] if isinstance(ww, list) else ww, wc[0] if isinstance(wc, list) else wc
                self.data['ww'], self.data['wc'] = ww, wc
        elif not hasattr(self, 'data'):
            ww, wc = self.annotation['00281051']['value'], self.annotation['00281050']['value']
            ww, wc = ww[0] if isinstance(ww, list) else ww, wc[0] if isinstance(wc, list) else wc
        else:
            ww, wc = self.data['ww'], self.data['wc']
        img_min = wc - ww // 2
        img_max = wc + ww // 2
        img[img < img_min] = img_min
        img[img > img_max] = img_max
        img = (img - np.min(img))  * 255 // (np.max(img) - np.min(img))

        self.dicom_data = dicom_slice
        img = np.squeeze(img.astype(np.uint8))
        return np.stack([img, img, img], axis=-1)
    
    def set_base_tags(self, img=None, padding=8):
        img = img if img is not None else self.img.copy()
        fontheight = min(self.canvas_frame.winfo_height(), self.canvas_frame.winfo_width()) // 30
        padding = min(self.canvas_frame.winfo_height(), self.canvas_frame.winfo_width()) // 80
        font = ImageFont.truetype(r"msyh.ttc", fontheight)

        decode_func = lambda x: self.annotation[x]['value']

        positions = {
            'nw': 0,
            'ne': 0,
            'sw': img.shape[0] - padding,
            'se': img.shape[0] - padding, 
        }
        def get_text_position(t, pst):
            text_size = font.getmask(text).size
            if pst == 'nw':
                text_position = [padding, positions[pst]]
                positions[pst] = positions[pst] + text_size[1] + padding
            elif pst == 'ne':
                text_position = [img.shape[1] - text_size[0] - padding, positions[pst]]
                positions[pst] = positions[pst] + text_size[1] + padding
            elif pst == 'sw':
                positions[pst] = positions[pst] - text_size[1] - padding
                text_position = [padding, positions[pst]]
            elif pst == 'se':  
                positions[pst] = positions[pst] - text_size[1] - padding
                text_position = [img.shape[1] - text_size[0] - padding, positions[pst]]
              
            return text_position
                
        all_text = []
        ww, wc = self.data['ww'], self.data['wc']
        
        text_to_check = [
            (   None, 
                lambda v1: f'Im:{self.crt_index.get()+1}/{len(self.dicom_paths)}', 
                self.red, 'nw'),
            (   ['00200011'], 
                lambda v1: f'Se:{decode_func(v1)}', 
                self.yellow, 'nw'),
            (   ['00180050', '00201041'], 
                lambda v1, v2: f'T:{float(decode_func(v1))}mm L:{float(decode_func(v2))}', 
                self.yellow, 'sw'),
            (   None, 
                lambda v1: f'WW:{ww} WC:{wc}', 
                self.red, 'sw'),
            (   ['00100020'], 
                lambda v1: f'{decode_func(v1)}', 
                self.yellow, 'ne'),
            (   ['00101001', '00100040'], 
                lambda v1, v2: f'{decode_func(v1)}  {"女" if decode_func(v2)=="F" else "男"}', 
                self.yellow, 'ne'),
            (   ['00100010'], 
                lambda v1: f'{decode_func(v1)}', 
                self.yellow, 'ne'),
            (   ['00100030'], 
                lambda v1: f'{self.unify_date_format(decode_func(v1))}', 
                self.yellow, 'ne'),
            (   ['00080080'], 
                lambda v1: f'{decode_func(v1)}', 
                self.yellow, 'ne'),
            (   ['00200010'], 
                lambda v1: f'{decode_func(v1)}', 
                self.yellow, 'ne'),
            (   ['0008103e'], 
                lambda v1: f'{decode_func(v1)}', 
                self.yellow, 'ne'),
            (   ['00400244', '00400245'], 
                lambda v1, v2: f'{self.unify_date_format(decode_func(v1))} {self.unify_date_format(decode_func(v2), sep=":")}', 
                self.yellow, 'se'),
        ]

        for item_id, process_func, *args in text_to_check:
            if item_id is None:
                all_text.append([process_func(0), *args])
            elif all(element in self.annotation.keys() for element in item_id):
                all_text.append([process_func(*item_id), *args])

        image = Image.fromarray(img)
        draw = ImageDraw.Draw(image)
        for text, color, position in all_text:
            draw.text(get_text_position(text, position), text, font=font, fill=color)
        return np.array(image)

    def show_image(self, pic_range=None):

        self.drawing = False
        img = self.get_raw_image()
        
        msk = self.mask[self.crt_index.get()].copy()
        if np.sum(msk):
            contours, _ = cv2.findContours(msk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img, contours, -1, (255, 255, 0), 1)

        self.img_backup = img.copy()
        self.image = self.resize(img, pic_range=pic_range)
        self.image = self.set_base_tags(self.image)
        self.image = ImageTk.PhotoImage(Image.fromarray(self.image))
        self.canvas.config(image=self.image)

    def draw_contour(self, add_mask=None, del_mask=None, zoom_range=None, pic_range=None, cross_loc=None):

        if hasattr(self, "drawing") and self.drawing:
            return
        self.drawing = True  # 标记正在绘制

        img = self.img_backup.copy()

        if add_mask is not None:
            cv2.drawContours(img, add_mask, -1, (0, 255, 0), 1)
        elif del_mask is not None:
            cv2.drawContours(img, del_mask, -1, (255, 0, 0), 1)
        elif zoom_range is not None:
            x1, y1, x2, y2 = zoom_range
            drawline(img, (x1, y1), (x2, y1), (0, 255, 0))
            drawline(img, (x2, y1), (x2, y2), (0, 255, 0))
            drawline(img, (x2, y2), (x1, y2), (0, 255, 0))
            drawline(img, (x1, y2), (x1, y1), (0, 255, 0))
        elif cross_loc is not None:
            x, y = cross_loc
            cv2.line(img, (x, 0), (x, img.shape[1]), (0, 255, 0), 1, cv2.LINE_8)
            cv2.line(img, (0, y), (img.shape[0], y), (0, 255, 0), 1, cv2.LINE_8)

        img = self.resize(img, pic_range=pic_range)
        
        if self.drawing:
            img = self.set_base_tags(img)
            self.image = ImageTk.PhotoImage(Image.fromarray(img))
            self.canvas.config(image=self.image)

            self.drawing = False
    
    def openserie(self, *args):
        if self.root.all_data is not None:

            filename = self.root.filename.get()
            self.data = self.root.all_data[filename]
            self.master.configure(text=filename)

            self.dicom_paths, self.mask_path = self.data['dicom'], self.data['mask']
            if os.path.exists(f"{self.save_path}/{self.data['name']}.npz"):
                file = np.load(f"{self.save_path}/{self.data['name']}.npz")
                self.mask, self.data['ww'], self.data['wc'] = file['mask'], file['ww'], file['wc']
                self.img_range = get_mask_range(self.mask)
            elif isinstance(self.mask_path, str):
                self.mask, record = read_mask(self.mask_path)
                self.img_range = get_mask_range(self.mask)
                self.data.update(record)
            else:
                self.mask = np.zeros([len(self.dicom_paths)-1, self.data["thumbnail"].shape[0], self.data["thumbnail"].shape[1]])
                self.img_range = (0, len(self.dicom_paths)-1)
            self.crt_index.set(self.img_range[0])
            self.rvs = 0
            self.is_change = False

            self.slider.config(to=len(self.dicom_paths)-1, bootstyle=SUCCESS)
            self.pic_range = [0, 0, -1,-1]
            self.show_image()

    ### utilitarian function ###
    def resize(self, img: np.ndarray, pic_range=None):
        self.canvas_frame.update()
        width, height = self.canvas_frame.winfo_width(), self.canvas_frame.winfo_height()
        
        l, t, r, b = self.pic_range if pic_range is None else pic_range
        b = img.shape[0] if b==-1 else b
        r = img.shape[1] if r==-1 else r

        pic_ratio = max((b-t)/height, (r-l)/width)
        self.pic_ratio = pic_ratio
        img = np.array(cv2.resize(img.copy(), None, fx=1/pic_ratio, fy=1/pic_ratio))
        l, t = max(0, int(((r+l)/pic_ratio-width)/2)), max(0, int(((b+t)/pic_ratio-height)/2))
        r, b = min(img.shape[1], int(((r+l)/pic_ratio+width)/2), width+l), min(img.shape[0], int(((b+t)/pic_ratio+height)/2), height+t)
        img = img[t:b, l:r]

        image = np.zeros([height, width, 3], dtype=np.uint8)
        height, width = (height-img.shape[0])//2, (width-img.shape[1])//2
        self.b_height, self.b_width = height, width
        image[height:height+img.shape[0], width:width+img.shape[1]] = img

        self.pic_range = [round(i*pic_ratio) for i in [l, t, r, b]]

        return image

    def check_save(self, filepath):
        
        new_window = ttk.Toplevel()
        new_window.grab_set()
        new_window.title('输入窗口')
        # 计算居中位置
        x = self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - new_window.winfo_reqwidth() // 2
        y = self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - new_window.winfo_reqheight() // 2
        new_window.geometry(f"+{x}+{y}")

        ttk.Label(new_window, text='文件未保存').grid(row=0, column=1, pady=10)

        def confirm():
            self.save_msk()
            new_window.destroy()
            new_window.grab_release()
            
        def refuse():
            self.change.set(0)
            self.openserie(filepath)
            new_window.destroy()
            new_window.grab_release()

        def cancel():
            new_window.destroy()
            new_window.grab_release()

        confirm_button = ttk.Button(new_window, text="保存", command=confirm)
        confirm_button.grid(row=1, column=0, padx=10, pady=10)

        confirm_button = ttk.Button(new_window, text="不保存", command=refuse)
        confirm_button.grid(row=1, column=1, padx=10, pady=10)

        confirm_button = ttk.Button(new_window, text="取消", command=cancel)
        confirm_button.grid(row=1, column=2, padx=10, pady=10)

    def insert_data(self, data, parent='', parentiid='0x'):
        for idx, item in enumerate(data.values()):
            if parent == '':
                iid = parentiid + rearrange_numbers(str(item['tag']))
            else:
                iid = parentiid + hex(idx)
            values =(item['tag'], item['name'], item['value'])
            child = self.root.annotation.insert(parent, "end", iid=iid, text=item['tag'], values=values)

            if "children" in item:
                self.insert_data(item["children"], child, iid)

    def show_annotation(self, datas):
        current_selection = self.root.annotation.selection()
        chidren = self.root.annotation.get_children('')
        flag = False
        if len(current_selection) != 0:
            idx = chidren.index(current_selection[0][:10])
            idx -= self.root.annotation.yview()[0] * len(chidren)
            flag=True

        # delete origin data
        self.root.annotation.delete(*chidren)
        # load new data
        self.insert_data(datas)

        if len(current_selection) == 0:
            current_selection = self.root.annotation.get_children()[0]
        else:
            current_selection = current_selection[0][:10]
            if current_selection not in self.root.annotation.get_children():
                closest_element = None
                min_difference = float('inf')
                for element in self.root.annotation.get_children():
                    element = element[:10]
                    encoded_element = eval(element)
                    difference = abs(eval(current_selection) - encoded_element)
                    if difference < min_difference:
                        min_difference = difference
                        closest_element = element
                current_selection = closest_element
        self.root.annotation.selection_set(current_selection)
        if flag:
            chidren = self.root.annotation.get_children('')
            idx = chidren.index(current_selection) - idx
            self.root.annotation.yview_moveto(idx/len(chidren))
    
    @staticmethod
    def unify_date_format(date_string, sep='/'):
        sep_char = []
        for char in date_string:
            if not char.isdigit():
                sep_char.append(char)
        for char in sep_char:
            date_string = ''.join(date_string.split(char))
        a, b, c = date_string[:-4], date_string[-4:-2], date_string[-2:]
        return sep.join([a, b, c])
    