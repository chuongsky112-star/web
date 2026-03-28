/**
 * config.ts
 * Đây là nơi duy nhất chứa thông tin về địa chỉ của backend.
 * Khi deploy, bạn chỉ cần thay đổi URL ở đây.
 */
// QUAN TRỌNG: Thay thế URL này bằng URL backend của bạn trên Render.
const PROD_BACKEND_HOST = 'https://web-22fs.onrender.com';
// URL backend khi bạn chạy ở môi trường local để phát triển.
const DEV_BACKEND_HOST = 'http://127.0.0.1:5000';
// Tự động xác định môi trường để dùng đúng URL.
// Nếu hostname của trang web là 'localhost', ta dùng URL dev.
// Ngược lại, ta dùng URL production.
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const BACKEND_HOST = isDevelopment ? DEV_BACKEND_HOST : PROD_BACKEND_HOST;
console.log(`[Config] Environment: ${isDevelopment ? 'Development' : 'Production'}. Backend target: ${BACKEND_HOST}`);
// Tự động tạo ra các URL đầy đủ cho API và WebSocket
export const API_BASE_URL = BACKEND_HOST;
export const WS_URL = BACKEND_HOST.replace(/^http/, 'ws') + '/ws';
