from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.user import User
from schemas.user import UserCreate, UserLogin
from core import security

router = APIRouter(tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem user đã tồn tại chưa
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Tạo user mới
    hashed_password = security.get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "message": "User created successfully"}

@router.post("/login")
def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    # Tìm kiếm người dùng trong database bằng username
    user = db.query(User).filter(User.username == form_data.username).first()

    # Nếu user không tồn tại hoặc mật khẩu sai, trả về lỗi
    # Sử dụng JSONResponse để trả về cấu trúc {success, message} mà frontend đang mong đợi
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng."}
        )

    # Tạo access token với payload chứa id và role
    token_data = {"sub": user.username, "user_id": user.id, "role": user.role}
    access_token = security.create_access_token(data=token_data)

    # Trả về response tương thích với frontend
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Đăng nhập thành công!", "access_token": access_token}
    )