import uvicorn
import threading
from fastapi import FastAPI, Response

# Import các module
from core import websocket_manager, desktop_utils
from api import auth
from config import middleware, frontend_serving, security

# Khởi tạo ứng dụng FastAPI.
app = FastAPI()

@app.get("/js/config.js", include_in_schema=False)
async def get_config_js():
    """
    Endpoint này tạo ra một file JS "ảo" chứa chìa khóa bí mật.
    Frontend sẽ gọi đến đây để lấy chìa khóa.
    """
    content = f'window.APP_SECRET = "{security.APP_SECRET}";'
    return Response(content=content, media_type="application/javascript")

# --- Đăng ký Middleware ---
app.middleware("http")(middleware.add_no_cache_headers)

# --- Đăng ký các API Routers ---
# Các route API cụ thể phải được đăng ký trước route "catch-all" của StaticFiles.
app.include_router(websocket_manager.router)
app.include_router(auth.router)
app.include_router(desktop_utils.router)

# --- Cấu hình phục vụ Frontend ---
# Đăng ký các route phục vụ file HTML và thư mục tĩnh.
# QUAN TRỌNG: Việc này phải được thực hiện SAU KHI đăng ký các API router.
frontend_serving.setup_frontend_serving(app)

if __name__ == "__main__":
    APP_PORT = 5000

    # Chống mở nhiều instance: Đánh thức tab cũ và tự động thoát trong im lặng
    if desktop_utils.is_app_already_running(APP_PORT):
        desktop_utils.focus_existing_app(APP_PORT)

    # Lên lịch mở trình duyệt sau khi server có thời gian khởi động
    threading.Timer(1.5, desktop_utils.open_browser, args=[APP_PORT]).start()

    # [SCALE 50 PROFILE] Uvicorn/FastAPI chạy chung event loop cực kỳ tối ưu, xoá bỏ xung đột Threading
    uvicorn.run(app, host="127.0.0.1", port=APP_PORT, log_level="debug")