/**
 * app_control.ts
 * Module này quản lý kết nối WebSocket theo chuẩn production.
 * - Tự động kết nối lại với chiến lược exponential backoff.
 * - Xử lý các lỗi kết nối và xác thực.
 */
import { CONFIG } from "../config";
let socket = null;
let reconnectDelay = 1000; // Bắt đầu với 1 giây
const MAX_RECONNECT_DELAY = 30000; // Tối đa 30 giây
export function connectWebSocket(token) {
    // Nếu đã có kết nối, không làm gì cả
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log('WebSocket is already connected.');
        return;
    }
    // Xây dựng URL với token trong query params
    const wsUrl = `${CONFIG.WS_BASE_URL}/ws?token=${token}`;
    console.log(`[WebSocket] Connecting to: ${CONFIG.WS_BASE_URL}/ws`);
    socket = new WebSocket(wsUrl);
    socket.onopen = () => {
        console.log('✅ [WebSocket] Connection established.');
        // Reset lại delay khi kết nối thành công
        reconnectDelay = 1000;
    };
    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('📩 [WebSocket] Message received:', data);
            // TODO: Xử lý các message từ server ở đây
        }
        catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    };
    socket.onerror = (error) => {
        console.error('❌ [WebSocket] Error:', error);
        // onerror sẽ luôn theo sau bởi onclose, nên logic reconnect sẽ nằm trong onclose
    };
    socket.onclose = (event) => {
        console.warn(`⚠️ [WebSocket] Disconnected. Code: ${event.code}.`);
        // Mã 1008 (Policy Violation) thường được dùng cho lỗi xác thực
        if (event.code === 1008) {
            console.error('Authentication failed. Redirecting to login.');
            localStorage.removeItem('accessToken');
            window.location.replace('/login');
            return; // Không kết nối lại
        }
        // Logic kết nối lại với exponential backoff
        console.log(`Reconnecting in ${reconnectDelay / 1000}s...`);
        setTimeout(() => connectWebSocket(token), reconnectDelay);
        // Tăng delay cho lần kết nối lại tiếp theo
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
    };
}
