/**
 * config.ts
 * Đây là nơi duy nhất chứa thông tin về địa chỉ của backend.
 * Khi deploy, bạn chỉ cần thay đổi URL ở đây.
 */

// QUAN TRỌNG: Thay thế URL này bằng URL backend của bạn trên Render.
const BACKEND_HOST = 'https://your-backend-on-render.com';

// Tự động tạo ra các URL đầy đủ cho API và WebSocket
export const API_BASE_URL = `${BACKEND_HOST}/api`;
export const WS_URL = BACKEND_HOST.replace(/^http/, 'ws') + '/ws';