import streamlit as st
import pandas as pd
import random
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

st.title("🎯 로또 직전 4회차 패턴 자동 분석기")
st.markdown("새로운 당첨번호를 입력하여 패턴을 분석하고, 인기 패턴 기반으로 번호를 추천받아 보세요!")

# 세션 상태에 초기 샘플 데이터 저장
if 'lotto_data' not in st.session_state:
    st.session_state.lotto_data = [
        [1210, 1, 7, 9, 17, 27, 38, 31],
        [1211, 23, 26, 27, 35, 38, 40, 10],
        [1212, 5, 8, 25, 31, 41, 44, 45],
        [1213, 5, 11, 25, 27, 36, 38, 2],
        [1214, 10, 15, 19, 27, 30, 33, 14],
        [1215, 13, 15, 19, 21, 44, 45, 39],
        [1216, 3, 10, 14, 15, 23, 24, 25],
        [1217, 8, 10, 15, 20, 29, 31, 41],
        [1218, 3, 28, 31, 32, 42, 45, 25],
        [1219, 1, 2, 15, 28, 39, 45, 31],
        [1220, 2, 22, 25, 28, 34, 43, 16],
        [1221, 6, 13, 18, 28, 30, 36, 9],
        [1222, 4, 11, 17, 22, 32, 41, 34],
        [1223, 16, 18, 20, 32, 33, 39, 26],
        [1224, 9, 18, 21, 27, 44, 45, 28],
        [1225, 8, 9, 19, 25, 41, 42, 33],
        [1226, 4, 6, 13, 17, 26, 28, 41],
        [1227, 1, 14, 16, 34, 41, 44, 13],
        [1228, 24, 29, 30, 31, 35, 44, 1],
        [1229, 12, 13, 29, 34, 37, 42, 16],
        [1230, 3, 8, 9, 22, 28, 42, 45],
        [1231, 4, 13, 14, 18, 31, 38, 15],
        [1232, 12, 15, 19, 22, 24, 36, 3]
    ]

# --- 1. 신규 번호 입력부 ---
st.subheader("📝 신규 당첨번호 입력")
with st.form("new_draw_form"):
    cols = st.columns(8)
    last_draw_no = st.session_state.lotto_data[-1][0]
    
    draw_no = cols[0].number_input("회차", value=last_draw_no + 1, step=1)
    n1 = cols[1].number_input("번호1", min_value=1, max_value=45, value=1)
    n2 = cols[2].number_input("번호2", min_value=1, max_value=45, value=2)
    n3 = cols[3].number_input("번호3", min_value=1, max_value=45, value=3)
    n4 = cols[4].number_input("번호4", min_value=1, max_value=45, value=4)
    n5 = cols[5].number_input("번호5", min_value=1, max_value=45, value=5)
    n6 = cols[6].number_input("번호6", min_value=1, max_value=45, value=6)
    bonus = cols[7].number_input("보너스", min_value=1, max_value=45, value=7)
    
    submitted = st.form_submit_button("패턴 분석 및 DB에 추가하기")

if submitted:
    new_draw = [draw_no, n1, n2, n3, n4, n5, n6, bonus]
    winning_nums = [n1, n2, n3, n4, n5, n6]
    data = st.session_state.lotto_data
    
    if len(data) >= 4:
        prev_4 = data[-4:]
        appeared_nums = []
        for d in prev_4:
            appeared_nums.extend(d[1:8])
            
        freq = {n: 0 for n in range(1, 46)}
        for n in appeared_nums:
            freq[n] += 1
            
        cnt_0, cnt_1, cnt_2plus = 0, 0, 0
        for wn in winning_nums:
            if freq[wn] == 0: cnt_0 += 1
            elif freq[wn] == 1: cnt_1 += 1
            else: cnt_2plus += 1
            
        pattern_str = f"{cnt_0}:{cnt_1}:{cnt_2plus}"
        st.success(f"✅ **{draw_no}회차 분석 완료!**")
        st.info(f"**도출된 패턴:** 🎯 {pattern_str} (미출현 {cnt_0}개, 1회출현 {cnt_1}개, 2회이상 {cnt_2plus}개)")
        st.session_state.lotto_data.append(new_draw)
    else:
        st.error("직전 4회차 이상의 데이터가 필요합니다.")

st.divider()

# --- 2. 최근 20회차 패턴 통계 ---
st.subheader("📈 최근 20회차 패턴 출현 통계")
data = st.session_state.lotto_data

if len(data) >= 5: 
    analyze_count = min(20, len(data) - 4)
    recent_analysis_data = data[-(analyze_count + 4):]
    
    pattern_list = []
    
    for i in range(4, len(recent_analysis_data)):
        curr_draw = recent_analysis_data[i]
        prev_4_draws = recent_analysis_data[i-4:i]
        
        appeared = []
        for d in prev_4_draws:
            appeared.extend(d[1:8])
            
        freq = {n: 0 for n in range(1, 46)}
        for n in appeared:
            freq[n] += 1
            
        wns = curr_draw[1:7]
        c0, c1, c2 = 0, 0, 0
        for w in wns:
            if freq[w] == 0: c0 += 1
            elif freq[w] == 1: c1 += 1
            else: c2 += 1
            
        pattern_list.append(f"{c0}:{c1}:{c2}")
        
    pattern_counts = Counter(pattern_list)
    df_patterns = pd.DataFrame(pattern_counts.items(), columns=["패턴", "출현 횟수"])
    df_patterns = df_patterns.sort_values(by="출현 횟수", ascending=False).reset_index(drop=True)
    
    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        st.write(f"**최근 {analyze_count}회 동안의 패턴 순위**")
        st.dataframe(df_patterns, use_container_width=True)
    with col_chart2:
        st.bar_chart(df_patterns.set_index("패턴"))
else:
    st.info("패턴 통계를 보려면 최소 5개 회차 이상의 데이터가 필요합니다.")

st.divider()

# --- 3. 인기 패턴 기반 랜덤 추천기 ---
st.subheader("🎲 인기 패턴 기반 번호 추천")
st.write("DB에 등록된 가장 최근 4회차 데이터를 기준으로 번호를 추출합니다.")

current_data = st.session_state.lotto_data
if len(current_data) >= 4:
    latest_4 = current_data[-4:]
    recent_appeared = []
    for d in latest_4:
        recent_appeared.extend(d[1:8])
        
    current_freq = {n: 0 for n in range(1, 46)}
    for n in recent_appeared:
        current_freq[n] += 1
        
    pool_0 = [n for n, c in current_freq.items() if c == 0]
    pool_1 = [n for n, c in current_freq.items() if c == 1]
    pool_2plus = [n for n, c in current_freq.items() if c >= 2]

    st.caption(f"📊 현재 번호 풀 (미출현: {len(pool_0)}개 / 1회출현: {len(pool_1)}개 / 2회이상: {len(pool_2plus)}개)")

    col1, col2 = st.columns([2, 1])
    with col1:
        target_pattern = st.selectbox(
            "원하시는 패턴을 선택하세요 (0회 : 1회 : 2회이상)",
            ["4:2:0 패턴 (가장 자주 등장)", "3:2:1 패턴", "3:3:0 패턴", "5:1:0 패턴", "4:1:1 패턴", "2:4:0 패턴"]
        )
    with col2:
        st.write("") 
        st.write("")
        gen_btn = st.button("행운 번호 뽑기! 🍀", use_container_width=True)

    if gen_btn:
        p_str = target_pattern.split(" ")[0] 
        p0, p1, p2 = map(int, p_str.split(":"))
        
        if len(pool_0) >= p0 and len(pool_1) >= p1 and len(pool_2plus) >= p2:
            rec_nums = random.sample(pool_0, p0) + random.sample(pool_1, p1) + random.sample(pool_2plus, p2)
            rec_nums.sort()
            
            st.success(f"🎉 **추천 번호:** {', '.join(map(str, rec_nums))}")
        else:
            st.error("현재 누적된 번호 풀의 숫자가 부족하여 해당 패턴을 생성할 수 없습니다.")

st.divider()

# --- 4. 누적 데이터베이스 (패턴 열 추가 반영) ---
st.subheader("📊 누적 당첨번호 데이터베이스")

data = st.session_state.lotto_data
display_data = []

# 각 회차별로 패턴을 계산하여 리스트에 추가
for i in range(len(data)):
    row = data[i]
    if i >= 4:
        prev_4 = data[i-4:i]
        appeared_nums = []
        for d in prev_4:
            appeared_nums.extend(d[1:8])
            
        freq = {n: 0 for n in range(1, 46)}
        for n in appeared_nums:
            freq[n] += 1
            
        wns = row[1:7]
        c0, c1, c2 = 0, 0, 0
        for w in wns:
            if freq[w] == 0: c0 += 1
            elif freq[w] == 1: c1 += 1
            else: c2 += 1
        pattern_str = f"{c0}:{c1}:{c2}"
    else:
        # 데이터가 부족한 최초 4회차는 계산 불가 표시
        pattern_str = "-" 
        
    display_data.append(row + [pattern_str])

# 데이터프레임 생성 및 출력
df = pd.DataFrame(display_data, columns=['회차', '번호1', '번호2', '번호3', '번호4', '번호5', '번호6', '보너스', '출현패턴'])
st.dataframe(df.sort_values(by='회차', ascending=False), use_container_width=True)
