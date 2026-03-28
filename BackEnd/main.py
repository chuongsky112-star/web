import uvicorn
import threading
import os
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
    # Cấu hình cho deployment trên các nền tảng như Render:
    # - Host: "0.0.0.0" để server có thể được truy cập từ bên ngoài container.
    # - Port: Đọc từ biến môi trường `PORT` do nền tảng cung cấp, mặc định là 5000 cho local dev.
    APP_HOST = "0.0.0.0"
    APP_PORT = int(os.environ.get("PORT", 5000))

    # Các logic dưới đây dành riêng cho môi trường desktop và sẽ gây lỗi khi deploy.
    # Chúng ta sẽ vô hiệu hóa chúng khi deploy lên server.
    # if desktop_utils.is_app_already_running(APP_PORT):
    #     desktop_utils.focus_existing_app(APP_PORT)
    #
    # # Tự động mở trình duyệt cũng không cần thiết trên server.
    # threading.Timer(1.5, desktop_utils.open_browser, args=[APP_PORT]).start()

    # Chạy server Uvicorn với cấu hình cho deployment.
    # log_level="info" là lựa chọn tốt cho môi trường production.
    uvicorn.run(app, host=APP_HOST, port=APP_PORT, log_level="info")