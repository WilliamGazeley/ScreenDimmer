# Screen Dimmer

A simple Windows application that dims your screen by adjusting the gamma ramp, allowing you to reduce brightness beyond your monitor's minimum setting.

## Features

- Adjustable brightness slider (10% to 100%)
- Real-time gamma adjustment
- Automatically restores original gamma when closed
- Simple, intuitive interface

## Requirements

- Windows operating system
- Python 3.x (tkinter included by default)

## Usage

1. Run the application:
   ```bash
   python screen_dimmer.py
   ```

2. Use the slider to adjust brightness:
   - Drag left to dim the screen
   - Drag right to brighten the screen

3. Click "Reset to Normal" to restore full brightness

4. The application will automatically restore your original gamma settings when closed

## How It Works

The application uses Windows GDI (Graphics Device Interface) API to adjust the gamma ramp of your display. This allows for software-based brightness control that works independently of your monitor's hardware brightness settings.

## Notes

- The gamma settings are applied system-wide
- Original gamma is automatically restored when the application closes
- Minimum brightness is set to 10% to prevent the screen from becoming completely unusable


