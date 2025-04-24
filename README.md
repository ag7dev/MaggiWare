[![Discord]()]()
# Arduino Colorbot for Valorant

## 📹 Preview

[https://streamable.com/xwlera]

## 📝 Project Description

This project is a Colorbot designed for the game Valorant. It uses computer vision techniques to detect enemy outlines based on color and automatically aims by sending movement commands to an Arduino Leonardo board. The bot captures a portion of the screen, processes the image to detect specific purple hues (enemy outlines), and moves the mouse via the Arduino to assist aiming. This version is an older public release, used successfully for 6 months without bans. A private, more precise, and undetected version is available via the Discord server.

## ✨ Features

- Real-time screen capture and color detection using OpenCV and MSS.
- HSV color filtering to detect enemy outlines (purple color range).
- Sends precise movement commands to Arduino Leonardo via serial communication.
- Configurable field of view (FOV), aiming speed, and keybinds via settings file.
- Dynamic configuration reloading without restarting the bot.
- Simple command-line interface with logging and status messages.

## ⚙️ Prerequisites

- **Hardware**:
  - Arduino Leonardo board (required).
  - USB Host Shield for Arduino (required).
  - External power source for Arduino to prevent bootloader issues.
- **Software**:
  - Python 3.x installed.
  - Python packages: `pyserial`, `mss`, `opencv-python`, `numpy`, `colorama`, `pywin32`.
  - Windows OS (due to use of win32api for key detection).

## 🛠️ Setup Instructions

1. **Arduino Spoofing**:
   - Spoof your Arduino Leonardo's USB VID and PID to match your mouse's to bypass Valorant's single input restriction.
   - Ensure your Arduino has an external power source to avoid bootloader resets.

2. **Install Python Dependencies**:
   Run the following command to install required packages:
   ```bash
   pip install pyserial mss opencv-python numpy colorama pywin32
   ```

3. **Configure `settings.gay`**:
   - The bot uses a configuration file named `settings.gay`.
   - Adjust parameters such as:
     - `fov`: Field of view size for screen capture (default 100).
     - `x_speed` and `y_speed`: Horizontal and vertical aiming speed factors.
     - `com_port`: COM port where Arduino is connected (e.g., COM3).
     - `keybind`: Hex code of the key to trigger aiming (default 0x02).
   - The bot automatically reloads configuration changes during runtime.

4. **Run the Colorbot**:
   Launch the bot by running:
   ```bash
   py main.py
   ```

5. **In-Game Settings**:
   - Recommended in-game sensitivity: **0.45**.
   - Set enemy outline color to **Purple** for best detection.

## 🧑‍💻 How It Works

- The bot captures a square area of the screen centered on the monitor.
- Converts the captured image to HSV color space and filters for purple hues.
- Detects contours of filtered areas and selects the closest target based on position.
- Calculates movement deltas scaled by configured speed factors.
- Sends movement commands to the Arduino via serial port to move the mouse.
- The aiming is triggered by holding down the configured keybind.

## ⚠️ Disclaimer and Notes

- This software is intended for educational purposes only.
- Use at your own risk; the author is not responsible for any bans or penalties.
- Compatible only with Arduino Leonardo boards and requires a USB Host Shield.
- Always ensure your Arduino is properly powered to avoid bootloader issues.
- You also NEED a external power source for your Arduino so its not going in the bootloader.

## 💬 Support

For help, updates, and to purchase the private version, join the Discord server:

[Discord Invite Link]()
