import secrets
from fastapi import Header, HTTPException, status

# 1. Tạo một "Chìa khóa bí mật" duy nhất ngay khi module này được import (tức là khi app khởi động)
APP_SECRET = secrets.token_hex(32)

async def verify_app_secret(x_app_secret: str = Header(None)):
    """
    Một dependency của FastAPI để kiểm tra custom header 'X-App-Secret'.
    Hàm này sẽ được gắn vào các API endpoint để bảo vệ chúng.
    """
    # 2. So sánh header từ client với chìa khóa bí mật trên server
    if not x_app_secret or not secrets.compare_digest(x_app_secret, APP_SECRET):
        # Dùng compare_digest để chống lại tấn công "timing attack"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing application secret token."
        )

    return True