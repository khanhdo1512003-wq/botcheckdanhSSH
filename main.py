import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fantan Streak Analyzer", layout="centered")

st.title("🧠 Fantan Streak Analysis Bot")

# -------- INPUT DATA --------
data_input = st.text_area("Nhập data (cách nhau bằng dấu phẩy)", height=150)

col1, col2 = st.columns(2)
with col1:
    start_idx = st.number_input("Start index", min_value=0, value=0)
with col2:
    end_idx = st.number_input("End index", min_value=1, value=100)

run = st.button("🚀 Analyze")

# -------- PROCESS --------
if run:
    try:
        data = [int(x.strip()) for x in data_input.split(",") if x.strip() != ""]
        
        # Cắt range
        data = data[start_idx:end_idx]

        if len(data) < 3:
            st.warning("Data quá ngắn!")
        else:
            streak_counts = {}
            streak_results = {}

            i = 0
            total_profit = 0
            total_bets = 0
            wins = 0
            losses = 0

            while i < len(data) - 2:
                current = data[i]
                count = 1

                # đếm streak
                while i + count < len(data) and data[i + count] == current:
                    count += 1

                # nếu streak >=2 và còn dữ liệu sau đó
                if count >= 2 and i + count < len(data) - 1:
                    end_value = data[i + count]       # số kết thúc streak
                    next_value = data[i + count + 1]  # ván sau

                    # thống kê streak
                    streak_counts[count] = streak_counts.get(count, 0) + 1

                    # check win/loss
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

                    # lưu theo streak
                    if count not in streak_results:
                        streak_results[count] = {"win": 0, "lose": 0}

                    streak_results[count][result] += 1

                i += count

            # -------- OUTPUT --------
            st.subheader("📊 Tổng quan")
            st.write(f"Tổng lệnh: {total_bets}")
            st.write(f"Win: {wins} | Lose: {losses}")
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

    except Exception as e:
        st.error(f"Lỗi: {e}")
