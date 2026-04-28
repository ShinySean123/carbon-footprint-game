import streamlit as st
import pandas as pd
import random
import time

# 1. 讀取與清理資料
@st.cache_data
def load_data():
    cols = ['Week', 'Level', 'Quantity', 'Item', 'CO2e_str', 'CO2e', 'Reason']
    df = pd.read_csv('carbon_data.csv', names=cols, skiprows=1)
    
    # 清理資料：確保碳排量是數字，並排除空缺值
    df['CO2e'] = pd.to_numeric(df['CO2e'], errors='coerce')
    df = df.dropna(subset=['CO2e', 'Item'])
    df['Reason'] = df['Reason'].fillna('無特別說明')
    return df

df = load_data()

# 定義抽題邏輯函式
def get_options(data, mode):
    if mode == "同週次對決":
        week_counts = data['Week'].value_counts()
        valid_weeks = week_counts[week_counts >= 2].index.tolist()
        if valid_weeks:
            chosen_week = random.choice(valid_weeks)
            return data[data['Week'] == chosen_week].sample(2).to_dict('records')
    return data.sample(2).to_dict('records')

# 切換模式或下一題的重置動作
def reset_question():
    st.session_state.answered = False
    st.session_state.current_options = get_options(df, st.session_state.mode)
    st.session_state.start_time = time.time()

# 2. 初始化 Session State
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'wrong' not in st.session_state:
    st.session_state.wrong = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "不限週次"
if 'current_options' not in st.session_state:
    st.session_state.current_options = get_options(df, "不限週次")
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'time_taken' not in st.session_state:
    st.session_state.time_taken = 0.0

# --- 側邊欄或頂部設定 ---
st.title("🌍 碳足跡大對決：誰比較環保？")

# 顯示計分板
col_score1, col_score2, col_mode = st.columns([1, 1, 2])
col_score1.metric("✅ 答對", st.session_state.score)
col_score2.metric("❌ 答錯", st.session_state.wrong)
with col_mode:
    st.radio("🎯 出題模式：", ["不限週次", "同週次對決"], horizontal=True, key="mode", on_change=reset_question)

st.divider()

# --- 📜 減碳小抄功能 ---
with st.expander("📜 查看減碳小抄 (按我打開/關閉)"):
    st.markdown("這裡有所有項目的排名，**碳排放由低到高**：")
    # 這裡將資料由小到大排序
    cheat_sheet_df = df.sort_values('CO2e').reset_index(drop=True)
    # 只顯示重點欄位
    st.dataframe(
        cheat_sheet_df[['CO2e', 'Item', 'Week', 'Reason']].rename(
            columns={'CO2e': '碳排放量', 'Item': '物品名稱', 'Week': '分類', 'Reason': '原因'}
        ),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# --- 遊戲主體 ---
item1 = st.session_state.current_options[0]
item2 = st.session_state.current_options[1]
correct_item = item1 if item1['CO2e'] < item2['CO2e'] else item2

def check_answer(selected_item):
    st.session_state.time_taken = time.time() - st.session_state.start_time
    st.session_state.answered = True
    if selected_item['Item'] == correct_item['Item']:
        st.session_state.score += 1
        st.session_state.result_style = "success"
        st.session_state.result_msg = f"🎉 答對了！耗時 {st.session_state.time_taken:.2f} 秒"
    else:
        st.session_state.wrong += 1
        st.session_state.result_style = "error"
        st.session_state.result_msg = f"💨 答錯囉！這題花了你 {st.session_state.time_taken:.2f} 秒"

# 顯示選項按鈕
col1, col2 = st.columns(2)
with col1:
    st.caption(f"🏷️ {item1['Week']}")
    st.subheader(item1['Item'])
    if not st.session_state.answered:
        st.button("這項排放較低", key="btn1", on_click=check_answer, args=(item1,), use_container_width=True)

with col2:
    st.caption(f"🏷️ {item2['Week']}")
    st.subheader(item2['Item'])
    if not st.session_state.answered:
        st.button("這項排放較低", key="btn2", on_click=check_answer, args=(item2,), use_container_width=True)

# 顯示結果與數據解析
if st.session_state.answered:
    if st.session_state.result_style == "success":
        st.success(st.session_state.result_msg)
    else:
        st.error(st.session_state.result_msg)
    
    st.markdown("### 📊 數據詳情")
    result_display = pd.DataFrame([item1, item2])[['Item', 'CO2e', 'Reason']]
    result_display.columns = ['物品名稱', '碳排放量 (CO2e)', '原因說明']
    st.table(result_display)
    
    st.button("下一題 ➡️", on_click=reset_question, type="primary")
