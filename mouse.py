import time
import threading
import serial
import serial.tools.list_ports
from settings import Settings
from colorama import init, Fore

init(autoreset=True)

class Mouse:
    def __init__(self):
        self.settings = Settings()
        self.lock = threading.Lock()
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.timeout = 0
        self.serial_port.port = self.find_serial_port()
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        try:
            self.serial_port.open()
        except serial.SerialException:
            print(Fore.YELLOW + "[!] Colorbot is already open or Arduino is being used by another app.\nExiting in 10 seconds...")
            time.sleep(10)
            exit()

    def find_serial_port(self):
        com_port = self.settings.get('Settings', 'COM-Port')
        port = next((port for port in serial.tools.list_ports.comports() if com_port in port.description), None)
        if port is not None:
            return port.device
        else:
            print(Fore.RED + "[!] Unable to detect your specified Arduino ({})\nPlease check its connection and the settings.gay file, then try again.\nExiting in 10 seconds...".format(com_port))
            time.sleep(10)
            exit()

    def move(self, x, y):
        x += self.remainder_x
        y += self.remainder_y

        move_x = int(x)
        move_y = int(y)
        self.remainder_x = x - move_x
        self.remainder_y = y - move_y

        if move_x != 0 or move_y != 0:
            with self.lock:
                self.serial_port.write(f'M{move_x},{move_y}\n'.encode())

    def click(self):
        with self.lock: 
            self.serial_port.write('C\n'.encode())
