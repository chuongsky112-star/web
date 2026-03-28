from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    """
    Model SQLAlchemy cho bảng 'users'.
    Bảng này sẽ lưu trữ thông tin đăng nhập của người dùng.
    """
    __tablename__ = "users"

    # Cột ID, khóa chính, tự động tăng
    id = Column(Integer, primary_key=True, index=True)
    
    # Tên đăng nhập, phải là duy nhất và không được để trống
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Mật khẩu đã được băm, không được để trống
    hashed_password = Column(String, nullable=False)