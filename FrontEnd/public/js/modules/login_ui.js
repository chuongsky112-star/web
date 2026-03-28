"use strict";
// IIFE (Immediately Invoked Function Expression) để chạy ngay lập tức.
// "Bảo vệ" cho trang đăng nhập: nếu người dùng đã có token (đã đăng nhập),
// tự động chuyển hướng họ đến trang dashboard để tránh việc đăng nhập lại không cần thiết.
(function protectLoginPage() {
    if (localStorage.getItem('accessToken')) {
        console.log('Đã đăng nhập, chuyển hướng tới dashboard...');
        window.location.replace('/dashboard');
    }
})();
document.addEventListener('DOMContentLoaded', () => {
    // Lấy tất cả các element cần thiết từ DOM
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-btn');
    const messageBox = document.getElementById('login-message');
    const formTitle = document.getElementById('form-title');
    const togglePassword = document.getElementById('toggle-password');
    // Kiểm tra chặt chẽ để đảm bảo tất cả các element đều tồn tại và đúng loại.
    // Đây là một "Type Guard" - nếu các element không tồn tại, code sẽ dừng lại.
    if (!(loginForm instanceof HTMLFormElement) ||
        !(usernameInput instanceof HTMLInputElement) ||
        !(passwordInput instanceof HTMLInputElement) ||
        !(loginButton instanceof HTMLButtonElement) ||
        !(messageBox instanceof HTMLDivElement) ||
        !(formTitle instanceof HTMLHeadingElement) ||
        !(togglePassword instanceof HTMLSpanElement)) {
        console.error('Lỗi: Không tìm thấy các thành phần của form đăng nhập. Vui lòng kiểm tra lại ID trong file HTML.');
        return; // Dừng thực thi nếu có lỗi
    }
    // Vô hiệu hóa validation mặc định của trình duyệt để sử dụng validation tùy chỉnh.
    loginForm.noValidate = true;
    formTitle.textContent = 'Đăng nhập';
    loginButton.textContent = 'Tiếp tục';
    togglePassword.addEventListener('click', () => {
        // Chuyển đổi thuộc tính 'type' của ô nhập mật khẩu
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        // Thay đổi icon con mắt
        // Bạn có thể dùng icon từ thư viện (Font Awesome, etc.) hoặc emoji như ở đây
        togglePassword.textContent = type === 'password' ? '👁️' : '🙈';
    });
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Ngăn form submit theo cách truyền thống
        // Xóa thông báo cũ
        messageBox.textContent = '';
        messageBox.className = 'message-box';
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        if (!username || !password) {
            messageBox.textContent = 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.';
            messageBox.className = 'message-box error';
            console.warn('Username or password missing.');
            return;
        }
        // --- THAY ĐỔI ĐỂ KIỂM TRA ---
        // Hiển thị trạng thái đang xử lý một cách "sống động" hơn.
        // Nếu bạn thấy các dòng chữ này thay đổi, điều đó có nghĩa là file TypeScript của bạn
        // đã được biên dịch và tải vào trình duyệt thành công!
        loginButton.disabled = true;
        messageBox.className = 'message-box info';
        const loadingMessages = [
            "Đang gửi tín hiệu lên vũ trụ...",
            "Hỏi ý kiến các chuyên gia...",
            "Kiểm tra xem bạn có phải robot không...",
            "Xác thực, vui lòng chờ..."
        ];
        let messageIndex = 0;
        messageBox.textContent = loadingMessages[messageIndex];
        const loadingInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % loadingMessages.length;
            messageBox.textContent = loadingMessages[messageIndex];
        }, 800);
        // --- KẾT THÚC THAY ĐỔI ---
        // --- GỌI API THẬT ---
        // --- LOGIC ĐĂNG NHẬP ---
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-App-Secret': window.APP_SECRET || '', // Gửi chìa khóa bí mật trong header
            },
            body: JSON.stringify({ username, password }),
        })
            .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                // Nếu server trả về lỗi (4xx, 5xx), ném ra lỗi để khối .catch() xử lý
                throw new Error(data.message || 'Có lỗi xảy ra từ server.');
            }
            return data; // Chuyển dữ liệu thành công xuống cho .then() tiếp theo
        })
            .then((data) => {
            clearInterval(loadingInterval); // Dừng thay đổi message khi có kết quả
            // --- LƯU TOKEN ---
            // Nếu đăng nhập thành công và có token, lưu nó vào localStorage.
            // localStorage là bộ nhớ của trình duyệt, nó sẽ không bị mất khi bạn tải lại trang.
            if (data.success && data.access_token) {
                localStorage.setItem('accessToken', data.access_token);
            }
            messageBox.textContent = data.message;
            messageBox.className = 'message-box success';
            // Đăng nhập thành công, chuyển hướng đến trang chính sau 1 giây
            setTimeout(() => {
                window.location.href = '/dashboard'; // Chuyển hướng đến trang dashboard (URL không có .html)
            }, 1000);
        })
            .catch((error) => {
            clearInterval(loadingInterval); // Dừng thay đổi message khi có lỗi
            console.error('Login Error:', error);
            messageBox.textContent = error.message;
            messageBox.className = 'message-box error';
            loginButton.disabled = false;
        });
    });
});
