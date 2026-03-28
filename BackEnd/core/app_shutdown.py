import os
import signal
import threading
import logging
import sys

logger = logging.getLogger(__name__)

def _shutdown():
    """
    Thực hiện hành động tắt server.
    """
    logger.info("Shutting down server now.")

    # Quay trở lại sử dụng os._exit(0).
    # Đây là phương pháp thoát tiến trình ngay lập tức và đã được chứng minh là hoạt động
    # hiệu quả trong file desktop_utils.py để đóng các instance bị trùng lặp.
    # Nó đảm bảo ứng dụng .exe được đóng hoàn toàn trên Windows mà không gặp lỗi.
    os._exit(0)

def schedule_shutdown(delay: float = 2.0) -> threading.Timer:
    """
    Lên lịch tắt server sau một khoảng thời gian chờ.
    Trả về đối tượng Timer để có thể hủy bỏ.
    """
    logger.info(f"Server will shut down in {delay} seconds if UI does not reconnect.")
    shutdown_timer = threading.Timer(delay, _shutdown)
    shutdown_timer.start()
    return shutdown_timer