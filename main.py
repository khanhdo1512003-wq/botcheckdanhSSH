import streamlit as st
import pandas as pd
from collections import defaultdict
import math

st.set_page_config(page_title="Fantan Bot Pro", layout="centered")

st.title("🔥 FANTAN AI BOT FINAL (STABLE + LIVE DATA)")

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"

# ================= LOAD DATA (FIX CACHE) =================
@st.cache_data(ttl=5)
def load_data():
    df = pd.read_csv(DATA_URL)
    data = df.iloc[:, 0].dropna().astype(int).tolist()
    return "".join(map(str, data))

# ================= SESSION =================
if "raw_data" not in st.session_state:
    st.session_state.raw_data = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "correct" not in st.session_state:
    st.session_state.correct = 0

if "total" not in st.session_state:
    st.session_state.total = 0

if "last_data" not in st.session_state:
    st.session_state.last_data = None

# ================= BUTTON =================
col1, col2 = st.columns(2)

with col1:
    if st.button("☁️ Load Google Sheet"):
        st.session_state.raw_data = load_data()

with col2:
    if st.button("♻️ Refresh Data"):
        st.cache_data.clear()
        st.success("Đã refresh cache")

# ================= INPUT =================
st.subheader("📥 DATA INPUT")

raw_input = st.text_area("", value=st.session_state.raw_data, height=200)

def parse_data(text):
    return [int(c) for c in text if c in "1234"]

# ================= CORE =================
def fantan_predict(data, min_k=5, max_k=12):
    n = len(data)
    
    k_results = {}
    final_score = defaultdict(float)
    final_count = defaultdict(float)

    for k in range(min_k, max_k + 1):
        if k >= n:
            break

        pattern = tuple(data[-k:])
        counts = defaultdict(int)
        total_match = 0

        for i in range(n - k):
            if tuple(data[i:i+k]) == pattern:
                next_val = data[i+k]
                counts[next_val] += 1
                total_match += 1

        if total_match < 3:
            continue

        k_results[k] = {
            "match": total_match,
            "counts": dict(counts)
        }

        weight = (k ** 1.3) * math.log(total_match + 1)

        for num in range(1, 5):
            c = counts.get(num, 0)
            final_score[num] += c * weight
            final_count[num] += c

    total_score = sum(final_score.values())

    final_prob = {}
    for num in range(1, 5):
        final_prob[num] = round((final_score[num] / total_score * 100), 2) if total_score > 0 else 0

    return k_results, final_count, final_prob

# ================= RUN =================
if st.button("🚀 RUN BOT"):

    data = parse_data(raw_input)
    st.write(f"📊 Tổng data: {len(data)}")

    # ===== INIT SNAPSHOT =====
    if st.session_state.last_data is None:
        st.session_state.last_data = data.copy()

    prev_data = st.session_state.last_data.copy()

    # ===== WINRATE ENGINE =====
    if prev_data != data:

        diff = len(data) - len(prev_data)

        # ➕ thêm 1 số
        if diff == 1 and len(st.session_state.history) > 0:
            last_real = data[-1]
            last_predict = st.session_state.history[-1]

            if last_real in last_predict:
                st.session_state.correct += 1

            st.session_state.total += 1

        # ➖ xoá 1 số
        elif diff == -1 and st.session_state.total > 0:
            last_predict = st.session_state.history[-1]
            last_real = prev_data[-1]

            if last_real in last_predict:
                st.session_state.correct -= 1

            st.session_state.total -= 1
            st.session_state.history.pop()

        # ✏️ sửa số cuối
        elif diff == 0 and len(data) > 0:
            if data[-1] != prev_data[-1] and st.session_state.total > 0:

                # rollback
                last_predict = st.session_state.history[-1]
                last_real = prev_data[-1]

                if last_real in last_predict:
                    st.session_state.correct -= 1

                st.session_state.total -= 1
                st.session_state.history.pop()

                # tính lại
                if len(st.session_state.history) > 0:
                    last_predict = st.session_state.history[-1]
                    new_real = data[-1]

                    if new_real in last_predict:
                        st.session_state.correct += 1

                    st.session_state.total += 1

    # ===== HIỂN THỊ 15 SỐ =====
    st.subheader("📍 15 SỐ GẦN NHẤT")
    st.code(" ".join(map(str, data[-15:])))

    # ===== PREDICT =====
    k_results, final_count, final_prob = fantan_predict(data)

    # ===== FINAL =====
    st.subheader("🔥 FINAL")

    for num in range(1, 5):
        st.write(f"{num} → {int(final_count[num])} lần | {final_prob[num]}%")

    # ===== TOP 2 =====
    st.subheader("🎯 TOP 2")

    sorted_nums = sorted(final_prob.items(), key=lambda x: x[1], reverse=True)
    top2 = sorted_nums[:2]

    for num, prob in top2:
        st.success(f"{num} → {prob}%")

    st.session_state.history.append([num for num, _ in top2])

    # ===== WINRATE =====
    st.subheader("📈 WINRATE")

    if st.session_state.total > 0:
        winrate = round(st.session_state.correct / st.session_state.total * 100, 2)

        st.write(f"✅ Đúng: {st.session_state.correct}")
        st.write(f"❌ Sai: {st.session_state.total - st.session_state.correct}")
        st.write(f"🎯 Tỷ lệ thắng: {winrate}%")
    else:
        st.write("Chưa có dữ liệu")

    # ===== CONFIDENCE =====
    st.subheader("🧠 ĐÁNH GIÁ")

    total_all = sum(final_count.values())

    if total_all < 10:
        st.warning("⚠️ Data yếu")
    elif max(final_prob.values()) < 35:
        st.info("🟡 Nhiễu")
    else:
        st.success("🟢 Có bias")

    # ===== UPDATE SNAPSHOT (CUỐI CÙNG) =====
    st.session_state.last_data = data.copy()
