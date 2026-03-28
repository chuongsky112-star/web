import logging
# Import engine và Base từ module database của bạn
from db.database import engine, Base
# Import các model của bạn. Việc import này là BẮT BUỘC để SQLAlchemy
# nhận biết được các model và tạo bảng tương ứng.
from model import models

# Cấu hình logging để xem thông báo
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """
    Hàm này sẽ tạo tất cả các bảng được định nghĩa trong các model
    (kế thừa từ Base) vào trong database đã được kết nối bởi engine.
    """
    try:
        logger.info("Đang chuẩn bị tạo bảng trong database...")
        # Lệnh này sẽ tạo tất cả các bảng (nếu chúng chưa tồn tại)
        Base.metadata.create_all(bind=engine)
        logger.info("Tất cả các bảng đã được tạo thành công (hoặc đã tồn tại).")
    except Exception as e:
        logger.error(f"Đã xảy ra lỗi khi tạo bảng: {e}")

if __name__ == "__main__":
    # Chạy hàm khởi tạo khi script này được thực thi trực tiếp
    init_database()