import customtkinter as ctk
import tkinter as tk
from typing import Optional


class ModernTooltip:
    """Modern tooltip for CustomTkinter widgets"""
    
    def __init__(self, widget, text: str, delay: int = 500, wraplength: int = 250):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        
        self.tooltip_window = None
        self.show_timer = None
        self.hide_timer = None
        
        # Bind events
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
        self.widget.bind('<Motion>', self.on_motion)
        
    def on_enter(self, event=None):
        """Handle mouse enter"""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
        
        self.show_timer = self.widget.after(self.delay, self.show_tooltip)
        
    def on_leave(self, event=None):
        """Handle mouse leave"""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
            
        if self.tooltip_window:
            self.hide_timer = self.widget.after(100, self.hide_tooltip)
            
    def on_motion(self, event=None):
        """Handle mouse motion"""
        if self.tooltip_window:
            self.update_position(event)
            
    def show_tooltip(self):
        """Show the tooltip"""
        if self.tooltip_window:
            return
            
        # Get widget position
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_attributes('-topmost', True)
        
        # Configure appearance
        self.tooltip_window.configure(bg='#2B2B2B', relief='solid', borderwidth=1)
        
        # Create content frame
        frame = tk.Frame(
            self.tooltip_window,
            bg='#2B2B2B',
            relief='flat',
            borderwidth=0
        )
        frame.pack()
        
        # Add text
        label = tk.Label(
            frame,
            text=self.text,
            bg='#2B2B2B',
            fg='#E0E0E0',
            font=('Segoe UI', 9),
            wraplength=self.wraplength,
            justify='left',
            relief='flat',
            borderwidth=0,
            padx=8,
            pady=6
        )
        label.pack()
        
        # Position tooltip
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()
        
        # Adjust position if tooltip goes off screen
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
            
        if y + tooltip_height > screen_height:
            y = self.widget.winfo_rooty() - tooltip_height - 5
            
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Bind events to tooltip window
        self.tooltip_window.bind('<Enter>', self.on_tooltip_enter)
        self.tooltip_window.bind('<Leave>', self.on_tooltip_leave)
        
    def hide_tooltip(self):
        """Hide the tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
        if self.hide_timer:
            self.widget.after_cancel(self.hide_timer)
            self.hide_timer = None
            
    def on_tooltip_enter(self, event=None):
        """Handle mouse enter tooltip window"""
        if self.hide_timer:
            self.widget.after_cancel(self.hide_timer)
            self.hide_timer = None
            
    def on_tooltip_leave(self, event=None):
        """Handle mouse leave tooltip window"""
        self.hide_tooltip()
        
    def update_position(self, event):
        """Update tooltip position based on mouse"""
        if not self.tooltip_window:
            return
            
        x = event.x_root + 10
        y = event.y_root + 10
        
        # Adjust if going off screen
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        if x + tooltip_width > screen_width:
            x = event.x_root - tooltip_width - 10
            
        if y + tooltip_height > screen_height:
            y = event.y_root - tooltip_height - 10
            
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
    def update_text(self, new_text: str):
        """Update tooltip text"""
        self.text = new_text


def add_tooltip(widget, text: str, delay: int = 500, wraplength: int = 250):
    """Add tooltip to a widget"""
    return ModernTooltip(widget, text, delay, wraplength)


class ModernProgressTooltip(ModernTooltip):
    """Special tooltip for progress bars with dynamic content"""
    
    def __init__(self, widget, get_text_func, delay: int = 200):
        self.get_text_func = get_text_func
        super().__init__(widget, "", delay)
        
    def show_tooltip(self):
        """Show tooltip with dynamic content"""
        self.text = self.get_text_func()
        super().show_tooltip()


class ModernButtonTooltip(ModernTooltip):
    """Enhanced tooltip for buttons with keyboard shortcuts"""
    
    def __init__(self, widget, text: str, shortcut: Optional[str] = None, delay: int = 500):
        if shortcut:
            full_text = f"{text}\n\n⌨️ Phím tắt: {shortcut}"
        else:
            full_text = text
            
        super().__init__(widget, full_text, delay, wraplength=300)