import os
import numpy as np
from pathlib import Path
from PIL import Image,ImageTk
from tkinter import filedialog

initial_dir = Path(__file__).resolve().parent.parent

class Floorplan_Processor:
    
    def __init__(self):
        # 
        self.valid_positions = None
        self.extent_x = None
        self.extent_y = None
        self.floorplan = None
        self.floorplan_path_json = None
    
    def process_image(self):
        floorplan_path = filedialog.askopenfilename(initialdir=initial_dir,title="Select File from UWB_WebMap\\public Directory",filetypes=(("PNG files", "*.png"),))
        self.floorplan_path_json = "/"+os.path.basename(floorplan_path)
        self.floorplan = Image.open(floorplan_path)
        self.extent_x = self.floorplan.size[0]
        self.extent_y = self.floorplan.size[1]
        self.create_valid_pixels()
        self.save_valid_positions()
        
    def create_valid_pixels(self):
        arr = np.array(self.floorplan)        
        colors = [(0,0,0,255), (255,255,255,0)]
        mask = np.any([np.all(arr == c, axis=-1) for c in colors], axis=0)
        #y_indices, x_indices = np.where(mask)
        true_y,true_x = np.where(~mask)
        self.valid_positions = np.column_stack((true_x, true_y))
     
    def save_valid_positions(self, path="valid_positions.npy"):
        np.save(path, self.valid_positions)
    


if __name__ =="__main__":
    prz = Floorplan_Processor()
    prz.process_image()
    prz.save_valid_positions()
 
    

