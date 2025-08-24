import customtkinter as ctk
import time
from typing import Optional


class ModernProgressWindow:
    """Modern progress window with enhanced visual feedback"""
    
    def __init__(self, parent, title: str = "Đang xử lý..."):
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.after(100, self._center_dialog)
        
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Variables
        self.start_time = time.time()
        self.last_update_time = time.time()
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.dialog, fg_color="#1A1A1A")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            main_frame,
            text="⚡ Đang xử lý",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        
        # Status
        self.status_var = ctk.StringVar(value="🔄 Đang chuẩn bị...")
        self.status_label = ctk.CTkLabel(
            main_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=14),
            text_color="#E0E0E0",
            wraplength=450
        )
        self.status_label.grid(row=1, column=0, pady=10, sticky="ew")
        
        # Progress frame
        progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            progress_color="#4CAF50"
        )
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progress.set(0)
        
        # Progress info frame
        info_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Progress text
        self.progress_var = ctk.StringVar(value="0/0")
        progress_label = ctk.CTkLabel(
            info_frame,
            textvariable=self.progress_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4CAF50"
        )
        progress_label.grid(row=0, column=0, sticky="w")
        
        # Time elapsed
        self.time_var = ctk.StringVar(value="⏱️ 00:00")
        time_label = ctk.CTkLabel(
            info_frame,
            textvariable=self.time_var,
            font=ctk.CTkFont(size=12),
            text_color="#BDBDBD"
        )
        time_label.grid(row=0, column=1, sticky="e")
        
        # ETA
        self.eta_var = ctk.StringVar(value="")
        self.eta_label = ctk.CTkLabel(
            info_frame,
            textvariable=self.eta_var,
            font=ctk.CTkFont(size=11),
            text_color="#FF9800"
        )
        self.eta_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Speed info
        self.speed_var = ctk.StringVar(value="")
        self.speed_label = ctk.CTkLabel(
            progress_frame,
            textvariable=self.speed_var,
            font=ctk.CTkFont(size=10),
            text_color="#9E9E9E"
        )
        self.speed_label.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Update timer
        self._update_timer()
        
    def _center_dialog(self):
        """Center the dialog on screen"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def _update_timer(self):
        """Update elapsed time"""
        if self.dialog.winfo_exists():
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.time_var.set(f"⏱️ {minutes:02d}:{seconds:02d}")
            
            # Schedule next update
            self.dialog.after(1000, self._update_timer)
            
    def _calculate_eta(self, current: int, total: int) -> str:
        """Calculate estimated time of arrival"""
        if current <= 0 or total <= 0:
            return ""
            
        elapsed = time.time() - self.start_time
        if elapsed < 1:  # Not enough data yet
            return ""
            
        rate = current / elapsed  # items per second
        if rate <= 0:
            return ""
            
        remaining_items = total - current
        eta_seconds = int(remaining_items / rate)
        
        if eta_seconds < 60:
            return f"📍 ETA: {eta_seconds}s"
        elif eta_seconds < 3600:
            minutes = eta_seconds // 60
            seconds = eta_seconds % 60
            return f"📍 ETA: {minutes}m {seconds}s"
        else:
            hours = eta_seconds // 3600
            minutes = (eta_seconds % 3600) // 60
            return f"📍 ETA: {hours}h {minutes}m"
            
    def _calculate_speed(self, current: int) -> str:
        """Calculate processing speed"""
        elapsed = time.time() - self.start_time
        if elapsed < 1 or current <= 0:
            return ""
            
        rate = current / elapsed
        if rate < 1:
            return f"🚀 Tốc độ: {rate:.2f} files/s"
        else:
            return f"🚀 Tốc độ: {rate:.1f} files/s"
            
    def update(self, current: int, total: int, status: str = ""):
        """Update progress with enhanced information"""
        def _update():
            if not self.dialog.winfo_exists():
                return
                
            # Update status
            if status:
                self.status_var.set(status)
                
            # Update progress
            if total > 0:
                progress_value = current / total
                self.progress.set(progress_value)
                self.progress_var.set(f"{current}/{total} files")
                
                # Update ETA
                eta_text = self._calculate_eta(current, total)
                self.eta_var.set(eta_text)
                
                # Update speed
                speed_text = self._calculate_speed(current)
                self.speed_var.set(speed_text)
                
                # Update title based on progress
                percentage = int(progress_value * 100)
                self.title_label.configure(text=f"⚡ Đang xử lý ({percentage}%)")
            else:
                self.progress_var.set("0/0 files")
                
        # Use after to ensure thread safety
        self.dialog.after(0, _update)
        
    def close(self):
        """Close the progress window"""
        def _close():
            if self.dialog.winfo_exists():
                self.dialog.destroy()
                
        self.dialog.after(0, _close)
        
    # Context manager support
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False