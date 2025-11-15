import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk

# Windows API constants and structures
GAMMA_RAMP_SIZE = 256

class GammaRamp(ctypes.Structure):
    _fields_ = [
        ('red', (wintypes.WORD * GAMMA_RAMP_SIZE)),
        ('green', (wintypes.WORD * GAMMA_RAMP_SIZE)),
        ('blue', (wintypes.WORD * GAMMA_RAMP_SIZE))
    ]

# Load Windows DLLs
gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32

# Get device context
hdc = user32.GetDC(0)

# Store original gamma for restoration
original_gamma = None

def get_gamma_ramp():
    """Get current gamma ramp"""
    ramp = GammaRamp()
    gdi32.GetDeviceGammaRamp(hdc, ctypes.byref(ramp))
    return ramp

def set_gamma(brightness):
    """
    Set brightness level using linear scaling
    brightness: 0.0 to 1.0 (1.0 = normal, 0.0 = very dim)
    """
    global original_gamma
    
    # Save original gamma on first call
    if original_gamma is None:
        original_gamma = get_gamma_ramp()
    
    ramp = GammaRamp()
    
    # Use linear scaling instead of gamma correction
    # Scale the original gamma ramp values by brightness factor
    for i in range(GAMMA_RAMP_SIZE):
        # Scale each channel value linearly by brightness
        red_value = int(original_gamma.red[i] * brightness)
        green_value = int(original_gamma.green[i] * brightness)
        blue_value = int(original_gamma.blue[i] * brightness)
        
        # Clamp to valid range
        ramp.red[i] = max(0, min(65535, red_value))
        ramp.green[i] = max(0, min(65535, green_value))
        ramp.blue[i] = max(0, min(65535, blue_value))
    
    gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))

def restore_gamma():
    """Restore original gamma"""
    global original_gamma
    if original_gamma is not None:
        gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(original_gamma))

class CustomSlider:
    def __init__(
        self,
        parent,
        width=380,
        height=36,
        min_value=0.1,
        max_value=1.0,
        initial_value=1.0,
        on_change=None,
        bg="#2a2a3e",
        track_color="#3a3a4e",
        progress_color="#6c5ce7",
        thumb_color="#ffffff",
        thumb_border="#6c5ce7"
    ):
        self.parent = parent
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = max(min(initial_value, max_value), min_value)
        self.on_change = on_change
        self.bg = bg
        self.track_color = track_color
        self.progress_color = progress_color
        self.thumb_color = thumb_color
        self.thumb_border = thumb_border
        self.padding = 12
        self.thumb_radius = 10
        self.center_y = height // 2

        self.canvas = tk.Canvas(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            relief=tk.FLAT,
            cursor="hand2"
        )

        # Track and progress (rounded via capstyle)
        self.track_id = self.canvas.create_line(
            self.padding,
            self.center_y,
            self.width - self.padding,
            self.center_y,
            fill=self.track_color,
            width=8,
            capstyle=tk.ROUND
        )
        self.progress_id = self.canvas.create_line(
            self.padding,
            self.center_y,
            self.padding,
            self.center_y,
            fill=self.progress_color,
            width=8,
            capstyle=tk.ROUND
        )

        # Thumb
        thumb_x = self._value_to_x(self.value)
        self.thumb_id = self.canvas.create_oval(
            thumb_x - self.thumb_radius,
            self.center_y - self.thumb_radius,
            thumb_x + self.thumb_radius,
            self.center_y + self.thumb_radius,
            fill=self.thumb_color,
            outline=self.thumb_border,
            width=2
        )

        # Events
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Configure>", self._on_resize)

        self._update_graphics()

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def set(self, new_value: float):
        clamped = max(min(new_value, self.max_value), self.min_value)
        self.value = clamped
        self._update_graphics()
        if self.on_change is not None:
            self.on_change(self.value)

    def get(self) -> float:
        return self.value

    def _value_to_x(self, value: float) -> float:
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        min_x = self.padding
        max_x = self.width - self.padding
        return min_x + ratio * (max_x - min_x)

    def _x_to_value(self, x: float) -> float:
        min_x = self.padding
        max_x = self.width - self.padding
        ratio = (x - min_x) / (max_x - min_x)
        ratio = max(0.0, min(1.0, ratio))
        return self.min_value + ratio * (self.max_value - self.min_value)

    def _update_graphics(self):
        x = self._value_to_x(self.value)
        self.canvas.coords(self.progress_id, self.padding, self.center_y, x, self.center_y)
        self.canvas.coords(
            self.thumb_id,
            x - self.thumb_radius,
            self.center_y - self.thumb_radius,
            x + self.thumb_radius,
            self.center_y + self.thumb_radius
        )

    def _on_click(self, event):
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.center_y = self.height // 2
        self.value = self._x_to_value(event.x)
        self._update_graphics()
        if self.on_change is not None:
            self.on_change(self.value)

    def _on_drag(self, event):
        self._on_click(event)

    def _on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.center_y = self.height // 2
        self.canvas.coords(
            self.track_id,
            self.padding,
            self.center_y,
            self.width - self.padding,
            self.center_y
        )
        self._update_graphics()

class ScreenDimmerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Dimmer")
        self.root.geometry("480x350")
        self.root.resizable(False, False)
        
        # Modern dark color scheme
        self.bg_color = "#1e1e2e"
        self.card_color = "#2a2a3e"
        self.accent_color = "#6c5ce7"
        self.text_color = "#ffffff"
        self.text_secondary = "#a0a0a0"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Restore gamma on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container with padding
        container = tk.Frame(root, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card frame for main content
        main_frame = tk.Frame(container, bg=self.card_color, relief=tk.FLAT)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inner padding frame
        inner_frame = tk.Frame(main_frame, bg=self.card_color)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Title with icon emoji
        title_label = tk.Label(
            inner_frame,
            text="💡 Screen Dimmer",
            font=("Segoe UI", 20, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title_label.pack(pady=(0, 20))
        
        # Brightness display with large percentage
        self.brightness_percentage = tk.Label(
            inner_frame,
            text="100%",
            font=("Segoe UI", 36, "bold"),
            bg=self.card_color,
            fg=self.accent_color
        )
        self.brightness_percentage.pack(pady=(0, 5))
        
        self.brightness_label = tk.Label(
            inner_frame,
            text="Brightness Level",
            font=("Segoe UI", 11),
            bg=self.card_color,
            fg=self.text_secondary
        )
        self.brightness_label.pack(pady=(0, 20))
        
        # Brightness slider with modern styling
        slider_container = tk.Frame(inner_frame, bg=self.card_color)
        slider_container.pack(pady=20, fill=tk.X)
        
        # Custom slider (Canvas-based) for modern look
        self.slider = CustomSlider(
            slider_container,
            width=380,
            height=36,
            min_value=0.1,
            max_value=1.0,
            initial_value=1.0,
            on_change=self.on_slider_change,
            bg=self.card_color,
            track_color="#3a3a4e",
            progress_color=self.accent_color,
            thumb_color="#ffffff",
            thumb_border=self.accent_color
        )
        self.slider.pack(fill=tk.X)
        
        # Buttons frame
        button_frame = tk.Frame(inner_frame, bg=self.card_color)
        button_frame.pack(pady=(15, 0))
        
        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text="↻ Reset",
            command=self.reset_brightness,
            font=("Segoe UI", 10, "bold"),
            bg="#4a4a5e",
            fg="#ffffff",
            activebackground="#5a5a6e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2",
            highlightthickness=0
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Minimize button
        minimize_btn = tk.Button(
            button_frame,
            text="⬇ Minimize",
            command=self.minimize_to_tray,
            font=("Segoe UI", 10, "bold"),
            bg="#4a4a5e",
            fg="#ffffff",
            activebackground="#5a5a6e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2",
            highlightthickness=0
        )
        minimize_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize with normal brightness
        set_gamma(1.0)
    
    def update_slider_progress(self, brightness):
        return
    
    def on_slider_change(self, value):
        """Handle slider change"""
        brightness = float(value)
        set_gamma(brightness)
        percentage = int(brightness * 100)
        self.brightness_percentage.config(text=f"{percentage}%")
    
    def reset_brightness(self):
        """Reset brightness to normal"""
        self.slider.set(1.0)
        restore_gamma()
        self.brightness_percentage.config(text="100%")
    
    def minimize_to_tray(self):
        """Minimize window to system tray"""
        self.root.iconify()
    
    def on_closing(self):
        """Handle window close - restore gamma"""
        restore_gamma()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenDimmerApp(root)
    root.mainloop()


