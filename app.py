import streamlit as st
import pandas as pd
import random
from collections import Counter
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

SHEET_URL = "여기에_구글시트_링크를_붙여넣으세요" # 본인의 링크로 바꾸세요!

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

    # 2. 번호 추천 (랜덤 패턴 추가)
    st.subheader("🎲 번호 추천")
    latest_4 = current_data[-4:]
    recent_appeared = [n for d in latest_4 for n in d[1:7]]
    current_freq = {n: recent_appeared.count(n) for n in range(1, 46)}
    pool_0 = [n for n, c in current_freq.items() if c == 0]
    pool_1 = [n for n, c in current_freq.items() if c == 1]
    pool_2plus = [n for n, c in current_freq.items() if c >= 2]

    # 패턴 선택 옵션
    options = ["모든 패턴에서 랜덤 섞기"] + [f"{p} 패턴" for p in df_patterns['패턴']]
    target_pattern = st.selectbox("패턴 선택", options)

    if st.button("행운 번호 뽑기! 🍀"):
        if "랜덤" in target_pattern:
            # 모든 패턴의 가중치를 반영하여 랜덤 선택
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

# 3. 데이터 관리 및 시각화 (용지 패턴은 맨 아래)
with st.expander("⚙️ 데이터베이스 관리"):
    st.write("데이터 수정 및 관리는 여기서 수행하세요.")
    # (기존 입력/수정/삭제 폼 코드 유지)

st.subheader("📍 최근 5회차 용지 패턴 (시각화)")
# (기존 용지 패턴 코드 유지)
