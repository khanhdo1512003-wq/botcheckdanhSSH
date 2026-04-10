import streamlit as st
import pandas as pd
from collections import defaultdict
import math

# ================== CONFIG ==================
st.set_page_config(page_title="Fantan Pattern Bot", layout="centered")

st.title("🧠 Fantan Pattern Prediction Bot")

# ================== LOAD DATA ==================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df

df = load_data()

# lấy cột A (cột đầu tiên)
data = df.iloc[:, 0].dropna().astype(int).tolist()

st.write(f"📊 Tổng data: {len(data)} ván")

# ================== SETTINGS ==================
min_k = st.slider("Min k", 3, 10, 5)
max_k = st.slider("Max k", min_k, 20, 12)

# ================== CORE FUNCTION ==================
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

        # bỏ nhiễu
        if total_match < 3:
            continue

        k_results[k] = {
            "match": total_match,
            "counts": dict(counts)
        }

        # trọng số
        weight = (k ** 1.3) * math.log(total_match + 1)

        for num in range(1, 5):
            c = counts.get(num, 0)
            final_score[num] += c * weight
            final_count[num] += c

    total_score = sum(final_score.values())

    final_prob = {}
    for num in range(1, 5):
        if total_score > 0:
            final_prob[num] = round(final_score[num] / total_score * 100, 2)
        else:
            final_prob[num] = 0

    return k_results, final_count, final_prob


# ================== RUN ==================
if st.button("🚀 RUN PREDICTION"):

    k_results, final_count, final_prob = fantan_predict(data, min_k, max_k)

    st.subheader("📌 KẾT QUẢ THEO TỪNG K")

    for k in sorted(k_results.keys()):
        res = k_results[k]
        st.write(f"👉 k = {k} | match = {res['match']}")

        counts = res["counts"]
        st.write(
            f"1: {counts.get(1,0)} | "
            f"2: {counts.get(2,0)} | "
            f"3: {counts.get(3,0)} | "
            f"4: {counts.get(4,0)}"
        )

    st.subheader("🔥 FINAL OUTPUT")

    total_all = sum(final_count.values())

    for num in range(1, 5):
        count = int(final_count[num])
        prob = final_prob[num]
        st.write(f"{num} → {count} lần | {prob}%")

    # ================== CONFIDENCE ==================
    st.subheader("🧠 CONFIDENCE")

    if total_all < 10:
        st.warning("⚠️ Dữ liệu yếu (Low Confidence)")
    elif max(final_prob.values()) < 35:
        st.info("🟡 Kèo nhiễu (No clear edge)")
    else:
        st.success("🟢 Có bias rõ → có thể đánh")
