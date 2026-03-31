import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fantan Streak Analyzer", layout="centered")

st.title("🧠 Fantan Streak Analysis Bot (Live Data)")

# -------- GOOGLE SHEET CSV --------
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5-pPONvbU7PR7FteVtEBvN6EuudQ2rgbV3sHX-Ngy1PALF4nvyTBidXOXXE325_TLKKDJwZB7xFgH/pub?output=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)
    
    # lấy cột đầu tiên (giả sử là kết quả 1-4)
    col = df.columns[0]
    data = df[col].dropna().astype(int).tolist()
    
    return data

# -------- LOAD DATA --------
if st.button("🔄 Load / Refresh Data"):
    st.cache_data.clear()

data = load_data()

st.success(f"Đã load {len(data)} ván")

# -------- RANGE SELECT --------
col1, col2 = st.columns(2)
with col1:
    start_idx = st.number_input("Start index", min_value=0, max_value=len(data)-1, value=0)
with col2:
    end_idx = st.number_input("End index", min_value=1, max_value=len(data), value=len(data))

run = st.button("🚀 Analyze")

# -------- PROCESS --------
if run:
    subset = data[start_idx:end_idx]

    streak_counts = {}
    streak_results = {}

    i = 0
    total_profit = 0
    total_bets = 0
    wins = 0
    losses = 0

    while i < len(subset) - 2:
        current = subset[i]
        count = 1

        # đếm streak
        while i + count < len(subset) and subset[i + count] == current:
            count += 1

        # nếu streak >=2
        if count >= 2 and i + count < len(subset) - 1:
            end_value = subset[i + count]
            next_value = subset[i + count + 1]

            streak_counts[count] = streak_counts.get(count, 0) + 1

            if next_value != end_value:
                result = "win"
                profit = 0.31
                wins += 1
            else:
                result = "lose"
                profit = -1
                losses += 1

            total_profit += profit
            total_bets += 1

            if count not in streak_results:
                streak_results[count] = {"win": 0, "lose": 0}

            streak_results[count][result] += 1

        i += count

    # -------- OUTPUT --------
    st.subheader("📊 Tổng quan")
    st.write(f"Tổng lệnh: {total_bets}")
    st.write(f"Win: {wins} | Lose: {losses}")
    if total_bets > 0:
        st.write(f"Winrate: {wins / total_bets * 100:.2f}%")
    st.write(f"Profit: {total_profit:.2f}")

    st.subheader("📈 Phân tích theo streak")

    table = []
    for streak in sorted(streak_counts.keys()):
        total = streak_results[streak]["win"] + streak_results[streak]["lose"]
        winrate = streak_results[streak]["win"] / total * 100

        table.append({
            "Streak": streak,
            "Số lần xuất hiện": streak_counts[streak],
            "Win": streak_results[streak]["win"],
            "Lose": streak_results[streak]["lose"],
            "Winrate (%)": round(winrate, 2)
        })

    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)
