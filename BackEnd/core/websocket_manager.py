import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
import asyncio
from core import security
# Cấu hình logging cơ bản để theo dõi các sự kiện WebSocket
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Quản lý các kết nối WebSocket đang hoạt động từ các extension và UI."""
    def __init__(self):
        # Lưu các kết nối extension: {uuid: websocket_object}
        self.active_extensions: Dict[str, WebSocket] = {}
        # Lưu kết nối UI, chỉ nên có một
        self.ui_connection: Optional[WebSocket] = None

    def _is_token_valid(self, token: Optional[str]) -> bool:
        """
        Kiểm tra xem token JWT có hợp lệ không.
        Hàm này gọi logic xác thực từ module `auth`.
        """
        if not token:
            return False
        try:
            # Sử dụng hàm xác thực đã có trong module `auth`.
            # Hàm này sẽ trả về None nếu token không hợp lệ.
            return security.decode_token(token) is not None
        except Exception as e: # Bắt các lỗi không mong muốn khác
            logger.debug(f"Token validation failed for UI websocket: {e}")
            return False

    async def connect(self, websocket: WebSocket, role: str, identifier: str = None, api_key: str = None):
        """Lưu trữ một kết nối đã được chấp nhận dựa trên vai trò."""
        if role == "extension" and identifier:
            # Nếu đã có kết nối với UUID này, đóng kết nối cũ
            if identifier in self.active_extensions:
                logger.warning(f"Duplicate extension connection for {identifier}. Closing old one.")
                await self.active_extensions[identifier].close(code=1000, reason="New connection established")
            self.active_extensions[identifier] = websocket
            logger.info(f"Extension connected: {identifier}")
        elif role == "ui":
            # --- LOGIC XÁC THỰC TOKEN CHO UI ---
            # Nếu có api_key (JWT token), nó PHẢI hợp lệ.
            # Nếu không có api_key, ta vẫn cho phép kết nối (dành cho trang login).
            if api_key and not self._is_token_valid(api_key):
                logger.warning("UI connection attempt with invalid or expired API Key. Closing.")
                await websocket.close(code=4001, reason="Invalid or expired API Key")
                return False

            if self.ui_connection:
                logger.warning("New UI connection received, closing the old one.")
                await self.ui_connection.close(code=1000, reason="New connection established")
            self.ui_connection = websocket
            logger.info("UI connected.")
        else:
            logger.warning(f"Unknown role or missing identifier for connection: {role}")
            await websocket.close(code=1008, reason="Invalid identification")
            return False
        return True

    def disconnect(self, websocket: WebSocket):
        """Xóa một kết nối khi nó bị ngắt."""
        # Tìm và xóa trong danh sách extension
        ext_id_to_remove = None
        for ext_id, ws in self.active_extensions.items():
            if ws == websocket:
                ext_id_to_remove = ext_id
                break
        if ext_id_to_remove:
            del self.active_extensions[ext_id_to_remove]
            logger.info(f"Extension disconnected: {ext_id_to_remove}")
            return

        # Kiểm tra và xóa kết nối UI
        if self.ui_connection == websocket:
            self.ui_connection = None
            logger.info("UI disconnected.")
            return

    async def send_to_extension(self, uuid: str, message: Dict[str, Any]):
        """Gửi một tin nhắn JSON tới một extension cụ thể bằng UUID."""
        if uuid in self.active_extensions:
            websocket = self.active_extensions[uuid]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Could not send message to extension {uuid}: {e}")
        else:
            logger.warning(f"Attempted to send message to non-existent extension: {uuid}")

    async def send_to_ui(self, message: Dict[str, Any]):
        """Gửi một tin nhắn JSON tới UI."""
        if self.ui_connection and self.ui_connection.client_state == 'CONNECTED':
            try:
                await self.ui_connection.send_json(message)
            except Exception as e:
                logger.error(f"Could not send message to UI: {e}")
        else:
            # Có thể buffer tin nhắn nếu UI không kết nối
            logger.warning("Attempted to send message to UI, but no UI is connected.")

    async def broadcast_to_extensions(self, message: Dict[str, Any]):
        """Gửi tin nhắn tới tất cả các extension đang kết nối."""
        if not self.active_extensions:
            return
        
        websockets_to_send = [ws for ws in self.active_extensions.values() if ws.client_state == 'CONNECTED']
        if not websockets_to_send:
            return

        tasks = [ws.send_json(message) for ws in websockets_to_send]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error broadcasting to an extension: {result}")

# Tạo một instance duy nhất của ConnectionManager để quản lý tất cả các kết nối
manager = ConnectionManager()

# Tạo một APIRouter để chứa endpoint WebSocket.
# Điều này giúp mã nguồn được module hóa và dễ dàng tích hợp vào app chính.
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint chính cho kết nối WebSocket từ Chrome Extension và Web UI.
    Lắng nghe tin nhắn IDENTIFY để đăng ký, sau đó xử lý các tin nhắn đến.
    """
    client_role = None
    client_id = None

    # Chấp nhận kết nối ngay lập tức. Đây phải là hành động đầu tiên.
    await websocket.accept()

    try:
        # Chờ tin nhắn IDENTIFY đầu tiên để xác định client
        data = await websocket.receive_json()
        msg_type = data.get("type")
        role = data.get("role")

        if msg_type == "IDENTIFY":
            client_role = role
            if role == "extension":
                client_id = data.get("uuid")
                if not await manager.connect(websocket, role="extension", identifier=client_id):
                    return # Kết nối thất bại, đã được đóng trong manager.connect
            elif role == "ui":
                client_id = "ui_client" # Gán một id tượng trưng
                api_key = data.get("apiKey") # JWT token
                if not await manager.connect(websocket, role="ui", api_key=api_key):
                    return # Kết nối thất bại
            else:
                logger.warning(f"Connection received with unknown role: {role}. Closing.")
                await websocket.close(code=1008)
                return
        else:
            logger.warning("Connection received without IDENTIFY message. Closing.")
            await websocket.close(code=1008)
            return

        # Vòng lặp chính để xử lý tin nhắn
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if client_role == "extension":
                # Xử lý tin nhắn từ Extension
                if msg_type == "LOG_BATCH":
                    # Chuyển tiếp log tới UI
                    await manager.send_to_ui(message)
                elif msg_type == "PING":
                    await websocket.send_json({"type": "PONG"})
                else:
                    # TODO: Chuyển tiếp tin nhắn đến các hệ thống xử lý khác
                    logger.info(f"Received from extension {client_id}: {message}")

            elif client_role == "ui":
                # Xử lý tin nhắn từ UI
                if msg_type == "CLEAR_LOG":
                    logger.info("Received CLEAR_LOG command from UI.")
                    # Gửi lệnh reset tới tất cả extensions
                    await manager.broadcast_to_extensions({"action": "reset"})
                    # Gửi lại cho UI để xác nhận và dọn dẹp view
                    await manager.send_to_ui({"type": "CLEAR_LOG"})
                elif msg_type == "PING":
                     await websocket.send_json({"type": "PONG"})
                else:
                    logger.info(f"Received from UI: {message}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"An error occurred with websocket client {client_id} ({client_role}): {e}")
        # Đảm bảo kết nối được đóng và xóa khỏi trình quản lý trong trường hợp có lỗi bất ngờ
        if websocket.client_state != 'DISCONNECTED':
            await websocket.close(code=1011) # Lỗi nội bộ
        manager.disconnect(websocket)