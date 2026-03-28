import webbrowser
import socket
import urllib.request
import os
from fastapi import APIRouter

# Khởi tạo router cho các endpoint hệ thống
# Router này chứa các API liên quan đến điều khiển desktop, như focus vào cửa sổ.
router = APIRouter(
    prefix="/api",
    tags=["System"],
)

def open_browser(port=5000):
    """Mở trình duyệt web trỏ tới frontend sau một khoảng trễ ngắn."""
    webbrowser.open_new_tab(f"http://127.0.0.1:{port}/login")

@router.get("/focus")
def focus_window():
    """Endpoint được gọi bởi instance mới của app để focus vào instance cũ."""
    open_browser()
    return {"message": "Focus request received"}

def is_app_already_running(port=5000):
    """Kiểm tra xem port đã bị chiếm dụng chưa. Nếu rồi thì app đã đang chạy."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True

def focus_existing_app(port=5000):
    """Gửi tín hiệu focus tới instance app đang chạy và thoát instance hiện tại."""
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/api/focus", timeout=2)
    except Exception:
        pass # Bỏ qua lỗi nếu app cũ không phản hồi
    os._exit(0) # [FIX FATAL ERROR] Ép Windows đóng tiến trình mượt mà, không bung popup lỗi của Pyinstaller