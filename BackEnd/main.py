import uvicorn
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Import các module
from core import websocket_manager
from api import auth
from core import security
from config import middleware
from db.database import engine, Base

# Khởi tạo ứng dụng FastAPI.
app = FastAPI()

# --- Cấu hình CORS (Cross-Origin Resource Sharing) ---
# Đây là bước BẮT BUỘC khi tách frontend và backend ra 2 domain khác nhau.
# Nó cho phép trình duyệt ở frontend (vd: your-app.netlify.app)
# có thể gửi yêu cầu đến backend (vd: your-api.onrender.com).
origins = [
    "https://gleaming-flan-0a1881.netlify.app", # URL production của Netlify
    "http://localhost", # Dành cho phát triển local
    "http://localhost:8080", # Thêm các port dev phổ biến nếu cần
    "http://127.0.0.1", # Dành cho phát triển local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Đăng ký Middleware ---
app.middleware("http")(middleware.add_no_cache_headers)

# --- Đăng ký các API Routers ---
# Các route API cụ thể phải được đăng ký trước route "catch-all" của StaticFiles.
app.include_router(websocket_manager.router)
app.include_router(auth.router, prefix="/api") # Router cho /login, /register

# Tạo bảng trong database (nếu chưa tồn tại) khi ứng dụng khởi động
Base.metadata.create_all(bind=engine)

# Endpoint ví dụ để kiểm tra auth guard
@app.get("/api/me", tags=["Users"])
def read_users_me(current_user: dict = Depends(security.get_current_user)):
    return current_user

if __name__ == "__main__":
    # Cấu hình cho deployment trên các nền tảng như Render:
    # - Host: "0.0.0.0" để server có thể được truy cập từ bên ngoài container.
    # - Port: Đọc từ biến môi trường `PORT` do nền tảng cung cấp, mặc định là 5000 cho local dev.
    APP_HOST = "0.0.0.0"
    APP_PORT = int(os.environ.get("PORT", 5000))

    # Chạy server Uvicorn với cấu hình cho deployment.
    # log_level="info" là lựa chọn tốt cho môi trường production.
    uvicorn.run(app, host=APP_HOST, port=APP_PORT, log_level="info")