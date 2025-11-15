# Screen Dimmer

A simple Windows application that dims your screen by adjusting the gamma ramp, allowing you to reduce brightness beyond your monitor's minimum setting.
Useful when your monitor won't get as dim as you'd like at night.

## Features

- Adjustable brightness slider
- Automatically restores original gamma when closed
- Literally just dims your screen. That's all this app does. And it's free!

## Usage

### For Normies

1. Click on the latest release on the left sidebar of this page
2. Download the .exe file
3. Run the .exe file. Windows will throw a warning - just ignore it.
4. That's it!

### For Techies

1. Run the application:
   ```bash
   python screen_dimmer.py
   ```
2. There is no step 2.


## How It Works

The application uses Windows GDI (Graphics Device Interface) API to adjust the gamma ramp of your display. This allows for software-based brightness control that works independently of your monitor's hardware brightness settings.

## Notes

- The gamma settings are applied system-wide
- Original gamma is automatically restored when the application closes
- Minimum brightness is set to 10% to prevent the screen from becoming completely unusable

