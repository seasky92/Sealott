import streamlit as st
import pandas as pd
import random
from collections import Counter
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1tW8KwjFh9PZEoLxNyoiboi_UFc9CRFX0tIj0pdIqGf4/edit?usp=drivesdk" # 본인의 링크로 바꾸세요!

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"🚨 구글 인증 실패: {e}")

@st.cache_data(ttl=5)
def load_data_from_sheet():
    try:
        sheet = client.open_by_url(SHEET_URL).sheet1
        data = sheet.get_all_values()
        parsed_data = []
        if len(data) > 1:
            for row in data[1:]:
                if not row or not row[0]: continue
                try:
                    clean_row = [int(str(x).replace(',', '').strip()) for x in row[:8]]
                    parsed_data.append(clean_row)
                except ValueError: continue
        parsed_data.sort(key=lambda x: x[0]) 
        return parsed_data
    except Exception as e:
        st.error(f"🚨 데이터 로드 에러: {e}")
        return []

current_data = load_data_from_sheet()

st.title("🎯 로또 패턴 분석 & 행운 번호 추천")

# 0. 패턴 분석
if len(current_data) >= 5:
    analyze_count = min(30, len(current_data) - 4)
    recent_analysis_data = current_data[-(analyze_count + 4):]
    pattern_list = []
    for i in range(4, len(recent_analysis_data)):
        curr_draw = recent_analysis_data[i]
        prev_4_draws = recent_analysis_data[i-4:i]
        appeared = [n for d in prev_4_draws for n in d[1:7]]
        freq = {n: appeared.count(n) for n in range(1, 46)}
        wns = curr_draw[1:7]
        c0 = sum(1 for w in wns if freq[w] == 0)
        c1 = sum(1 for w in wns if freq[w] == 1)
        c2 = sum(1 for w in wns if freq[w] >= 2)
        pattern_list.append(f"{c0}:{c1}:{c2}")
    pattern_counts = Counter(pattern_list)
    df_patterns = pd.DataFrame(pattern_counts.items(), columns=["패턴", "출현 횟수"]).sort_values(by="출현 횟수", ascending=False)

    # 1. 그래프 및 통계 출력
    col_chart, col_stat = st.columns([2, 1])
    with col_chart:
        st.subheader("📊 패턴 출현 빈도 그래프")
        st.bar_chart(df_patterns.set_index("패턴"))
    with col_stat:
        st.subheader("📋 통계 표")
        st.dataframe(df_patterns, use_container_width=True)

    # 2. 번호 추천
    st.subheader("🎲 번호 추천")
    latest_4 = current_data[-4:]
    recent_appeared = [n for d in latest_4 for n in d[1:7]]
    current_freq = {n: recent_appeared.count(n) for n in range(1, 46)}
    pool_0 = [n for n, c in current_freq.items() if c == 0]
    pool_1 = [n for n, c in current_freq.items() if c == 1]
    pool_2plus = [n for n, c in current_freq.items() if c >= 2]

    options = ["모든 패턴에서 랜덤 섞기"] + [f"{p} 패턴" for p in df_patterns['패턴']]
    target_pattern = st.selectbox("패턴 선택", options)

    if st.button("행운 번호 뽑기! 🍀"):
        if "랜덤" in target_pattern:
            p_str = random.choices(list(pattern_counts.keys()), weights=list(pattern_counts.values()))[0]
        else:
            p_str = target_pattern.split(" ")[0]
        p0, p1, p2 = map(int, p_str.split(":"))
        if len(pool_0) >= p0 and len(pool_1) >= p1 and len(pool_2plus) >= p2:
            rec = random.sample(pool_0, p0) + random.sample(pool_1, p1) + random.sample(pool_2plus, p2)
            st.success(f"🎉 추천 번호: {', '.join(map(str, sorted(rec)))}")
        else:
            st.error("숫자 풀이 부족합니다.")

st.divider()

# 3. 데이터 관리
with st.expander("⚙️ 데이터베이스 관리"):
    tab1, tab2, tab3 = st.tabs(["📝 신규 입력", "✏️ 수정", "🗑️ 삭제"])
    with tab1:
        with st.form("new"):
            cols = st.columns(8)
            draw_no = cols[0].number_input("회차", value=int(current_data[-1][0])+1 if current_data else 1)
            nums = [cols[i+1].number_input(f"번호{i+1}", min_value=1, max_value=45, value=i+1) for i in range(6)]
            bonus = cols[7].number_input("보너스", min_value=1, max_value=45, value=7)
            if st.form_submit_button("추가"):
                client.open_by_url(SHEET_URL).sheet1.append_row([draw_no] + nums + [bonus])
                st.rerun()

    with tab2:
        if current_data:
            target = st.selectbox("수정 회차", [r[0] for r in reversed(current_data)])
            if st.button("해당 회차 수정"): st.warning("수정 기능 구현 중...")

    with tab3:
        if st.button("마지막 회차 삭제"):
            client.open_by_url(SHEET_URL).sheet1.delete_rows(len(current_data)+1)
            st.rerun()

# 4. 용지 패턴 시각화
st.divider()
st.subheader("📍 최근 5회차 용지 패턴 (시각화)")
if len(current_data) >= 5:
    recent_5 = list(reversed(current_data[-5:]))
    tabs = st.tabs([f"{row[0]}회차" for row in recent_5])
    for i, tab in enumerate(tabs):
        with tab:
            win_nums, bonus = recent_5[i][1:7], recent_5[i][7]
            grid_html = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; max-width: 320px;'>"
            for n in range(1, 46):
                style = "background:#ff4b4b; color:white;" if n in win_nums else "background:#00cc66; color:white;" if n==bonus else "background:white; color:#ff9999; border:1px solid #ffcccc;"
                grid_html += f"<div style='{style} border-radius:4px; padding:10px 0; text-align:center;'>{n}</div>"
            st.markdown(grid_html + "</div>", unsafe_allow_html=True)
