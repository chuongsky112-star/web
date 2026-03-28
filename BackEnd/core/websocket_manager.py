import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from core import security

# Cấu hình logging cơ bản để theo dõi các sự kiện WebSocket
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tạo một APIRouter để chứa endpoint WebSocket.
# Điều này giúp mã nguồn được module hóa và dễ dàng tích hợp vào app chính.
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Lấy token từ query parameters của URL
    token = websocket.query_params.get("token")
    
    # Xác thực token
    payload = security.decode_token(token)
    if payload is None:
        logger.warning("WebSocket connection attempt with invalid token.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("user_id")
    logger.info(f"WebSocket client connected: user_id={user_id}")

    try:
        while True:
            data = await websocket.receive_text()
            # Ví dụ: Xử lý và phản hồi lại tin nhắn
            logger.info(f"Received message from user {user_id}: {data}")
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: user_id={user_id}")
    except Exception as e:
        logger.error(f"An error occurred with WebSocket client {user_id}: {e}")