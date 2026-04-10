import streamlit as st
import pandas as pd
from collections import defaultdict
import math

st.set_page_config(page_title="Fantan Bot Pro", layout="wide")

st.title("🧠 Fantan Pattern Bot PRO")

# ================== LOAD DATA ==================
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    return df.iloc[:, 0].dropna().astype(int).tolist()

# session lưu data
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ================== LAYOUT ==================
col1, col2 = st.columns([2,1])

# ================== DATA TABLE ==================
with col1:
    st.subheader("📊 DATA HIỆN TẠI")

    df_display = pd.DataFrame({"Result": data[::-1]})
    st.dataframe(df_display, height=400)

    st.write(f"🔢 Tổng: {len(data)} ván")

# ================== INPUT ==================
with col2:
    st.subheader("➕ THÊM DATA")

    new_input = st.text_input("Nhập số (1-4), cách nhau bằng dấu cách", "")

    if st.button("ADD DATA"):
        try:
            nums = [int(x) for x in new_input.split()]
            nums = [x for x in nums if x in [1,2,3,4]]

            st.session_state.data.extend(nums)
            st.success(f"Đã thêm {len(nums)} số")

        except:
            st.error("Input lỗi")

    if st.button("🔄 RESET DATA"):
        st.session_state.data = load_data()
        st.success("Đã reset về dữ liệu gốc")

# ================== SETTINGS ==================
st.subheader("⚙️ SETTINGS")

col3, col4 = st.columns(2)
with col3:
    min_k = st.slider("Min k", 3, 10, 5)
with col4:
    max_k = st.slider("Max k", min_k, 20, 12)

# ================== CORE ==================
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
        if total_score > 0:
            final_prob[num] = round(final_score[num] / total_score * 100, 2)
        else:
            final_prob[num] = 0

    return k_results, final_count, final_prob

# ================== RUN ==================
st.subheader("🚀 PREDICTION")

if st.button("RUN BOT"):

    k_results, final_count, final_prob = fantan_predict(data, min_k, max_k)

    colA, colB = st.columns(2)

    # ===== K RESULTS =====
    with colA:
        st.subheader("📌 THEO TỪNG K")

        for k in sorted(k_results.keys()):
            res = k_results[k]
            counts = res["counts"]

            st.write(f"👉 k={k} | match={res['match']}")
            st.write(
                f"1:{counts.get(1,0)} | "
                f"2:{counts.get(2,0)} | "
                f"3:{counts.get(3,0)} | "
                f"4:{counts.get(4,0)}"
            )

    # ===== FINAL =====
    with colB:
        st.subheader("🔥 FINAL")

        total_all = sum(final_count.values())

        for num in range(1,5):
            st.write(f"{num} → {int(final_count[num])} lần | {final_prob[num]}%")

        # ===== CONFIDENCE =====
        st.subheader("🧠 CONFIDENCE")

        if total_all < 10:
            st.warning("⚠️ Yếu")
        elif max(final_prob.values()) < 35:
            st.info("🟡 Nhiễu")
        else:
            st.success("🟢 Có bias")
