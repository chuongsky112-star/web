from fastapi import Request

async def add_no_cache_headers(request: Request, call_next):
    """
    Thêm header vào mỗi response để yêu cầu trình duyệt
    luôn tải lại file mới nhất từ server, rất hữu ích khi đang phát triển.
    """
    response = await call_next(request)
    # Chỉ áp dụng cho các request không phải API để tránh ảnh hưởng đến các client khác
    if not request.url.path.startswith('/api') and not request.url.path.startswith('/ws'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response