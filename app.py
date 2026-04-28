import streamlit as st
import pandas as pd

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

# 2. 初始化 Session State (記錄分數與當前題目)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'wrong' not in st.session_state:
    st.session_state.wrong = 0
if 'current_options' not in st.session_state:
    # 隨機挑選兩個不同的項目
    st.session_state.current_options = df.sample(2).to_dict('records')
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'result_msg' not in st.session_state:
    st.session_state.result_msg = ""

# 標題與說明
st.title("🌍 碳足跡大對決：誰比較環保？")
st.markdown("請選擇以下兩項物品中，**人均碳排放量較低（較環保）**的選項！")

# 顯示計分板
col_score1, col_score2 = st.columns(2)
col_score1.metric("✅ 答對題數", st.session_state.score)
col_score2.metric("❌ 答錯題數", st.session_state.wrong)

st.divider()

# 取得當前題目
item1 = st.session_state.current_options[0]
item2 = st.session_state.current_options[1]

# 判斷正確答案
correct_item = item1 if item1['CO2e'] < item2['CO2e'] else item2

# 3. 處理答題邏輯
def check_answer(selected_item):
    st.session_state.answered = True
    if selected_item['Item'] == correct_item['Item']:
        st.session_state.score += 1
        st.session_state.result_msg = "🎉 答對了！你真內行！"
    else:
        st.session_state.wrong += 1
        st.session_state.result_msg = "💨 答錯囉！再接再厲！"

def next_question():
    st.session_state.current_options = df.sample(2).to_dict('records')
    st.session_state.answered = False

# 4. 建立互動介面
col1, col2 = st.columns(2)

with col1:
    # 先顯示這是第幾週的分類
    st.caption(f"🏷️ 類別：{item1['Week']}")
    st.subheader(item1['Item'])
    if not st.session_state.answered:
        st.button("選擇這個", key="btn1", on_click=check_answer, args=(item1,), use_container_width=True)

with col2:
    # 先顯示這是第幾週的分類
    st.caption(f"🏷️ 類別：{item2['Week']}")
    st.subheader(item2['Item'])
    if not st.session_state.answered:
        st.button("選擇這個", key="btn2", on_click=check_answer, args=(item2,), use_container_width=True)

# 5. 顯示結果與解析
if st.session_state.answered:
    # 使用標準的 if/else 避免 Streamlit Magic 印出多餘的程式碼
    if "答對了" in st.session_state.result_msg:
        st.success(st.session_state.result_msg)
    else:
        st.error(st.session_state.result_msg)
    
    st.markdown("### 📊 數據解析")
    
    # 整理要顯示的表格資料
    result_df = pd.DataFrame([item1, item2])[['Item', 'Week', 'CO2e', 'Reason']]
    result_df.columns = ['物品名稱', '分類週數', '碳排放量 (CO2e)', '原因說明']
    
    # 使用 st.dataframe 或 st.table 顯示乾淨的表格
    st.table(result_df)
    
    st.button("下一題 ➡️", on_click=next_question, type="primary")
