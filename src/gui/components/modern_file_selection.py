import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
from typing import Callable, Optional


class ModernDragDropFrame(ctk.CTkFrame):
    """Modern drag-and-drop frame with enhanced visual feedback"""
    
    def __init__(self, parent, folder_var: ctk.StringVar, 
                 callback: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.folder_var = folder_var
        self.callback = callback
        self.is_dragging = False
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Icon and text
        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text="📁",
            font=ctk.CTkFont(size=48),
            text_color="#4CAF50"
        )
        self.icon_label.grid(row=0, column=0, pady=(20, 10))
        
        self.main_text_label = ctk.CTkLabel(
            self.content_frame,
            text="Kéo thả thư mục vào đây",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#E0E0E0"
        )
        self.main_text_label.grid(row=1, column=0, pady=(0, 5))
        
        self.sub_text_label = ctk.CTkLabel(
            self.content_frame,
            text="hoặc nhấn để chọn thư mục",
            font=ctk.CTkFont(size=12),
            text_color="#BDBDBD"
        )
        self.sub_text_label.grid(row=2, column=0, pady=(0, 10))
        
        # Current folder display
        self.folder_display = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#4CAF50",
            wraplength=300
        )
        self.folder_display.grid(row=3, column=0, pady=(0, 20))
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            self.content_frame,
            text="🔍 Chọn thư mục",
            command=self.browse_folder,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        self.browse_btn.grid(row=4, column=0, pady=(0, 20))
        
        # Bind events
        self.bind_events()
        
        # Update display if folder already set
        self.update_display()
        
        # Watch for changes in folder_var
        self.folder_var.trace('w', lambda *args: self.update_display())
        
    def bind_events(self):
        """Bind drag and drop events"""
        # Bind to all widgets in the frame
        widgets = [self, self.content_frame, self.icon_label, 
                  self.main_text_label, self.sub_text_label, self.folder_display]
        
        for widget in widgets:
            # Drag enter
            widget.bind("<Button-1>", self.on_click)
            
        # Note: Actual drag and drop requires platform-specific implementations
        # For now, we'll focus on the visual feedback and click-to-browse
        
    def on_click(self, event):
        """Handle click to browse"""
        self.browse_folder()
        
    def browse_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(
            title="Chọn thư mục chứa video",
            initialdir=self.folder_var.get() if self.folder_var.get() else os.path.expanduser("~")
        )
        
        if folder:
            self.folder_var.set(folder)
            if self.callback:
                self.callback(folder)
                
    def update_display(self):
        """Update the display based on current folder"""
        folder = self.folder_var.get()
        
        if folder and os.path.exists(folder):
            # Show selected folder
            self.icon_label.configure(text="✅", text_color="#4CAF50")
            self.main_text_label.configure(
                text="Thư mục đã chọn:",
                text_color="#4CAF50"
            )
            
            # Show folder name (last part of path)
            folder_name = os.path.basename(folder) or folder
            self.folder_display.configure(
                text=f"📁 {folder_name}",
                text_color="#4CAF50"
            )
            
            self.sub_text_label.configure(
                text="Nhấn để thay đổi thư mục",
                text_color="#BDBDBD"
            )
            
            self.browse_btn.configure(text="🔄 Đổi thư mục")
            
            # Change frame color to indicate selection
            self.content_frame.configure(fg_color="#1B3B1B")
            
        else:
            # Reset to default state
            self.icon_label.configure(text="📁", text_color="#4CAF50")
            self.main_text_label.configure(
                text="Kéo thả thư mục vào đây",
                text_color="#E0E0E0"
            )
            self.folder_display.configure(text="")
            self.sub_text_label.configure(
                text="hoặc nhấn để chọn thư mục",
                text_color="#BDBDBD"
            )
            self.browse_btn.configure(text="🔍 Chọn thư mục")
            self.content_frame.configure(fg_color="#2B2B2B")
            
    def set_drag_state(self, is_dragging: bool):
        """Set visual state for drag and drop"""
        if is_dragging:
            self.content_frame.configure(fg_color="#3B3B2B")
            self.icon_label.configure(text="📂", text_color="#FF9800")
            self.main_text_label.configure(
                text="Thả thư mục tại đây",
                text_color="#FF9800"
            )
        else:
            self.update_display()


class ModernFileSelectionPanel(ctk.CTkFrame):
    """Enhanced file selection panel with modern UX"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#2B2B2B", **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Variables
        self.input_folder_var = ctk.StringVar()
        self.output_folder_var = ctk.StringVar()
        self.save_same_folder_var = ctk.BooleanVar(value=True)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets"""
        
        # Section title
        title_label = ctk.CTkLabel(
            self,
            text="📁 Quản lý thư mục",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2196F3"
        )
        title_label.grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        # Input folder section
        input_section = ctk.CTkFrame(self, fg_color="#1A1A1A")
        input_section.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        input_section.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            input_section,
            text="📥 Thư mục đầu vào (Video):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Drag and drop frame for input
        self.input_drag_frame = ModernDragDropFrame(
            input_section,
            self.input_folder_var,
            callback=self.on_input_folder_selected,
            height=120
        )
        self.input_drag_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Save same folder checkbox
        checkbox_frame = ctk.CTkFrame(self, fg_color="#1A1A1A")
        checkbox_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.same_folder_cb = ctk.CTkCheckBox(
            checkbox_frame,
            text="💾 Lưu phụ đề cùng vị trí với video",
            variable=self.save_same_folder_var,
            command=self.toggle_output_folder,
            text_color="#E0E0E0",
            checkbox_width=20,
            checkbox_height=20,
            font=ctk.CTkFont(size=13)
        )
        self.same_folder_cb.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Output folder section
        self.output_section = ctk.CTkFrame(self, fg_color="#1A1A1A")
        self.output_section.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.output_section.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.output_section,
            text="📤 Thư mục đầu ra (Phụ đề):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF9800"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Drag and drop frame for output
        self.output_drag_frame = ModernDragDropFrame(
            self.output_section,
            self.output_folder_var,
            callback=self.on_output_folder_selected,
            height=120
        )
        self.output_drag_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Initially disable output folder
        self.toggle_output_folder()
        
    def on_input_folder_selected(self, folder: str):
        """Handle input folder selection"""
        # You can add additional logic here
        pass
        
    def on_output_folder_selected(self, folder: str):
        """Handle output folder selection"""
        # You can add additional logic here
        pass
        
    def toggle_output_folder(self):
        """Toggle output folder based on checkbox"""
        if self.save_same_folder_var.get():
            # Disable output folder selection
            self.output_section.configure(fg_color="#0F0F0F")
            self.output_drag_frame.configure(state="disabled")
            for child in self.output_drag_frame.winfo_children():
                if hasattr(child, 'configure'):
                    try:
                        child.configure(state="disabled")
                    except:
                        pass
        else:
            # Enable output folder selection
            self.output_section.configure(fg_color="#1A1A1A")
            self.output_drag_frame.configure(state="normal")
            for child in self.output_drag_frame.winfo_children():
                if hasattr(child, 'configure'):
                    try:
                        child.configure(state="normal")
                    except:
                        pass
                        
    def get_folders(self) -> tuple[str, str, bool]:
        """Get selected folders and save preference"""
        return (
            self.input_folder_var.get(),
            self.output_folder_var.get(),
            self.save_same_folder_var.get()
        )