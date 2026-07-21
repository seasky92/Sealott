import streamlit as st
import pandas as pd
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

st.title("🎯 로또 직전 4회차 패턴 자동 분석기")
st.markdown("새로운 회차의 당첨번호를 입력하면, 직전 4회차 데이터를 바탕으로 **`0회 : 1회 : 2회이상`** 출현 패턴을 즉시 분석해 줍니다.")

# 세션 상태(Session State)에 초기 샘플 데이터 저장 (앱이 새로고침되어도 데이터 유지)
if 'lotto_data' not in st.session_state:
    # 1229회 ~ 1232회 초기 데이터 셋팅
    st.session_state.lotto_data = [
        [1229, 12, 13, 29, 34, 37, 42, 16],
        [1230, 3, 8, 9, 22, 28, 42, 45],
        [1231, 4, 13, 14, 18, 31, 38, 15],
        [1232, 12, 15, 19, 22, 24, 36, 3]
    ]

# --- UI: 신규 번호 입력부 ---
st.subheader("📝 신규 당첨번호 입력")
with st.form("new_draw_form"):
    cols = st.columns(8)
    
    # 마지막 입력된 회차 + 1을 기본값으로 설정
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

# --- 로직: 패턴 분석 및 추가 ---
if submitted:
    new_draw = [draw_no, n1, n2, n3, n4, n5, n6, bonus]
    winning_nums = [n1, n2, n3, n4, n5, n6]
    
    data = st.session_state.lotto_data
    
    if len(data) >= 4:
        # 직전 4회차 데이터 추출
        prev_4 = data[-4:]
        appeared_nums = []
        for d in prev_4:
            appeared_nums.extend(d[1:8]) # 6개 번호 + 보너스 번호 포함
            
        # 출현 빈도 계산
        freq = {n: 0 for n in range(1, 46)}
        for n in appeared_nums:
            freq[n] += 1
            
        # 이번 회차 당첨번호 패턴 분석
        cnt_0, cnt_1, cnt_2plus = 0, 0, 0
        for wn in winning_nums:
            if freq[wn] == 0: cnt_0 += 1
            elif freq[wn] == 1: cnt_1 += 1
            else: cnt_2plus += 1
            
        pattern_str = f"{cnt_0} : {cnt_1} : {cnt_2plus}"
        
        # 분석 결과 시각화
        st.success(f"✅ **{draw_no}회차 분석 완료!**")
        st.info(f"**도출된 패턴:** 🎯 {pattern_str} (미출현 {cnt_0}개, 1회출현 {cnt_1}개, 2회이상 {cnt_2plus}개)")
        
        # 데이터를 세션(DB)에 추가
        st.session_state.lotto_data.append(new_draw)
    else:
        st.error("직전 4회차 이상의 데이터가 필요합니다.")

st.divider()

# --- UI: 누적 데이터 및 통계 확인 ---
st.subheader("📊 누적 당첨번호 데이터베이스")
df = pd.DataFrame(st.session_state.lotto_data, columns=['회차', '번호1', '번호2', '번호3', '번호4', '번호5', '번호6', '보너스'])

# 최신 데이터가 위로 오도록 정렬
st.dataframe(df.sort_values(by='회차', ascending=False), use_container_width=True)
