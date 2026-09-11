# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 4 tiếng
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.5, 1.0 và 1.5 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2–3 câu)
> *Khi temperature tăng từ 0.0 lên 1.5, câu trả lời chuyển dần từ tính xác định, chuẩn mực sang đa dạng và bất ngờ hơn. Ở mức 0.0 và 0.5, model chọn các từ ngữ an toàn và sự thật phổ biến (như vị trí địa lý, xuất khẩu gạo/cà phê). Ở mức 1.0 đến 1.5, cấu trúc câu sáng tạo hơn, dẫn chứng phong phú hơn nhưng mức 1.5 bắt đầu xuất hiện câu từ kém mạch lạc và có nguy cơ ảo giác (hallucination).*

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> *Tôi sẽ đặt temperature khoảng 0.0 đến 0.2 cho chatbot hỗ trợ khách hàng. Chatbot CSKH yêu cầu tính chính xác cao, nội dung nhất quán và tuân thủ chặt chẽ tài liệu/chính sách của doanh nghiệp, việc hạ thấp temperature giúp hạn chế tối đa việc model tự bịa đặt thông tin sai lệch.*

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 3 lần,
mỗi lần trung bình ~350 token đầu ra.

**Ước tính GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này? Nêu một
trường hợp GPT-4o xứng đáng với chi phí và một trường hợp nên dùng mini:**
> *Dựa theo bảng giá ($0.010/1k token của GPT-4o so với $0.0006/1k token của GPT-4o-mini), GPT-4o đắt hơn khoảng 16.67 lần cho token đầu ra. Trường hợp nên dùng GPT-4o: Tác vụ đòi hỏi lập luận logic phức tạp, viết code chuyên sâu hoặc tổng hợp báo cáo tài chính/pháp lý cần độ chính xác tối đa. Trường hợp nên dùng mini: Tác vụ phân loại ý định người dùng (intent classification), tóm tắt tin tức đơn giản hoặc trả lời câu hỏi phổ thông theo mẫu có sẵn.*

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích blockchain là gì?"** nhưng hai system prompt khác nhau:
- "Bạn là giáo viên tiểu học, giải thích thật đơn giản cho trẻ 8 tuổi."
- "Bạn là chuyên gia tài chính, trả lời chuyên sâu bằng thuật ngữ kỹ thuật."

**Hai phản hồi khác nhau như thế nào (độ dài, từ vựng, ví dụ)? System prompt
ảnh hưởng đến hành vi model ra sao?** (3–4 câu)
> *Phản hồi cho trẻ em dùng từ ngữ sinh động, ví dụ so sánh blockchain như "cuốn sổ tay chung của cả lớp", câu văn ngắn gọn và tránh thuật ngữ trừu tượng. Ngược lại, phản hồi tài chính giải thích bằng các khái niệm kỹ thuật như "sổ cái phân tán (distributed ledger)", "cơ chế đồng thuận (consensus mechanism)", và "mã hóa cryptographic". System prompt đóng vai trò như bộ lọc ngữ cảnh, trực tiếp điều chỉnh persona, độ sâu kiến thức và phong cách hành văn của model cho đúng đối tượng người nghe.*

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~100 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Vì sao tiếng Việt thường tốn
nhiều token hơn tiếng Anh cùng độ dài?**
> *Số token thực tế đếm bằng tiktoken thường cao hơn con số ước lượng (số từ / 0.75) khoảng 20% đến 40%. Tiếng Việt tốn nhiều token hơn tiếng Anh cùng độ dài vì các thuật toán tokenization (như BPE) được huấn luyện chủ yếu trên văn bản tiếng Anh; khi gặp tiếng Việt, các ký tự có dấu thanh và phụ âm ghép thường bị phân tách thành nhiều byte/token riêng lẻ thay vì gộp thành một token nguyên vẹn.*

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì
non-streaming lại phù hợp hơn?** (1 đoạn văn)
> *Streaming quan trọng nhất trong các giao diện hội thoại tương tác trực tiếp (chatbots, CLI assistant), giúp giảm thời gian chờ phản hồi đầu tiên (Time to First Token - TTFT) và tạo cảm giác phản hồi tức thì cho người dùng. Ngược lại, non-streaming phù hợp hơn với các tác vụ xử lý hàng loạt (batch processing), xử lý ngầm ở backend (background job), hoặc khi cần gọi function calling và trả về định dạng có cấu trúc như JSON schema hoàn chỉnh trước khi phân tích tiếp.*

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**So với delay cố định (ví dụ luôn chờ 1 giây), exponential backoff có lợi
thế gì khi API bị quá tải? Điều gì xảy ra nếu hàng nghìn client cùng retry
với delay cố định giống nhau?**
> *Exponential backoff giúp giãn cách thời gian giữa các lần thử lại (0.1s, 0.2s, 0.4s...), tạo thời gian đệm để hệ thống phía server kịp giải phóng tài nguyên và hồi phục. Nếu dùng delay cố định và hàng nghìn client cùng retry tại một thời điểm, hiện tượng bão yêu cầu ("thundering herd problem") sẽ xảy ra, khiến server vừa khởi động lại đã ngay lập tức bị quá tải sập tiếp.*

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Bạn chọn persona gì cho trợ lý của mình? Viết lại system prompt đó và giải
thích 1–2 lựa chọn từ ngữ quan trọng trong prompt (ví dụ: vì sao yêu cầu
"trả lời ngắn gọn", vì sao chỉ định ngôn ngữ...):**
> *System prompt: "Bạn là trợ giảng thân thiện của khóa học AI, chuyên giải thích ngắn gọn, súc tích bằng tiếng Việt và dùng ví dụ thực tế." Lựa chọn từ ngữ quan trọng: "ngắn gọn, súc tích": Để kiểm soát độ dài phản hồi, tiết kiệm token output và chi phí API. "bằng tiếng Việt": Đảm bảo tính nhất quán ngôn ngữ, tránh trường hợp prompt tiếng Anh xen lẫn khiến model trả lời song ngữ. "trợ giảng thân thiện": Tạo giọng điệu gần gũi, khích lệ người học đặt câu hỏi.*

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn hiện có hạn chế lớn nhất là gì (ví dụ: history chỉ 3 lượt,
không có bộ nhớ dài hạn, không kiểm duyệt nội dung...)? Đề xuất một cải
thiện cụ thể và mô tả ngắn cách triển khai:**
> *Hạn chế lớn nhất: Bộ nhớ ngắn hạn chỉ lưu được 3 lượt hội thoại gần nhất (history[-6:]), khiến bot quên hoàn toàn thông tin người dùng đã chia sẻ từ các lượt chat trước đó. Đề xuất cải thiện: Tích hợp cơ chế Tóm tắt bộ nhớ (Memory Summarization). Mỗi khi history vượt quá 6 messages, thay vì cắt bỏ trực tiếp, ta cho model chạy ngầm một lượt để tóm tắt các điểm chính của đoạn hội thoại cũ thành một đoạn văn ngắn và chèn đoạn tóm tắt đó vào ngay sau system prompt để giữ ngữ cảnh xuyên suốt phiên chat.*

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [ ] Cả 4 checkpoint pytest đều pass
- [ ] Tất cả 9 câu trong file này đã được trả lời
- [ ] Đã copy bài làm vào folder `solution/`, push lên fork và dán link trên trang bài Lab ở VLearn trước 23:59 ngày 11/09/2026