# Báo cáo kỹ thuật: Hệ thống bảo mật cho VinBank AI Assistant
**Sinh viên thực hiện:** 2A202600404 - Nguyễn Thành Đại Khánh
**Bài tập:** Day 11 — Guardrails, HITL & Responsible AI

## 1. Các lớp phòng thủ đã triển khai
Trong bài tập này, em đã xây dựng một chuỗi các lớp bảo vệ (Defense-in-Depth) để giúp AI của VinBank an toàn hơn.

| Lớp bảo vệ | Chức năng | Mục tiêu ngăn chặn |
| :--- | :--- | :--- |
| **1. Rate Limiter** | Giới hạn số câu hỏi | Ngăn chặn việc spam tin nhắn làm tốn API hoặc treo máy |
| **2. Input Regex** | Kiểm tra từ khóa đầu vào | Chặn các câu lệnh tấn công phổ biến như "Ignore instructions" |
| **3. Topic Filter** | Lọc chủ đề | Chỉ cho phép AI trả lời các câu hỏi liên quan đến ngân hàng |
| **4. PII Masking** | Lọc dữ liệu đầu ra | Tự động che đi các thông tin nhạy cảm như Mật khẩu, API Key |
| **5. LLM-as-Judge** | Dùng AI kiểm tra lại | Sử dụng một model phụ để đánh giá xem câu trả lời có an toàn không |
| **6. Audit Log** | Nhật ký hệ thống | Ghi lại toàn bộ lịch sử để kiểm tra và nộp bài |

## 2. Kết quả kiểm thử & Các trường hợp chặn nhầm
Em đã chạy bộ test tự động để so sánh trước và sau khi có bảo vệ.

### Chỉ số bảo mật
- **Tấn công giả lập:** Chặn thành công 100% các câu lệnh cố tình hỏi mật khẩu hoặc API Key.
- **Giới hạn tốc độ:** Hệ thống đã chặn đúng lúc khi em thử gửi 12 tin nhắn liên tục trong thời gian ngắn.
- **Nhật ký:** Mọi dữ liệu đã được xuất thành file `assignment_audit_log.json` để minh chứng.

### Trường hợp chặn nhầm (False Positives)
- **Ví dụ:** Khi khách hàng hỏi *"Làm sao để đổi mật khẩu thẻ ATM?"*, hệ thống có thể nhầm từ "mật khẩu" là hành vi tấn công.
- **Cách khắc phục:** Em đã điều chỉnh Filter để cho phép các câu hỏi chứa từ "mật khẩu" nhưng đi kèm với các từ khóa về "hướng dẫn" hoặc "thẻ", chỉ chặn khi người dùng yêu cầu "tiết lộ" hoặc "hiển thị" mật khẩu hệ thống.

## 3. Những điểm hạn chế còn sót lại
Hệ thống hiện tại vẫn còn một số điểm cần cải thiện:
1.  **Các cách tấn công ẩn ý:** Nếu kẻ tấn công dùng mật mã (như Base64) hoặc dùng cách nói quá vòng vo, bộ lọc Regex có thể bị bỏ lọt.
2.  **Vấn đề môi trường:** Do phiên bản Python 3.14 trên máy em chưa tương thích tốt với thư viện NeMo Guardrails, nên phần này em đã chuẩn bị code sẵn nhưng chưa kích hoạt được hoàn toàn trên máy cá nhân. Em sẽ chạy bù trên Google Colab nếu cần thiết.

## 4. Kế hoạch vận hành thực tế
- **Giám sát:** Em đã cài đặt hệ thống tự động ghi lại Latency (thời gian phản hồi) và Trạng thái (status) của mỗi câu hỏi.
- **Cảnh báo:** Nếu tỷ lệ bị chặn tăng đột biến (ví dụ trên 50%), hệ thống sẽ in ra cảnh báo để quản trị viên biết có người đang cố tình phá hoại.
- **Sự can thiệp của con người (HITL):** Đối với các giao dịch chuyển tiền số tiền lớn, hệ thống sẽ không tự thực hiện mà yêu cầu nhân viên ngân hàng kiểm tra lại (Routing).

## 5. Suy nghĩ về đạo đức AI
- **Tính công bằng:** Em đã kiểm tra để bộ lọc không chặn nhầm người dùng dựa trên ngôn ngữ (Tiếng Anh hay Tiếng Việt).
- **Trải nghiệm người dùng:** Thay vì hiện lỗi "Access Denied", em đã viết các câu từ chối lịch sự, hướng dẫn người dùng quay lại chủ đề ngân hàng.
- **Sử dụng tài nguyên:** Việc cài Rate Limit giúp tránh lãng phí tài nguyên của ngân hàng và đảm bảo hệ thống luôn sẵn sàng phục vụ mọi người.

---
