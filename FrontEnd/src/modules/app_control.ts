/**
 * app_control.ts
 * Module này chịu trách nhiệm duy trì kết nối WebSocket với backend.
 * Nó xử lý các tác vụ sau:
 * 1. Thiết lập và tự động kết nối lại WebSocket.
 * 2. Gửi token xác thực (JWT) để định danh người dùng.
 * 3. Xử lý các sự kiện của kết nối (mở, đóng, lỗi) và thực hiện các hành động tương ứng,
 *    như chuyển hướng người dùng khi token hết hạn.
 */

import { WS_URL } from "../config";

// Logic để xử lý chuyển hướng ở trang gốc.
// Nếu người dùng truy cập vào trang gốc ('/') hoặc 'index.html', chuyển hướng họ đến trang đăng nhập.
// Điều này đảm bảo người dùng luôn bắt đầu từ một luồng có chủ đích.
if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    window.location.replace('/login');
}

class AppController {
    private ws: WebSocket | null = null;
    private url: string;
    private apiKey: string | null = null;
    private reconnectInterval: number = 5000; // Thử kết nối lại sau 5 giây
    private reconnectTimer: number | null = null;
    private isUnloading: boolean = false; // Cờ để xác định trang đang được đóng

    constructor(url: string) {
        this.url = url;
        // Lấy access token từ localStorage để xác thực với backend
        this.apiKey = localStorage.getItem('accessToken');

        // Lắng nghe sự kiện trước khi trang bị đóng (unload).
        // Đây là cách đáng tin cậy để biết người dùng đang đóng tab/trình duyệt.
        window.addEventListener('beforeunload', () => {
            console.log('[AppController] Page is unloading. Disconnecting WebSocket gracefully.');
            this.isUnloading = true; // Đặt cờ để ngăn việc kết nối lại
            if (this.ws) {
                // Vô hiệu hóa trình xử lý onclose để ngăn nó chạy logic kết nối lại
                this.ws.onclose = null;
                // Gửi một mã đóng chuẩn để báo cho server biết đây là hành động chủ ý
                this.ws.close(1000, "Page closed by user");
            }
        });

        this.connect();
    }

    private connect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        console.log(`[AppController] Connecting to ${this.url}...`);
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('[AppController] WebSocket connection established.');
            // Chuẩn bị payload để gửi, giúp dễ dàng debug
            const identifyPayload = {
                type: "IDENTIFY",
                role: "ui",
                apiKey: this.apiKey // Gửi kèm token JWT (có thể là null)
            };
            console.log('[AppController] Sending IDENTIFY message:', identifyPayload);
            // Gửi tin nhắn xác thực ngay khi kết nối thành công
            this.ws?.send(JSON.stringify(identifyPayload));
        };

        this.ws.onmessage = (event) => {
            // Hiện tại chưa cần xử lý message từ server, nhưng có thể mở rộng trong tương lai
            const message = JSON.parse(event.data);
            console.log('[AppController] Received message:', message);
        };

        this.ws.onclose = (event) => {
            // Thêm 'reason' để biết chính xác lý do server đóng kết nối
            console.warn(`[AppController] WebSocket disconnected. Code: ${event.code}. Reason: "${event.reason}"`);
            this.ws = null;

            // Nếu trang đang trong quá trình đóng, không thực hiện bất kỳ hành động kết nối lại nào.
            if (this.isUnloading) {
                console.log('[AppController] Unload in progress. Halting all reconnect attempts.');
                return;
            }

            // Mã 1000 với lý do cụ thể: Bị ngắt bởi một kết nối mới hơn.
            // Đây là trường hợp người dùng mở app lần 2, tạo ra tab mới. Tab cũ sẽ bị đóng kết nối.
            // Chúng ta không cần kết nối lại ở tab cũ này.
            if (event.code === 1000 && event.reason === "New connection established") {
                console.log('[AppController] Connection superseded by a new tab. Halting reconnect.');
                return; // Dừng, không kết nối lại.
            }

            // Mã lỗi 4001 là mã tùy chỉnh chúng ta đã định nghĩa ở backend
            // cho trường hợp token không hợp lệ hoặc đã hết hạn.
            if (event.code === 4001) {
                console.error('[AppController] Authentication failed. Token is invalid or expired.');
                
                // Xóa token đã hết hạn khỏi bộ nhớ
                localStorage.removeItem('accessToken');
                this.apiKey = null; // QUAN TRỌNG: Reset apiKey trong instance để lần kết nối lại không dùng token cũ
                
                // Chuyển hướng về trang đăng nhập để người dùng không bị kẹt.
                // Tránh chuyển hướng nếu đã ở trang đăng nhập để không tạo vòng lặp.
                if (window.location.pathname !== '/login' && window.location.pathname !== '/login.html') {
                    console.log('[AppController] Redirecting to login page due to invalid token.');
                    window.location.href = '/login';
                }
                // Không thử kết nối lại khi token đã sai.
                return;
            }
            
            // Đối với các lỗi khác (ví dụ: mất mạng), thử kết nối lại.
            console.log(`Reconnecting in ${this.reconnectInterval / 1000}s.`);
            this.reconnectTimer = window.setTimeout(() => this.connect(), this.reconnectInterval);
        };
 
        this.ws.onerror = (error) => {
            console.error('[AppController] WebSocket error:', error);
            // onclose sẽ được gọi ngay sau onerror, nên không cần xử lý reconnect ở đây
        };
    }
}

// Khởi tạo controller với URL WebSocket từ file cấu hình tập trung.
new AppController(WS_URL);

// Biến file này thành một module để cho phép `declare global`.