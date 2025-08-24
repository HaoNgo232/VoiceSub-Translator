import customtkinter as ctk
from tkinter import messagebox
import traceback
from typing import Optional, Callable


class ModernErrorHandler:
    """Modern error handling with user-friendly messages"""
    
    ERROR_MESSAGES = {
        "FileNotFoundError": {
            "title": "❌ Không tìm thấy file",
            "message": "File hoặc thư mục bạn chọn không tồn tại hoặc đã bị di chuyển.",
            "suggestions": [
                "Kiểm tra lại đường dẫn file/thư mục",
                "Đảm bảo file không bị xóa hoặc di chuyển",
                "Thử chọn lại file/thư mục"
            ]
        },
        "PermissionError": {
            "title": "🔒 Không có quyền truy cập",
            "message": "Ứng dụng không có quyền truy cập vào file hoặc thư mục này.",
            "suggestions": [
                "Chạy ứng dụng với quyền Administrator",
                "Kiểm tra quyền truy cập file/thư mục",
                "Đảm bảo file không bị khóa bởi ứng dụng khác"
            ]
        },
        "ConnectionError": {
            "title": "🌐 Lỗi kết nối",
            "message": "Không thể kết nối đến dịch vụ AI. Kiểm tra kết nối internet.",
            "suggestions": [
                "Kiểm tra kết nối internet",
                "Thử lại sau vài phút",
                "Thử đổi sang dịch vụ khác",
                "Kiểm tra firewall/proxy"
            ]
        },
        "ValueError": {
            "title": "⚠️ Giá trị không hợp lệ",
            "message": "Dữ liệu đầu vào không đúng định dạng hoặc không hợp lệ.",
            "suggestions": [
                "Kiểm tra lại file video/phụ đề",
                "Đảm bảo file không bị hỏng",
                "Thử với file khác để kiểm tra"
            ]
        },
        "MemoryError": {
            "title": "💾 Không đủ bộ nhớ",
            "message": "Hệ thống không đủ RAM để xử lý file này.",
            "suggestions": [
                "Đóng các ứng dụng khác đang chạy",
                "Thử với file video nhỏ hơn",
                "Khởi động lại máy tính",
                "Giảm chất lượng model AI"
            ]
        },
        "TimeoutError": {
            "title": "⏰ Hết thời gian chờ",
            "message": "Quá trình xử lý mất quá nhiều thời gian và đã bị dừng.",
            "suggestions": [
                "Thử lại với file nhỏ hơn",
                "Kiểm tra kết nối internet",
                "Giảm chất lượng model AI",
                "Thử vào thời điểm khác khi server ít tải"
            ]
        }
    }
    
    @staticmethod
    def show_error_dialog(parent, exception: Exception, context: str = ""):
        """Show modern error dialog with helpful information"""
        
        # Get error type
        error_type = type(exception).__name__
        error_info = ModernErrorHandler.ERROR_MESSAGES.get(
            error_type, 
            {
                "title": "❌ Lỗi không xác định",
                "message": "Đã xảy ra lỗi không xác định trong quá trình xử lý.",
                "suggestions": [
                    "Thử lại thao tác",
                    "Khởi động lại ứng dụng",
                    "Kiểm tra file log để biết thêm chi tiết"
                ]
            }
        )
        
        # Create error dialog
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Lỗi")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure grid
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color="#1A1A1A")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=error_info["title"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F44336"
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Context if provided
        if context:
            context_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
            context_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
            
            ctk.CTkLabel(
                context_frame,
                text="📍 Ngữ cảnh:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FF9800"
            ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                context_frame,
                text=context,
                font=ctk.CTkFont(size=12),
                text_color="#E0E0E0",
                wraplength=500,
                justify="left"
            ).grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Error message
        message_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        message_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            message_frame,
            text="💬 Mô tả:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2196F3"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            message_frame,
            text=error_info["message"],
            font=ctk.CTkFont(size=12),
            text_color="#E0E0E0",
            wraplength=500,
            justify="left"
        ).grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Suggestions
        suggestions_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        suggestions_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            suggestions_frame,
            text="💡 Giải pháp:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        for i, suggestion in enumerate(error_info["suggestions"]):
            ctk.CTkLabel(
                suggestions_frame,
                text=f"• {suggestion}",
                font=ctk.CTkFont(size=12),
                text_color="#E0E0E0",
                wraplength=500,
                justify="left"
            ).grid(row=i+1, column=0, sticky="w", padx=30, pady=2)
            
        ctk.CTkLabel(
            suggestions_frame,
            text="",
            height=10
        ).grid(row=len(error_info["suggestions"])+1, column=0)
        
        # Technical details (expandable)
        details_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        details_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        
        show_details_var = ctk.BooleanVar(value=False)
        
        def toggle_details():
            if show_details_var.get():
                details_text.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
                details_btn.configure(text="🔼 Ẩn chi tiết kỹ thuật")
            else:
                details_text.grid_remove()
                details_btn.configure(text="🔽 Hiện chi tiết kỹ thuật")
        
        details_btn = ctk.CTkButton(
            details_frame,
            text="🔽 Hiện chi tiết kỹ thuật",
            command=toggle_details,
            height=30,
            fg_color="#607D8B",
            hover_color="#455A64"
        )
        details_btn.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Technical details text
        technical_details = f"""Loại lỗi: {error_type}
Chi tiết: {str(exception)}

Traceback:
{traceback.format_exc()}"""
        
        details_text = ctk.CTkTextbox(
            details_frame,
            height=150,
            font=ctk.CTkFont(family="Courier", size=10)
        )
        details_text.insert("1.0", technical_details)
        details_text.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="📋 Sao chép lỗi",
            command=lambda: ModernErrorHandler._copy_to_clipboard(technical_details),
            height=40,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="✅ Đóng",
            command=dialog.destroy,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049"
        ).pack(side="left", padx=10)
        
    @staticmethod
    def _copy_to_clipboard(text: str):
        """Copy text to clipboard"""
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
        except:
            pass
            
    @staticmethod
    def handle_exception(parent, func: Callable, *args, context: str = "", **kwargs):
        """Execute function with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ModernErrorHandler.show_error_dialog(parent, e, context)
            return None
            
    @staticmethod
    def safe_execute(parent, func: Callable, context: str = "", 
                    success_callback: Optional[Callable] = None,
                    error_callback: Optional[Callable] = None):
        """Safely execute function with callbacks"""
        try:
            result = func()
            if success_callback:
                success_callback(result)
            return result
        except Exception as e:
            ModernErrorHandler.show_error_dialog(parent, e, context)
            if error_callback:
                error_callback(e)
            return None


def show_success_notification(parent, title: str, message: str, 
                            duration: int = 3000):
    """Show success notification"""
    notification = ctk.CTkToplevel(parent)
    notification.title("Thành công")
    notification.geometry("400x120")
    notification.transient(parent)
    notification.attributes("-topmost", True)
    
    # Position in top-right corner
    notification.update_idletasks()
    x = notification.winfo_screenwidth() - 420
    y = 50
    notification.geometry(f"400x120+{x}+{y}")
    
    # Configure
    notification.configure(fg_color="#1B5E20")
    
    # Content
    main_frame = ctk.CTkFrame(notification, fg_color="#2E7D32")
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    ctk.CTkLabel(
        main_frame,
        text=f"✅ {title}",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#FFFFFF"
    ).pack(pady=(10, 5))
    
    ctk.CTkLabel(
        main_frame,
        text=message,
        font=ctk.CTkFont(size=12),
        text_color="#E8F5E8",
        wraplength=350
    ).pack(pady=(0, 10))
    
    # Auto close
    notification.after(duration, notification.destroy)


def show_warning_dialog(parent, title: str, message: str, 
                       suggestions: list = None):
    """Show warning dialog"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Cảnh báo")
    dialog.geometry("450x300")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    main_frame = ctk.CTkFrame(dialog, fg_color="#1A1A1A")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    ctk.CTkLabel(
        main_frame,
        text=f"⚠️ {title}",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#FF9800"
    ).pack(pady=(10, 20))
    
    # Message
    ctk.CTkLabel(
        main_frame,
        text=message,
        font=ctk.CTkFont(size=12),
        text_color="#E0E0E0",
        wraplength=400,
        justify="left"
    ).pack(pady=(0, 20))
    
    # Suggestions
    if suggestions:
        ctk.CTkLabel(
            main_frame,
            text="💡 Khuyến nghị:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        ).pack(anchor="w", padx=20)
        
        for suggestion in suggestions:
            ctk.CTkLabel(
                main_frame,
                text=f"• {suggestion}",
                font=ctk.CTkFont(size=11),
                text_color="#E0E0E0",
                wraplength=350,
                justify="left"
            ).pack(anchor="w", padx=40, pady=2)
    
    # Button
    ctk.CTkButton(
        main_frame,
        text="Đã hiểu",
        command=dialog.destroy,
        height=40,
        fg_color="#FF9800",
        hover_color="#F57C00"
    ).pack(pady=20)