import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Tính toán đường dẫn tuyệt đối đến thư mục public của frontend
# __file__ -> .../BackEnd/config/frontend_serving.py
# os.path.dirname(...) -> .../BackEnd/config
# os.path.dirname(...) -> .../BackEnd
# os.path.dirname(...) -> .../ALL_IN_ONE (PROJECT_ROOT)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_PUBLIC_DIR = os.path.join(PROJECT_ROOT, "FrontEnd", "public")

def setup_frontend_serving(app: FastAPI):
    """
    Cấu hình phục vụ các file tĩnh và các trang HTML của frontend.
    
    Hàm này định nghĩa các route tường minh cho các trang chính và mount
    thư mục public để phục vụ các tài nguyên tĩnh khác (JS, CSS, images).
    
    QUAN TRỌNG: Hàm này nên được gọi sau khi đã đăng ký tất cả các API router
    để đảm bảo `app.mount("/", ...)` không "nuốt" mất các route API.
    """

    # Định nghĩa các route tường minh cho các trang HTML chính.
    # Cách này đảm bảo các trang luôn được phục vụ đúng cách và có độ ưu tiên cao.
    # `include_in_schema=False` để ẩn các route này khỏi giao diện Swagger/OpenAPI.
    @app.get("/", tags=["Frontend"], include_in_schema=False)
    async def serve_root_as_login():
        return FileResponse(os.path.join(FRONTEND_PUBLIC_DIR, "login.html"))

    @app.get("/login", tags=["Frontend"], include_in_schema=False)
    async def serve_login_page():
        return FileResponse(os.path.join(FRONTEND_PUBLIC_DIR, "login.html"))

    @app.get("/dashboard", tags=["Frontend"], include_in_schema=False)
    async def serve_dashboard_page():
        return FileResponse(os.path.join(FRONTEND_PUBLIC_DIR, "dashboard.html"))

    # Mount StaticFiles ở root. Vì các route HTML đã được định nghĩa ở trên,
    # FastAPI sẽ ưu tiên chúng. Các request khác (vd: /js/login_ui.js)
    # sẽ được xử lý bởi StaticFiles.
    if os.path.isdir(FRONTEND_PUBLIC_DIR):
        app.mount("/", StaticFiles(directory=FRONTEND_PUBLIC_DIR), name="static")
    else:
        print(f"Cảnh báo: Không tìm thấy thư mục frontend tại '{FRONTEND_PUBLIC_DIR}'. Các file tĩnh sẽ không được phục vụ.")