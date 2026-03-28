// Đây là file để mở rộng các kiểu dữ liệu toàn cục cho toàn bộ dự án.
// Theo quy ước, nó thường được đặt tên là `globals.d.ts` hoặc `types.d.ts`.

declare global {
    interface Window {
        APP_SECRET: string;
    }
}

// Dòng export rỗng này là cần thiết để TypeScript coi file này là một module,
// đây là một yêu cầu để có thể mở rộng phạm vi toàn cục (global scope).
// Vì đây là file .d.ts, nó sẽ không được biên dịch ra JavaScript và sẽ không gây ra lỗi runtime.
export {};