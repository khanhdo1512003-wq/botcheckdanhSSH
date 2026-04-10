import streamlit as st
import pandas as pd
from collections import defaultdict
import math

st.set_page_config(page_title="Fantan Bot", layout="centered")

st.title("🔥 V43 FINAL BOT")

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"

# ================= LOAD =================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    data = df.iloc[:, 0].dropna().astype(int).tolist()
    return "".join(map(str, data))

if "raw_data" not in st.session_state:
    st.session_state.raw_data = ""

if st.button("☁️ Load từ Google Sheets"):
    st.session_state.raw_data = load_data()

# ================= INPUT =================
st.subheader("Nhập dữ liệu")

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
if st.button("📊 Phân tích"):

    data = parse_data(raw_input)
    st.write(f"📊 Tổng data: {len(data)}")

    # ===== HIỆN 15 SỐ GẦN NHẤT =====
    st.subheader("📍 Chuỗi hiện tại (15 số gần nhất)")
    last_15 = data[-15:]
    st.code(" ".join(map(str, last_15)))

    k_results, final_count, final_prob = fantan_predict(data)

    # ===== K RESULT =====
    st.subheader("📌 Theo từng k")

    for k in sorted(k_results.keys()):
        res = k_results[k]
        c = res["counts"]

        st.write(f"k={k} | match={res['match']}")
        st.write(f"1:{c.get(1,0)}  2:{c.get(2,0)}  3:{c.get(3,0)}  4:{c.get(4,0)}")

    # ===== FINAL =====
    st.subheader("🔥 FINAL")

    for num in range(1, 5):
        st.write(f"{num} → {int(final_count[num])} lần | {final_prob[num]}%")

    # ===== TOP 2 =====
    st.subheader("🎯 TOP 2 NÊN ĐÁNH")

    sorted_nums = sorted(final_prob.items(), key=lambda x: x[1], reverse=True)

    top2 = sorted_nums[:2]

    for num, prob in top2:
        st.success(f"{num} → {prob}%")

    # ===== CONFIDENCE =====
    st.subheader("🧠 Đánh giá")

    total_all = sum(final_count.values())

    if total_all < 10:
        st.warning("⚠️ Data yếu")
    elif max(final_prob.values()) < 35:
        st.info("🟡 Không có lợi thế rõ")
    else:
        st.success("🟢 Có bias")
