"""
K4 — Ngày 1: Khám Phá LLM API (4 tiếng)
AICB-P1: AI Practical Competency Program, Phase 1

Hướng dẫn:
    1. Làm theo LAB_GUIDE.md — mỗi block có các bước chi tiết và checkpoint.
    2. Điền vào tất cả các chỗ đánh dấu TODO.
    3. KHÔNG đổi chữ ký hàm (tên hàm, tham số).
    4. Import OpenAI BÊN TRONG hàm (xem gợi ý) — nếu import ở đầu file,
       các bài test mock sẽ không hoạt động.
    5. Kiểm tra tiến độ:  pytest tests/test_part1.py -v  (từng phần)
       Chấm điểm tổng:    python grade.py
"""

import os
import time
from openai import OpenAI
from typing import Any, Callable

from dotenv import load_dotenv
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
)
OPENAI_MODEL = os.getenv("LAB_MODEL", "anthropic/claude-3.5-sonnet")
OPENAI_MINI_MODEL = os.getenv("LAB_MINI_MODEL", "anthropic/claude-3-haiku")
# Nạp OPENAI_API_KEY từ file .env (copy .env.example thành .env và dán key vào)
load_dotenv()

# ---------------------------------------------------------------------------
# Bảng giá ước tính (USD / 1K token) — cập nhật nếu giá thay đổi
# ---------------------------------------------------------------------------
PRICING_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}

# Tên model có thể đổi qua .env — ví dụ khi dùng NVIDIA NIM miễn phí
# (xem LAB_GUIDE.md, Phụ lục B). Không đặt gì trong .env thì mặc định OpenAI.
OPENAI_MODEL = os.getenv("LAB_MODEL", "gpt-4o")
OPENAI_MINI_MODEL = os.getenv("LAB_MINI_MODEL", "gpt-4o-mini")


# ===========================================================================
# PART 1 — API CƠ BẢN (Block 1: phút 60–100)
# ===========================================================================

# ---------------------------------------------------------------------------
# Task 1.1 — Gọi GPT-4o
# ---------------------------------------------------------------------------
def call_openai(
    prompt: str,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    latency = time.perf_counter() - start
    return response.choices[0].message.content, latency

def call_openai_mini(
    prompt: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 256,
) -> tuple[str, float]:
    return call_openai(
        prompt,
        model=OPENAI_MINI_MODEL,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )

# ---------------------------------------------------------------------------
# Task 1.3 — So sánh GPT-4o vs GPT-4o-mini
# ---------------------------------------------------------------------------
def compare_models(prompt: str) -> dict:
    gpt4o_text, gpt4o_latency = call_openai(prompt)
    mini_text, mini_latency = call_openai_mini(prompt)
    cost = (len(gpt4o_text.split()) / 0.75) / 1000 \
           * PRICING_PER_1K_TOKENS["gpt-4o"]["output"]
    return {
        "gpt4o_response": gpt4o_text,
        "mini_response": mini_text,
        "gpt4o_latency": gpt4o_latency,
        "mini_latency": mini_latency,
        "gpt4o_cost_estimate": cost,
    }

# ===========================================================================
# PART 2 — SYSTEM PROMPT & TOKEN (Block 2: phút 100–140)
# ===========================================================================

# ---------------------------------------------------------------------------
# Task 2.1 — Chat với system prompt (persona)
# ---------------------------------------------------------------------------
def chat_with_system_prompt(
    system_prompt: str,
    user_prompt: str,
    model: str = OPENAI_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> tuple[str, float]:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = time.perf_counter() - start
    return response.choices[0].message.content, latency


# ---------------------------------------------------------------------------
# Task 2.2 — Đếm token bằng tiktoken
# ---------------------------------------------------------------------------
def count_tokens(text: str, model: str = OPENAI_MODEL) -> int:
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        # Fallback ước lượng khi offline hoặc gặp model lạ
        return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Task 2.3 — Ước tính chi phí chính xác
# ---------------------------------------------------------------------------
def estimate_cost(prompt: str, response: str, model: str = OPENAI_MODEL) -> dict:
    input_tokens = count_tokens(prompt, model)
    output_tokens = count_tokens(response, model)

    # Dùng .get(...) với gpt-4o làm dự phòng để tránh KeyError khi dùng model khác
    pricing = PRICING_PER_1K_TOKENS.get(model, PRICING_PER_1K_TOKENS["gpt-4o"])
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }


# ===========================================================================
# PART 3 — STREAMING & ĐỘ BỀN (Block 3: phút 150–190)
# ===========================================================================

# ===========================================================================
# PART 3 — STREAMING & ĐỘ BỀN (Block 3: phút 150–190)
# ===========================================================================

# ---------------------------------------------------------------------------
# Task 3.1 — Chatbot streaming có lịch sử hội thoại
# ---------------------------------------------------------------------------
def streaming_chatbot() -> None:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    history = []

    while True:
        user_msg = input("Bạn: ")
        # Thoát nếu gõ quit hoặc exit (không phân biệt hoa thường)
        if user_msg.strip().lower() in ("quit", "exit"):
            break

        # Ghép messages = history + tin nhắn user hiện tại
        messages = history + [{"role": "user", "content": user_msg}]

        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            stream=True,
        )

        reply = ""
        # In từng chunk khi nhận được
        for chunk in stream:
            # Chunk cuối có delta.content là None -> bắt buộc dùng 'or ""'
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            reply += delta
        print()

        # Lưu vào history và giữ lại tối đa 3 lượt (6 tin nhắn)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reply})
        history = history[-6:]


# ---------------------------------------------------------------------------
# Task 3.2 — Retry với exponential backoff
# ---------------------------------------------------------------------------
def retry_with_backoff(
    fn: Callable,
    max_retries: int = 3,
    base_delay: float = 0.1,
) -> Any:
    # Vòng lặp max_retries + 1 lần (lần đầu + các lần retry)
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            # Nếu đã thử hết số lượt cho phép thì ném exception gốc ra ngoài
            if attempt == max_retries:
                raise
            # Chờ với độ trễ tăng gấp đôi: base_delay * (2 ^ attempt)
            time.sleep(base_delay * (2 ** attempt))


# ===========================================================================
# PART 4 — MINI-PROJECT: TRỢ LÝ CLI HOÀN CHỈNH (Block 4: phút 190–230)
# ===========================================================================
def run_assistant(
    persona: str,
    get_input: Callable[[], str] = None,
    max_turns: int = None,
) -> dict:
    from openai import OpenAI

    if get_input is None:
        get_input = input

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    history = []
    num_turns = 0
    total_tokens = 0
    total_cost = 0.0

    while True:
        # Bắt buộc kiểm tra max_turns trước khi gọi get_input
        if max_turns is not None and num_turns >= max_turns:
            break

        user_msg = get_input()
        if user_msg.strip().lower() in ("quit", "exit"):
            break

        messages = (
            [{"role": "system", "content": persona}]
            + history
            + [{"role": "user", "content": user_msg}]
        )

        stream = retry_with_backoff(
            lambda: client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                stream=True,
            )
        )

        reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            reply += delta
        print()

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": reply})
        history = history[-6:]

        num_turns += 1
        total_tokens += count_tokens(user_msg) + count_tokens(reply)
        total_cost += estimate_cost(user_msg, reply)["total_cost"]

    return {
        "num_turns": num_turns,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "history": history,
    }
# ===========================================================================
# BONUS (không bắt buộc — cho bạn nào xong sớm)
# ===========================================================================
def batch_compare(prompts: list[str]) -> list[dict]:
    """
    Chạy compare_models cho từng prompt trong list.
    """
    results = []
    for prompt in prompts:
        # Gọi lại compare_models đã viết ở Part 1
        res = compare_models(prompt)
        # Thêm key "prompt" chứa prompt gốc
        res["prompt"] = prompt
        results.append(res)
    return results


def format_comparison_table(results: list[dict]) -> str:
    """
    Định dạng kết quả batch_compare thành bảng text dễ đọc.

    Cột: Prompt | GPT-4o Response | Mini Response | GPT-4o Latency | Mini Latency
    """
    # Tiêu đề bảng
    header = f"{'Prompt':<40} | {'GPT-4o Response':<40} | {'Mini Response':<40} | {'GPT-4o Latency':<15} | {'Mini Latency':<15}"
    separator = "-" * len(header)
    lines = [header, separator]

    for item in results:
        # Cắt chuỗi text dài còn tối đa 40 ký tự và thay ký tự xuống dòng
        prompt_txt = (item.get("prompt", "")[:37] + "...") if len(item.get("prompt", "")) > 40 else item.get("prompt", "")
        gpt4o_res = item.get("gpt4o_response", "").replace("\n", " ")
        gpt4o_txt = (gpt4o_res[:37] + "...") if len(gpt4o_res) > 40 else gpt4o_res
        mini_res = item.get("mini_response", "").replace("\n", " ")
        mini_txt = (mini_res[:37] + "...") if len(mini_res) > 40 else mini_res
        
        gpt4o_lat = f"{item.get('gpt4o_latency', 0.0):.2f}s"
        mini_lat = f"{item.get('mini_latency', 0.0):.2f}s"

        row = f"{prompt_txt:<40} | {gpt4o_txt:<40} | {mini_txt:<40} | {gpt4o_lat:<15} | {mini_lat:<15}"
        lines.append(row)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point — demo chạy thật (cần OPENAI_API_KEY)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== So sánh model ===")
    result = compare_models(
        "Giải thích khác biệt giữa temperature và top_p trong một câu."
    )
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n=== Trợ lý CLI (gõ 'quit' để thoát) ===")
    stats = run_assistant(
        persona="Bạn là trợ giảng thân thiện của khóa AI, "
                "trả lời ngắn gọn bằng tiếng Việt.",
    )
    print("\n--- Thống kê phiên chat ---")
    for key, value in stats.items():
        if key != "history":
            print(f"{key}: {value}")
