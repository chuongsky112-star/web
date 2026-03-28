from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chuỗi kết nối bạn đã cung cấp
DATABASE_URL = "postgresql://chembet_user:admin@localhost:5432/chembet_db"

# Tạo "engine" - Cổng giao tiếp chính với database
engine = create_engine(DATABASE_URL)

# Tạo một lớp SessionLocal. Mỗi instance của lớp này sẽ là một phiên làm việc (session) với database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo một lớp Base. Các model (bảng dữ liệu) của chúng ta sẽ kế thừa từ lớp này.
Base = declarative_base()

# Hàm này sẽ được dùng như một dependency trong các API endpoint
# để cung cấp một phiên làm việc với DB và đảm bảo nó được đóng lại sau khi dùng xong.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
