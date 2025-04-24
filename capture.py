import numpy as np
from mss import mss

class Capture:
    def __init__(self, x, y, x_fov, y_fov):
        self.monitor = {
            "top": y,
            "left": x,
            "width": x_fov,
            "height": y_fov
        }
        
    def get_screen(self):
        with mss() as sct:
            screenshot = sct.grab(self.monitor)
            return np.array(screenshot)
