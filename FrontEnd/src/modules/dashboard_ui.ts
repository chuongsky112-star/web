// --- "BẢO VỆ" CHO TRANG DASHBOARD ---

import { connectWebSocket } from "./app_control";

// IIFE (Immediately Invoked Function Expression) để chạy ngay lập tức
(function checkAuthentication() {
    const accessToken = localStorage.getItem('accessToken');

    // Nếu không tìm thấy "vé" (token), lập tức chuyển hướng về trang đăng nhập.
    if (!accessToken) {
        console.warn('Chưa đăng nhập! Đang chuyển hướng về trang login...');
        // Dùng replace để người dùng không thể nhấn "Back" quay lại trang dashboard.
        window.location.replace('/login'); // Chuyển hướng về URL không có .html
    } else {
        // Nếu đã xác thực, khởi tạo kết nối WebSocket
        connectWebSocket(accessToken);
    }
})(); // Dấu () ở cuối để gọi hàm ngay lập tức

// --- LOGIC CỦA TRANG DASHBOARD SAU KHI ĐÃ XÁC THỰC ---

document.addEventListener('DOMContentLoaded', () => {
    const logoutButton = document.getElementById('logout-btn');

    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            // Xóa "vé" khỏi bộ nhớ
            localStorage.removeItem('accessToken');
            console.log('Đã đăng xuất. Xóa token thành công.');
            window.location.href = '/login'; // Chuyển hướng về URL không có .html
        });
    }
});