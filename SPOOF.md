# How to Spoof Arduino and Raspberry Pi USB Devices

This guide explains how to spoof USB device identifiers for Arduino and Raspberry Pi boards, allowing them to mimic other USB devices such as a mouse. It also includes instructions on how to reverse these changes to re-enable CDC Serial functionality.

---

## Spoofing Arduino

### Steps to Spoof Arduino:

1. Locate the `boards.txt` file for your Arduino installation. For example:
   ```
   C:\Program Files (x86)\Arduino\hardware\arduino\avr\boards.txt
   ```
2. Copy the section for the Arduino Leonardo board and paste it at the bottom of the file.
3. Replace all instances of `leonardo` with a new unique identifier.
4. Change all `vid` (Vendor ID) and `pid` (Product ID) values to match those of your target device (e.g., your mouse).
5. Change the `build.usb_product` field to the name of your target device.
6. Disable the COM port by following instructions here: [Disable COM Port](https://www.unknowncheats.me/forum/3871884-post5.html)

---

## Spoofing Raspberry Pi

### Steps to Spoof Raspberry Pi:

1. Locate the `boards.txt` file for the Raspberry Pi Pico W package. For example:
   ```
   \AppData\Local\Arduino15\packages\rp2040\hardware\rp2040\3.6.0\boards.txt
   ```
2. Copy the Raspberry Pi Pico W section and paste it at the bottom of the file.
3. Replace all instances of `rpipicow` with a new unique identifier.
4. Change all `vid` and `pid` values to match those of your target device (e.g., your mouse).
5. Change `build.usb_manufacturer` and `build.usb_product` to your target device's manufacturer and name.
6. Locate the file:
   ```
   \AppData\Local\Arduino15\packages\rp2040\hardware\rp2040\3.6.0\cores\rp2040\RP2040USB.cpp
   ```
7. Search for the line containing:
   ```
   if (__USBInstallMouse || __USBInstallAbsoluteMouse)
   ```
8. Change the value `0x4000` to `0x0000` in the if statement.

---

## How to Reverse (Re-enable CDC Serial)

### For Leonardo/32u4-based boards

Instructions adapted from the [Arduino Forum](https://forum.arduino.cc/t/serial-port-for-leonardo-has-disappeared-from-ide/932053/2):

1. Remove the `-DCDC_DISABLED` flag from your build configuration.
2. Start uploading the Blink example sketch.
3. When the IDE reports memory usage, immediately press and release the reset button on the Arduino board.

### For UNO/Hoodloader2

1. Remove the `-DCDC_DISABLED` flag from your build configuration.
2. Re-install the [Hoodloader2 bootloader](https://github.com/NicoHood/HoodLoader2/wiki/Hardware-Installation).

---

This guide helps you customize your Arduino or Raspberry Pi USB device descriptors to spoof other devices, and also how to restore original serial functionality if needed.
