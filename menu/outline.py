import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils import Button
import numpy as np
import cv2


class Outline_Menu(ttk.Frame):
    def __init__(
            self, 
            master: ttk.Frame, 
            root: ttk.Frame,
            ) -> None:
        super().__init__(master=master)
        
        self.root = root
        self.master = master
        self.viewer = root.viewer
        self.pic_range = None
        
        self.style = ttk.Style()
        self.style.configure("Chosen.TButton", background="white", bordercolor="#17a2b8", padding=2, relief="solid")

        self.add_b = Button(
            master=self, 
            icons=r'icons\add-outline',
            annotation='Add (CTRL + Left Click)',
            command=self.add_chosen
        )
        self.add_b.pack(side=LEFT, padx=5, pady=5)
        
        self.del_b = Button(
            master=self, 
            icons=r'icons\del-outline',
            annotation='Delete (CTRL + Right Click)',
            command=self.del_chosen
        )
        self.del_b.pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)
        
        self.drag_b = Button(
            master=self, 
            icons=r'icons\drag',
            annotation='Drag (ALT + Left Click)',
            command=self.drag_chosen
        )
        self.drag_b.pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)

        self.zoom_b = Button(
            master=self, 
            icons=r'icons\zoom',
            annotation='Zoom into Area (ALT + Right Click)',
            command=self.zoom_chosen
        )
        self.zoom_b.pack(side=LEFT, padx=5, pady=5)
        Button(
            master=self, 
            icons=r'icons\zoom-in',
            annotation='Zoom in (ALT + Mouse Wheel)',
            command=self.zoom_in
        ).pack(side=LEFT, padx=5, pady=5)
        Button(
            master=self, 
            icons=r'icons\zoom-out',
            annotation='Zoom out (ALT + Mouse Wheel)',
            command=self.zoom_out
        ).pack(side=LEFT, padx=5, pady=5)

        ttk.Separator(self, orient='vertical').pack(side=LEFT, padx=10, pady=5)

        self.chosen_b = None
        self.chosen_func = None
        self.contour = []
        self.add_keys = ["<B1-Motion>", "<ButtonRelease-1>"]
        self.del_keys = ["<B3-Motion>", "<ButtonRelease-3>"]
        self.drag_keys = ["<B1-Motion>", "<ButtonRelease-1>"]
        self.zoom_keys = ["<B3-Motion>", "<ButtonRelease-3>"]

        self.drag_chosen()

    ### button function ###
    def zoom_wheel(self, event):
        """
        Handles zooming via mouse wheel with center-point preservation.
        """
        self.viewer.canvas.unbind("<MouseWheel>")
        x, y = self.get_point(event)
        h, w = self.viewer.img_backup.shape[:2]
        zoom = 1.1 ** (event.delta//120)
        l, t, r, b = self.viewer.pic_range
        l, t = max(int(x-(x-l)*zoom), 0), max(int(y-(y-t)*zoom), 0) 
        r, b = min(int(x+(r-x)*zoom), h), min(int(y+(b-y)*zoom), w)
        self.viewer.show_image(pic_range=[l, t, r, b])
        self.viewer.canvas.bind("<MouseWheel>", self.zoom_wheel)
    def zoom_in(self):
        """
        Zooms in the image view by 10% centered on current view.
        """
        h, w = self.viewer.img_backup.shape[:2]
        zoom = 0.9
        l, t, r, b = self.viewer.pic_range
        x, y = (l+r)//2, (t+b)//2
        l, t = max(int(x-(x-l)*zoom), 0), max(int(y-(y-t)*zoom), 0) 
        r, b = min(int(x+(r-x)*zoom), h), min(int(y+(b-y)*zoom), w)
        self.viewer.show_image(pic_range=[l, t, r, b])
    def zoom_out(self):
        """
        Zooms out the image view by 10% centered on current view.
        """
        h, w = self.viewer.img_backup.shape[:2]
        zoom = 1.1
        l, t, r, b = self.viewer.pic_range
        x, y = (l+r)//2, (t+b)//2
        l, t = max(int(x-(x-l)*zoom), 0), max(int(y-(y-t)*zoom), 0) 
        r, b = min(int(x+(r-x)*zoom), h), min(int(y+(b-y)*zoom), w)
        self.viewer.show_image(pic_range=[l, t, r, b])

    def drag_chosen(self):
        """
        Activates image dragging mode.
        """
        self.chosen(mod='drag')
    def drag_tap(self, event):
        """
        Initializes drag operation starting point.
        """
        self.viewer.canvas.unbind('<Motion>')
        self.drag_x, self.drag_y = self.get_point(event)
        self.drag_func = [self.viewer.canvas.bind(i) for i in self.drag_keys]
        self.pic_range = self.viewer.pic_range
        
        self.viewer.canvas.bind(self.drag_keys[0], self.drag_mov)
        self.viewer.canvas.bind(self.drag_keys[1], self.drag_rls)
    def drag_mov(self, event):
        """
        Updates image position during drag operation.
        """
        x, y = self.get_point(event)
        l, t, r, b = self.pic_range
        width, height = self.viewer.img_backup.shape[:2]
        x, y = min(max(self.drag_x-x, -l), width-r), min(max(self.drag_y-y, -t), height-b)
        self.viewer.pic_range = [l+x, t+y, r+x, b+y]
        self.viewer.draw_contour()
    def drag_rls(self, event):
        """
        Finalizes drag operation and cleans up event bindings.
        """
        self.viewer.canvas.bind(self.drag_keys[0], self.drag_func[0])
        self.viewer.canvas.bind(self.drag_keys[1], self.drag_func[1])
        self.drag_x, self.drag_y, self.drag_func, self.pic_range = None, None, None, None

    def zoom_chosen(self):
        """
        Activates rectangular zoom selection mode.
        """
        self.chosen('zoom')
    def zoom_tap(self, event):
        """
        Initializes zoom rectangle starting point.
        """
        self.viewer.canvas.unbind('<Motion>')
        self.zoom_x, self.zoom_y = self.get_point(event)
        self.zoom_func = [self.viewer.canvas.bind(i) for i in self.zoom_keys]
        
        self.viewer.canvas.bind(self.zoom_keys[0], self.zoom_mov)
        self.viewer.canvas.bind(self.zoom_keys[1], self.zoom_rls)
    def zoom_mov(self, event):
        """
        Updates zoom rectangle during mouse movement.
        """
        x, y = self.get_point(event)
        self.viewer.draw_contour(zoom_range=[self.zoom_x, self.zoom_y, x, y])
    def zoom_rls(self, event):
        """
        Applies zoom to selected area and cleans up event bindings.
        """
        x, y = self.get_point(event)

        self.viewer.show_image(pic_range=[min(x, self.zoom_x), min(y, self.zoom_y), max(x, self.zoom_x), max(y, self.zoom_y)])

        self.viewer.canvas.bind('<Motion>', self.show_cross)
        self.viewer.canvas.bind(self.zoom_keys[0], self.zoom_func[0])
        self.viewer.canvas.bind(self.zoom_keys[1], self.zoom_func[1])
        self.zoom_x, self.zoom_y, self.zoom_func = None, None, None

    def add_chosen(self):
        """
        Activates contour addition mode.
        """
        self.chosen(mod='add')
    def add_tap(self, event):
        """
        Starts new contour at clicked position.
        """
        self.root.change.set(1)
        x, y = self.get_point(event)
        self.contour.append([[x, y]])

        self.add_func = [self.viewer.canvas.bind(i) for i in self.add_keys]
        self.viewer.canvas.bind(self.add_keys[0], self.add_mov)
        self.viewer.canvas.bind(self.add_keys[1], self.add_rls)
    def add_mov(self, event):
        """
        Draws temporary contour during mouse movement.
        """
        x, y = self.get_point(event)
        self.contour.append([[x, y]])

        self.viewer.draw_contour(add_mask=[np.array(self.contour)])
    def add_rls(self, event):
        """
        Finalizes contour addition and updates mask.
        """
        x, y = self.get_point(event)
        self.contour.append([[x, y]])
        
        msk = self.viewer.mask[self.viewer.crt_index.get()].copy()
        draw = np.zeros(msk.shape, dtype=np.uint8)
        cv2.fillPoly(draw, [np.array(self.contour)], 1)
        msk[draw==1] = 1
        self.viewer.mask[self.viewer.crt_index.get()] = msk.astype(np.uint8)

        self.viewer.show_image()
        self.viewer.canvas.bind(self.add_keys[0], self.add_func[0])
        self.viewer.canvas.bind(self.add_keys[1], self.add_func[1])
        self.contour = []
        
    def del_chosen(self):
        """
        Activates contour deletion mode.
        """
        self.chosen(mod='del')
    def del_tap(self, event):
        """
        Starts deletion area at clicked position.
        """
        self.root.change.set(1)
        x, y = self.get_point(event)
        self.contour.append([[x, y]])

        self.del_func = [self.viewer.canvas.bind(i) for i in self.del_keys]
        self.viewer.canvas.bind(self.del_keys[0], self.del_mov)
        self.viewer.canvas.bind(self.del_keys[1], self.del_rls)
    def del_mov(self, event):
        """
        Draws temporary deletion area during mouse movement.
        """
        x, y = self.get_point(event)
        self.contour.append([[x, y]])

        self.viewer.draw_contour(del_mask=[np.array(self.contour)])
    def del_rls(self, event):
        """
        Finalizes contour deletion and updates mask.
        """
        x, y = self.get_point(event)
        self.contour.append([[x, y]])
        
        msk = self.viewer.mask[self.viewer.crt_index.get()].copy()
        draw = np.zeros(msk.shape, dtype=np.uint8)
        cv2.fillPoly(draw, [np.array(self.contour)], 1)
        msk[draw==1] = 0
        self.viewer.mask[self.viewer.crt_index.get()] = msk.astype(np.uint8)

        self.viewer.show_image()
        self.viewer.canvas.bind(self.del_keys[0], self.del_func[0])
        self.viewer.canvas.bind(self.del_keys[1], self.del_func[1])
        self.contour = []
        

    ### utilitarian fuction ###
    def get_point(self, event):
        """
        Converts screen coordinates to image coordinates.
        """
        pic_range = self.viewer.pic_range if self.pic_range is None else self.pic_range
        pic_ratio = self.viewer.pic_ratio
        x, y = round((event.x-self.viewer.b_width)*pic_ratio), round((event.y-self.viewer.b_height)*pic_ratio)
        x, y = x + pic_range[0], y + pic_range[1]
        x, y = min(max(x, 0), self.viewer.img_backup.shape[0]-1), min(max(y, 0), self.viewer.img_backup.shape[1]-1)
        return x, y
    
    def show_cross(self, event):
        """
        Displays crosshair at current mouse position.
        """
        x, y = self.get_point(event)
        self.viewer.draw_contour(cross_loc=[x, y])

    def chosen(self, mod):
        """
        Manages tool selection state and event bindings.
        """
        if mod in ["add", self.add_b]:
            button, func = self.add_b, self.add_tap
        elif mod in ["del", self.del_b]:
            button, func = self.del_b, self.del_tap
            self.del_keys = ["<B1-Motion>", "<ButtonRelease-1>"]
        elif mod in ["drag", self.drag_b]: 
            button, func = self.drag_b, self.drag_tap
        elif mod in ["zoom", self.zoom_b]:
            self.viewer.canvas.bind('<Motion>', self.show_cross)
            button, func = self.zoom_b, self.zoom_tap
            self.zoom_keys = ["<B1-Motion>", "<ButtonRelease-1>"]

        if self.chosen_b is not None:
            self.chosen_b.config(style="Custom.TButton")
            self.viewer.canvas.bind(*self.chosen_func)
        if self.chosen_b == button and mod != 'drag':
            self.chosen_b=None
            self.chosen_func = None
            self.del_keys = ["<B3-Motion>", "<ButtonRelease-3>"]
            self.zoom_keys = ["<B3-Motion>", "<ButtonRelease-3>"]
        else:
            if mod in ["zoom", self.zoom_b]: self.viewer.canvas.bind('<Motion>', self.show_cross)
            if self.chosen_b in ["zoom", self.zoom_b]: self.viewer.canvas.unbind('<Motion>')
            button.config(style="Chosen.TButton")
            self.chosen_b = button
            self.chosen_func = ["<Button-1>", self.viewer.canvas.bind("<Button-1>")]
            self.viewer.canvas.bind('<Button-1>', func)
            try:
                self.viewer.show_image()
            except:
                pass
