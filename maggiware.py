import os
import sys
import time
import threading
import configparser

import cv2
import numpy as np
from mss import mss
import win32api

from colorama import init as init_color, Fore, Style
import logging

try:
    import serial
    try:
        SerialPort = serial.Serial
        SerialExc = serial.SerialException
    except AttributeError:
        from serial import Serial as SerialPort, SerialException as SerialExc
except ImportError:
    print(Fore.RED + "[!] pyserial is required. Install with 'pip install pyserial'.")
    sys.exit(1)

class MaggiWare:
    def __init__(self):
        init_color(autoreset=True)
        self._init_logger()

        try:
            os.system("title MaggiWare ~ ag7dev ~ github.com/ag7dev")
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as e:
            print(Fore.YELLOW + "[!] Could not set console title/clear: {}".format(e))

        logo = r'''

• ▌ ▄ ·.  ▄▄▄·  ▄▄ •  ▄▄ • ▪  ▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄  ▄▄▄ .
·██ ▐███▪▐█ ▀█ ▐█ ▀ ▪▐█ ▀ ▪██ ██· █▌▐█▐█ ▀█ ▀▄ █·▀▄.▀·
▐█ ▌▐▌▐█·▄█▀▀█ ▄█ ▀█▄▄█ ▀█▄▐█·██▪▐█▐▐▌▄█▀▀█ ▐▀▀▄ ▐▀▀▪▄
██ ██▌▐█▌▐█ ▪▐▌▐█▄▪▐█▐█▄▪▐█▐█▌▐█▌██▐█▌▐█ ▪▐▌▐█•█▌▐█▄▄▌
▀▀  █▪▀▀▀ ▀  ▀ ·▀▀▀▀ ·▀▀▀▀ ▀▀▀ ▀▀▀▀ ▀▪ ▀  ▀ .▀  ▀ ▀▀▀ 
Welcome to MaggiWare! Enjoy your stay.
        '''
        width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
        divider = "=" * width
        centered = "\n".join(line.center(width) for line in logo.splitlines())
        print(Fore.MAGENTA + divider)
        print(Fore.MAGENTA + centered)
        print(Fore.MAGENTA + divider)

        self.cfg_file = "settings.gay"
        self.cfg = configparser.ConfigParser()
        try:
            if not os.path.exists(self.cfg_file):
                self.cfg["Aimbot"] = {"fov": "100", "x_speed": "1.0", "y_speed": "1.0"}
                self.cfg["Connection"] = {"com_port": "COM3"}
                self.cfg["Keybinds"] = {"keybind": "0x02"}
                with open(self.cfg_file, "w") as f:
                    self.cfg.write(f)
            self.cfg.read(self.cfg_file)
        except Exception as e:
            self.log.error(Fore.RED + f"[!] Config load error: {e}")
            sys.exit(1)

        try:
            self.view_size = self.cfg.getint("Aimbot", "fov")
            self.horiz_factor = self.cfg.getfloat("Aimbot", "x_speed")
            self.vert_factor = self.cfg.getfloat("Aimbot", "y_speed")
            self.port = self.cfg.get("Connection", "com_port")
            self.trigger_key = int(self.cfg.get("Keybinds", "keybind"), 16)
            self.log.info(Fore.CYAN + f"[+] Loaded cfg: FOV={self.view_size}, Xf={self.horiz_factor}, Yf={self.vert_factor}")
        except Exception as e:
            self.log.error(Fore.RED + f"[!] Config parsing error: {e}")
            sys.exit(1)

        try:
            self.capture = mss()
            mon = self.capture.monitors[1]
            half = self.view_size // 2
            self.area = {"left": mon["width"]//2 - half,
                         "top": mon["height"]//2 - half,
                         "width": self.view_size,
                         "height": self.view_size}
        except Exception as e:
            self.log.error(Fore.RED + f"[!] Screen capture init error: {e}")
            sys.exit(1)

        self.hsv_lower = np.array([130, 80, 80])
        self.hsv_upper = np.array([165, 255, 255])

        self.ardu = None
        while True:
            try:
                self.ardu = SerialPort(self.port, 115200, timeout=1)
                self.log.info(Fore.GREEN + f"[+] Arduino connected on {self.port}")
                break
            except SerialExc as e:
                self.log.error(Fore.RED + f"[!] Cannot connect at {self.port}: {e}")
                self.port = input(Fore.YELLOW + "[?] Enter new COM port: ").strip()

        threading.Thread(target=self._aim_loop, daemon=True).start()
        threading.Thread(target=self._config_watcher, daemon=True).start()
        self._idle_loop()

    def _init_logger(self):
        self.log = logging.getLogger("MaggiWare")
        h = logging.StreamHandler(sys.stdout)
        fmt = f"{Fore.YELLOW}%(asctime)s{Style.RESET_ALL} | %(levelname)s | %(message)s"
        h.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
        self.log.addHandler(h)
        self.log.setLevel(logging.INFO)

    def _config_watcher(self):
        prev_time = os.path.getmtime(self.cfg_file)
        prev_vals = dict(self.cfg["Aimbot"])
        while True:
            time.sleep(1)
            try:
                curr_time = os.path.getmtime(self.cfg_file)
                if curr_time != prev_time:
                    self.cfg.read(self.cfg_file)
                    updates = []
                    for key, val in self.cfg["Aimbot"].items():
                        if prev_vals.get(key) != val:
                            updates.append(f"{key}: {prev_vals.get(key)} -> {val}")
                    if updates:
                        for u in updates:
                            self.log.info(Fore.CYAN + f"[+] Cfg changed: {u}")
                    prev_vals = dict(self.cfg["Aimbot"])
                    self.view_size = self.cfg.getint("Aimbot", "fov")
                    self.horiz_factor = self.cfg.getfloat("Aimbot", "x_speed")
                    self.vert_factor = self.cfg.getfloat("Aimbot", "y_speed")
                    half = self.view_size // 2
                    mon = self.capture.monitors[1]
                    self.area.update({"left": mon["width"]//2 - half,
                                      "top": mon["height"]//2 - half,
                                      "width": self.view_size,
                                      "height": self.view_size})
                    prev_time = curr_time
            except Exception as e:
                self.log.error(Fore.RED + f"[!] Config watcher error: {e}")

    def _send_move(self, dx, dy, dz):
        if self.ardu:
            try:
                msg = f"m{int(dx)},{int(dy)},{int(dz)}\n"
                self.ardu.write(msg.encode())
                self.log.debug(Fore.GREEN + f"[+] Sent move: {msg.strip()}")
            except Exception as e:
                self.log.error(Fore.RED + f"[!] Movement send error: {e}")

    def _aim_loop(self):
        center = self.view_size / 2
        kern = np.ones((5,5), np.uint8)
        while True:
            try:
                self.capture = mss()
                if win32api.GetAsyncKeyState(self.trigger_key) < 0:
                    frame = np.array(self.capture.grab(self.area))
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
                    dil = cv2.dilate(mask, kern, iterations=2)
                    cnts, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    best = None
                    best_dist = float('inf')
                    for c in cnts:
                        if cv2.contourArea(c) < 200:
                            continue
                        pt = min((tuple(p[0]) for p in c), key=lambda p: p[1])
                        dist = np.hypot(pt[0]-center, pt[1]-center)
                        if dist < best_dist:
                            best_dist, best = dist, pt
                    if best:
                        x_move = (best[0]-center)*self.horiz_factor + 5
                        y_move = (best[1]-center)*self.vert_factor + 6
                        self._send_move(x_move, y_move, 1)
                        cv2.circle(frame, best, 5, (0,255,0), -1)
            except Exception as e:
                self.log.error(Fore.RED + f"[!] Aim loop error: {e}")
            time.sleep(0.01)

    def _idle_loop(self):
        self.log.info(Fore.CYAN + "[+] Idle. Press trigger to aim.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log.info(Fore.YELLOW + "[!] Exiting MaggiWare.")
            sys.exit(0)

if __name__ == "__main__":
    MaggiWare()
