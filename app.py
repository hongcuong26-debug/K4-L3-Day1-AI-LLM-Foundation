import os
import random
import sys
import time
import streamlit as st

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Otaku Station - Waifu AI",
    page_icon="🌸",
    layout="wide",
)

# Nạp các hàm từ template.py
_LAB_AVAILABLE = False
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from template import (
        OPENAI_MODEL,
        call_openai,
        count_tokens,
        estimate_cost,
        retry_with_backoff,
    )
    _LAB_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    OPENAI_MODEL = "gpt-4o (demo)"
    _LAB_AVAILABLE = False

KAOMOJI = ["(≧◡≦)", "(◕‿◕✿)", "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧", "(๑˃̵ᴗ˂̵)و", "(*≧▽≦)"]
DEMO_REPLIES = [
    "Sugoi! Đang ở chế độ Demo nè senpai~ Thêm API key để trò chuyện thật nha!",
    "Ara ara~ Hệ thống chưa nhận API key thật, em trả lời thử nghiệm thôi nhé!",
    "Beep boop~ Neural core đang mô phỏng phản hồi nè (◕‿◕✿)!",
]

# CSS giao diện Neon Anime / Cyberpunk Wibu
st.markdown("""
<style>
    .stApp {
        background-color: #0e0517;
        color: #f0f0f0;
    }
    .main-title {
        text-align: center;
        color: #ff4fd8;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 10px #ff4fd8, 0 0 20px #b967ff;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #4dfff3;
        font-size: 14px;
        margin-bottom: 25px;
    }
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid #b967ff;
        background-color: #1a0b2e;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if "turns" not in st.session_state:
    st.session_state.turns = 0
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0
if "hp" not in st.session_state:
    st.session_state.hp = 100
if "mp" not in st.session_state:
    st.session_state.mp = 80
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tiêu đề
st.markdown("<h1 class='main-title'>✧ OTAKU STATION ✧</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>Cyberpunk Anime Terminal OS {random.choice(KAOMOJI)}</div>", unsafe_allow_html=True)

# Sidebar hiển thị trạng thái RPG
with st.sidebar:
    st.header("⚔ STATUS ⚔")
    st.write(f"**Companion:** Mika {random.choice(KAOMOJI)}")
    st.write(f"**Mode:** {'LIVE 🟢' if _LAB_AVAILABLE else 'DEMO 🟡'}")
    st.write(f"**Model:** `{OPENAI_MODEL}`")
    
    st.write("---")
    st.write(f"**HP:** {st.session_state.hp}/100")
    st.progress(st.session_state.hp / 100)
    
    st.write(f"**MP:** {st.session_state.mp}/100")
    st.progress(st.session_state.mp / 100)
    
    st.write("---")
    st.metric("Total Turns", st.session_state.turns)
    st.metric("Tokens Used", st.session_state.total_tokens)
    st.metric("Session Cost", f"${st.session_state.total_cost:.5f}")

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🌸" if msg["role"] == "assistant" else "🎮"):
        st.markdown(msg["content"])

# Nhận tin nhắn từ người dùng
if prompt := st.chat_input("Master@OtakuStation ❯ Hãy nhập câu hỏi..."):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎮"):
        st.markdown(prompt)

    # Xử lý phản hồi
    with st.chat_message("assistant", avatar="🌸"):
        reply_placeholder = st.empty()
        full_reply = ""
        
        start_time = time.perf_counter()
        if _LAB_AVAILABLE:
            try:
                full_reply, _ = retry_with_backoff(lambda: call_openai(prompt))
            except Exception as e:
                full_reply = f"Lỗi: {e}. " + random.choice(DEMO_REPLIES)
            tokens_in = count_tokens(prompt)
            tokens_out = count_tokens(full_reply)
            cost = estimate_cost(prompt, full_reply)["total_cost"]
            total_tok = tokens_in + tokens_out
        else:
            time.sleep(0.4)
            full_reply = random.choice(DEMO_REPLIES)
            cost = 0.0
            total_tok = len(prompt.split()) + len(full_reply.split())

        # Hiệu ứng gõ chữ
        for ch in full_reply:
            reply_placeholder.markdown(full_reply[:len(reply_placeholder.text or "") + 1] + "▌")
            time.sleep(0.01)
        reply_placeholder.markdown(full_reply)

    # Cập nhật số liệu RPG
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.session_state.turns += 1
    st.session_state.total_tokens += total_tok
    st.session_state.total_cost += cost
    st.session_state.mp = max(5, st.session_state.mp - random.randint(3, 8))
    st.rerun()