import pyautogui
import os
from colorbot import Colorbot
from settings import Settings
from colorama import init, Fore

class Main:
    def __init__(self):
        init(autoreset=True)
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

        self.settings = Settings()
        self.monitor = pyautogui.size()
        self.center_x, self.center_y = self.monitor.width // 2, self.monitor.height // 2
        self.x_fov = self.settings.get_int('Aimbot', 'xFov')
        self.y_fov = self.settings.get_int('Aimbot', 'yFov')

        self.colorbot = Colorbot(
            self.center_x - self.x_fov // 2, 
            self.center_y - self.y_fov // 2, 
            self.x_fov, 
            self.y_fov
        )

    def _init_logger(self):
        pass  # Falls du hier etwas hinzufügen möchtest, mach es gerne

    def run(self):
        os.system('cls')
        os.system('title github.com/iamennui/ValorantArduinoColorbot')
        print('Enemy Outline Color: Purple')
        self.colorbot.listen()

if __name__ == '__main__':
    Main().run()
