import streamlit as st
import pandas as pd
import random

# 페이지 설정
st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

st.title("🎯 로또 직전 4회차 패턴 자동 분석기")
st.markdown("새로운 회차의 당첨번호를 입력하여 패턴을 분석하고, 인기 패턴 기반으로 번호를 추천받아 보세요!")

# 세션 상태에 초기 샘플 데이터 저장
if 'lotto_data' not in st.session_state:
    st.session_state.lotto_data = [
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
            
        pattern_str = f"{cnt_0} : {cnt_1} : {cnt_2plus}"
        st.success(f"✅ **{draw_no}회차 분석 완료!**")
        st.info(f"**도출된 패턴:** 🎯 {pattern_str} (미출현 {cnt_0}개, 1회출현 {cnt_1}개, 2회이상 {cnt_2plus}개)")
        st.session_state.lotto_data.append(new_draw)
    else:
        st.error("직전 4회차 이상의 데이터가 필요합니다.")

st.divider()

# --- 2. 인기 패턴 기반 랜덤 추천기 ---
st.subheader("🎲 인기 패턴 기반 번호 추천")
st.write("DB에 등록된 가장 최근 4회차 데이터를 기준으로 번호를 추출합니다.")

# 현재 DB 기준 번호 풀(Pool) 계산
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

    # 현재 번호 풀 상태 보여주기
    st.caption(f"📊 현재 번호 풀 (미출현: {len(pool_0)}개 / 1회출현: {len(pool_1)}개 / 2회이상: {len(pool_2plus)}개)")

    # 패턴 선택 UI
    col1, col2 = st.columns([2, 1])
    with col1:
        target_pattern = st.selectbox(
            "원하시는 패턴을 선택하세요 (0회 : 1회 : 2회이상)",
            ["4:2:0 패턴 (가장 자주 등장)", "3:2:1 패턴", "3:3:0 패턴", "5:1:0 패턴", "4:1:1 패턴", "2:4:0 패턴"]
        )
    with col2:
        st.write("") # 줄맞춤용
        st.write("")
        gen_btn = st.button("행운 번호 뽑기! 🍀", use_container_width=True)

    if gen_btn:
        # "4:2:0 패턴 (가장 자주 등장)" 문자열에서 숫자만 분리
        p_str = target_pattern.split(" ")[0] # "4:2:0"
        p0, p1, p2 = map(int, p_str.split(":"))
        
        # 남은 번호 풀이 충분한지 확인
        if len(pool_0) >= p0 and len(pool_1) >= p1 and len(pool_2plus) >= p2:
            rec_nums = random.sample(pool_0, p0) + random.sample(pool_1, p1) + random.sample(pool_2plus, p2)
            rec_nums.sort()
            
            # 보기 좋게 출력
            st.success(f"🎉 **추천 번호:** {', '.join(map(str, rec_nums))}")
        else:
            st.error("현재 누적된 번호 풀의 숫자가 부족하여 해당 패턴을 생성할 수 없습니다.")

st.divider()

# --- 3. 누적 데이터베이스 ---
st.subheader("📊 누적 당첨번호 데이터베이스")
df = pd.DataFrame(st.session_state.lotto_data, columns=['회차', '번호1', '번호2', '번호3', '번호4', '번호5', '번호6', '보너스'])
st.dataframe(df.sort_values(by='회차', ascending=False), use_container_width=True)
