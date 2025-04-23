"""
DISCLAIMER:
This tool is for educational purposes only. Use at your own risk.
Unauthorized device spoofing may violate terms of service or laws.
The developer assumes no liability for misuse of this software.
"""

import os
import re
import time
import random
import requests
import zipfile
import subprocess
import win32com.client
from colorama import init, Fore, Style

init(autoreset=True)

class Spoofer:
    SKETCH_FILE = "arduino/arduino.ino"
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")

    def __init__(self):
        self.arduino_cli_path = os.path.join(os.getcwd(), "arduino/arduino-cli.exe")
        self.setup_directories()

    def setup_directories(self):
        try:
            os.makedirs("arduino", exist_ok=True)
        except OSError as e:
            self.exit_error(f"Failed to create directory: {e}")

    def exit_error(self, message, delay=10):
        print(f"{Fore.RED}[!] {message}")
        print(f"{Fore.YELLOW}Exiting in {delay} seconds...{Style.RESET_ALL}")
        time.sleep(delay)
        exit(1)

    def download_arduino_cli(self):
        if os.path.exists(self.arduino_cli_path):
            return

        zip_path = "arduino/arduino-cli.zip"
        if not os.path.exists(zip_path):
            try:
                print(f"{Fore.CYAN}[+] Downloading Arduino CLI...")
                response = requests.get(
                    "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip",
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()
                with open(zip_path, "wb") as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)
            except Exception as e:
                self.exit_error(f"Download failed: {e}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./arduino/")
            print(f"{Fore.GREEN}[+] Arduino CLI setup complete")
        except zipfile.BadZipFile:
            self.exit_error("Corrupted CLI zip file")

    def update_boards(self, vendor_id, product_id):
        if not os.path.exists(self.BOARDS_TXT_PATH):
            self.exit_error("boards.txt not found")

        try:
            with open(self.BOARDS_TXT_PATH, 'r') as f:
                lines = f.readlines()
        except IOError as e:
            self.exit_error(f"Error reading boards.txt: {e}")

        random_name = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))
        patterns = {
            r"leonardo\.name=": f"leonardo.name={random_name}\n",
            r"leonardo\.vid\.": f"{vendor_id}\n",
            r"leonardo\.pid\.": f"{product_id}\n",
            r"leonardo\.build\.vid=": f"leonardo.build.vid={vendor_id}\n",
            r"leonardo\.build\.pid=": f"leonardo.build.pid={product_id}\n",
            r"leonardo\.build\.usb_product=": f'leonardo.build.usb_product="{random_name}"\n'
        }

        for i, line in enumerate(lines):
            for pattern, replacement in patterns.items():
                if re.match(pattern, line):
                    lines[i] = replacement if "name" in pattern else line.split("=")[0] + f"={replacement}"

        try:
            with open(self.BOARDS_TXT_PATH, 'w') as f:
                f.writelines(lines)
        except IOError as e:
            self.exit_error(f"Error writing boards.txt: {e}")

    def detect_mice(self):
        try:
            wmi = win32com.client.GetObject("winmgmts:")
            devices = wmi.InstancesOf("Win32_PointingDevice")
            return [
                (dev.Name, *re.search(r'VID_(\w+)&PID_(\w+)', dev.PNPDeviceID).groups())
                for dev in devices if "USB" in dev.Name and dev.PNPDeviceID
            ]
        except Exception as e:
            self.exit_error(f"Device detection failed: {e}")

    def select_mouse(self):
        mice = self.detect_mice()
        if not mice:
            self.exit_error("No compatible mice detected")

        print(f"{Fore.YELLOW}[!] Detected USB devices:")
        unique_mice = list({(vid, pid): name for name, vid, pid in mice}.items())
        
        for i, ((vid, pid), name) in enumerate(unique_mice, 1):
            print(f"{Fore.CYAN}{i}: {name} {Fore.WHITE}(VID: {vid}, PID: {pid})")

        try:
            choice = int(input(f"\n{Fore.YELLOW}[?] Select mouse number: ")) - 1
            if 0 <= choice < len(unique_mice):
                return unique_mice[choice][0]
            raise ValueError
        except (ValueError, IndexError):
            self.exit_error("Invalid selection")

    def install_dependencies(self):
        try:
            core_check = subprocess.run(
                [self.arduino_cli_path, "core", "list"],
                capture_output=True, text=True, check=True
            )
            if "arduino:avr@1.8.6" not in core_check.stdout:
                print(f"{Fore.CYAN}[+] Installing AVR core...")
                subprocess.run(
                    [self.arduino_cli_path, "core", "install", "arduino:avr@1.8.6"],
                    capture_output=True, check=True
                )

            lib_check = subprocess.run(
                [self.arduino_cli_path, "lib", "list"],
                capture_output=True, text=True, check=True
            )
            if "Mouse" not in lib_check.stdout:
                print(f"{Fore.CYAN}[+] Installing Mouse library...")
                subprocess.run(
                    [self.arduino_cli_path, "lib", "install", "Mouse"],
                    capture_output=True, check=True
                )
        except subprocess.CalledProcessError as e:
            self.exit_error(f"Dependency install failed: {e.stderr}")

    def handle_sketch(self):
        com_port = input(f"{Fore.YELLOW}[?] Enter COM port (e.g. COM3): ").strip()
        if not re.match(r"^COM\d+$", com_port, re.IGNORECASE):
            self.exit_error("Invalid COM port format")

        try:
            print(f"{Fore.CYAN}[+] Compiling sketch...")
            subprocess.run(
                [self.arduino_cli_path, "compile", "--fqbn", "arduino:avr:leonardo", self.SKETCH_FILE],
                capture_output=True, check=True
            )
            
            print(f"{Fore.CYAN}[+] Uploading sketch...")
            subprocess.run(
                [self.arduino_cli_path, "upload", "-p", com_port, "--fqbn", "arduino:avr:leonardo", self.SKETCH_FILE],
                capture_output=True, check=True
            )
            print(f"{Fore.GREEN}[+] Spoof complete! Ready for use")
        except subprocess.CalledProcessError as e:
            self.exit_error(f"Sketch failed: {e.stderr.decode()}")

    def run(self):
        os.system("title Valorant Arduino Spoofer - github.com/ag7dev")
        os.system('cls')
        
        self.download_arduino_cli()
        self.install_dependencies()
        vid, pid = self.select_mouse()
        self.update_boards(f"0x{vid}", f"0x{pid}")
        self.handle_sketch()
        time.sleep(5)

if __name__ == "__main__":
    Spoofer().run()