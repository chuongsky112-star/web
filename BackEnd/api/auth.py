from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.security import verify_app_secret
from sqlalchemy.orm import Session

from db.database import get_db # Import the dependency
from model.user import User     # Import the User model

# --- Cấu hình JWT ---
SECRET_KEY = "a_very_secret_key_for_your_local_app" # Trong thực tế, hãy dùng key phức tạp hơn và lưu trong secrets
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token hết hạn sau 30 phút

# --- Cấu hình Passlib ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Khởi tạo router cho các endpoint xác thực
router = APIRouter(
    prefix="/api",  # Tiền tố chung cho các route trong file này
    tags=["Authentication"],  # Gom nhóm các API trong giao diện Swagger/OpenAPI
)

# --- Pydantic Models for Request Body Validation ---
class LoginRequest(BaseModel):
    username: str
    password: str

def get_password_hash(password: str) -> str:
    """Hashes a password using the configured context."""
    # Thuật toán bcrypt có giới hạn mật khẩu là 72 byte.
    # Để tránh lỗi ValueError từ passlib, chúng ta cần cắt ngắn mật khẩu.
    # Quan trọng: Phải mã hóa chuỗi thành bytes trước khi cắt để đảm bảo
    # độ dài byte là chính xác, vì một ký tự Unicode có thể chiếm nhiều hơn 1 byte.
    password_bytes = password.encode('utf-8')
    # passlib's hash() sẽ ném ra lỗi nếu mật khẩu dài hơn 72 byte.
    # Chúng ta phải tự cắt nó để ngăn chặn lỗi.
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed one."""
    # Mặc dù passlib's verify() tự động cắt mật khẩu dài, việc thực hiện
    # một cách tường minh ở đây giúp logic nhất quán với hàm get_password_hash
    # và làm cho code dễ hiểu hơn, tránh các hành vi ngầm.
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # pwd_context.verify có thể xử lý secret là bytes hoặc string.
    # Nó sẽ so sánh hash của password_bytes với hashed_password đã lưu.
    return pwd_context.verify(password_bytes, hashed_password)

def create_access_token(data: dict):
    """Tạo một JSON Web Token (JWT) mới."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_for_websocket(token: str):
    """
    Xác thực một token JWT. Ném ra Exception nếu token không hợp lệ.
    Hàm này được thiết kế để sử dụng bên ngoài các endpoint HTTP (ví dụ: WebSocket).
    """
    try:
        if not token:
            raise JWTError("Token is missing")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Ném ra lỗi nếu payload không chứa thông tin người dùng
            raise JWTError("Token payload is invalid")
    except JWTError as e:
        # Ném lại lỗi để nơi gọi (websocket_manager) có thể xử lý
        raise e

@router.post("/login", dependencies=[Depends(verify_app_secret)])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Tìm kiếm người dùng trong database bằng username
    user = db.query(User).filter(User.username == login_data.username).first()

    # 1. Kiểm tra người dùng có tồn tại không
    # 2. Nếu có, kiểm tra mật khẩu có khớp không
    # Gộp cả hai trường hợp (không tìm thấy user hoặc sai mật khẩu) vào một thông báo lỗi
    # để tăng cường bảo mật, tránh việc hacker có thể dò ra username nào đã tồn tại.
    if not user or not verify_password(login_data.password, user.hashed_password):
        return JSONResponse(status_code=401, content={"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng."})

    # Nếu mọi thứ đều đúng, tạo token và trả về
    access_token = create_access_token(data={"sub": user.username})
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Đăng nhập thành công!", "access_token": access_token}
    )