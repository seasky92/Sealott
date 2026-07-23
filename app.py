import streamlit as st
import pandas as pd
import random
from collections import Counter
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------
# 1. 페이지 설정 및 구글 시트 연동 세팅
# ---------------------------------------------
st.set_page_config(page_title="로또 패턴 분석기", page_icon="🎯", layout="wide")

# 👇👇👇 복사하신 구글 시트 링크(URL)를 아래 따옴표 안에 꼭 붙여넣어 주세요! 👇👇👇
SHEET_URL = "https://docs.google.com/spreadsheets/d/1tW8KwjFh9PZEoLxNyoiboi_UFc9CRFX0tIj0pdIqGf4/edit?usp=drivesdk"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"🚨 구글 인증 실패: {e}")

@st.cache_data(ttl=5)
def load_data_from_sheet():
    try:
        # 이름 대신 주소(URL)로 정확히 찾아가서 엽니다.
        sheet = client.open_by_url(SHEET_URL).sheet1
        data = sheet.get_all_values()
        
        parsed_data = []
        if len(data) > 1:
            for idx, row in enumerate(data[1:]):
                if not row or not row[0]: continue
                try:
                    clean_row = [int(str(x).replace(',', '').strip()) for x in row[:8]]
                    parsed_data.append(clean_row)
                except ValueError:
                    continue
                    
        parsed_data.sort(key=lambda x: x[0]) 
        return parsed_data
    except Exception as e:
        st.error(f"🚨 구글 시트 데이터를 불러오는 중 에러가 발생했습니다: {e}")
        return []

current_data = load_data_from_sheet()

st.title("🎯 로또 직전 4회차 패턴 자동 분석기 (DB연동형)")
st.markdown("새로운 당첨번호를 입력하면 구글 시트(DB)에 자동 저장되며 패턴을 분석합니다.")

if 'success_msg' in st.session_state:
    st.success(st.session_state.success_msg)
    del st.session_state.success_msg
if 'error_msg' in st.session_state:
    st.error(st.session_state.error_msg)
    del st.session_state.error_msg

analyze_count = 0
df_patterns = pd.DataFrame()
pattern_counts = Counter()

if len(current_data) >= 5: 
    analyze_count = min(20, len(current_data) - 4)
    recent_analysis_data = current_data[-(analyze_count + 4):]
    
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

st.subheader("🎲 인기 패턴 기반 번호 추천")
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

    base_patterns = ["2:4:0", "4:2:0", "4:1:1", "3:2:1", "3:3:0", "5:1:0"]
    sorted_patterns = [p for p, c in pattern_counts.most_common()]
    for bp in base_patterns:
        if bp not in sorted_patterns:
            sorted_patterns.append(bp)
            
    selectbox_options = []
    for i, p in enumerate(sorted_patterns[:8]): 
        if i == 0 and len(pattern_counts) > 0:
            selectbox_options.append(f"{p} 패턴 (⭐최근 1위)")
        else:
            selectbox_options.append(f"{p} 패턴")

    col1, col2 = st.columns([2, 1])
    with col1:
        target_pattern = st.selectbox("원하시는 패턴을 선택하세요", selectbox_options)
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
            st.error("숫자가 부족하여 해당 패턴을 생성할 수 없습니다.")

st.divider()

st.subheader("📈 최근 20회차 패턴 출현 통계")
if not df_patterns.empty: 
    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        st.dataframe(df_patterns, use_container_width=True)
    with col_chart2:
        st.bar_chart(df_patterns.set_index("패턴"))

st.divider()

st.subheader("⚙️ 데이터베이스 관리")
tab1, tab2, tab3 = st.tabs(["📝 신규 입력", "✏️ 특정 회차 수정", "🗑️ 마지막 데이터 삭제"])

with tab1:
    with st.form("new_draw_form"):
        cols = st.columns(8)
        last_draw_no = int(current_data[-1][0]) if current_data else 1230
        draw_no = cols[0].number_input("회차", value=last_draw_no + 1, step=1)
        n1 = cols[1].number_input("번호1", min_value=1, max_value=45, value=1)
        n2 = cols[2].number_input("번호2", min_value=1, max_value=45, value=2)
        n3 = cols[3].number_input("번호3", min_value=1, max_value=45, value=3)
        n4 = cols[4].number_input("번호4", min_value=1, max_value=45, value=4)
        n5 = cols[5].number_input("번호5", min_value=1, max_value=45, value=5)
        n6 = cols[6].number_input("번호6", min_value=1, max_value=45, value=6)
        bonus = cols[7].number_input("보너스", min_value=1, max_value=45, value=7)
        submitted = st.form_submit_button("DB에 영구 저장")

    if submitted:
        new_draw = [draw_no, n1, n2, n3, n4, n5, n6, bonus]
        try:
            sheet = client.open_by_url(SHEET_URL).sheet1
            sheet.append_row(new_draw)
            load_data_from_sheet.clear() 
            st.session_state.success_msg = f"✅ **{draw_no}회차 데이터 추가 완료!**"
            st.rerun()
        except Exception as e:
            st.session_state.error_msg = f"저장 실패: {e}"
            st.rerun()

with tab2:
    if current_data:
        draw_list = [row[0] for row in reversed(current_data)]
        target_edit = st.selectbox("수정할 회차 선택", draw_list)
        target_row_data = next((row for row in current_data if row[0] == target_edit), None)
        
        if target_row_data:
            with st.form("edit_form"):
                cols = st.columns(8)
                e_n1 = cols[1].number_input("번호1", min_value=1, max_value=45, value=target_row_data[1], key="e_n1")
                e_n2 = cols[2].number_input("번호2", min_value=1, max_value=45, value=target_row_data[2], key="e_n2")
                e_n3 = cols[3].number_input("번호3", min_value=1, max_value=45, value=target_row_data[3], key="e_n3")
                e_n4 = cols[4].number_input("번호4", min_value=1, max_value=45, value=target_row_data[4], key="e_n4")
                e_n5 = cols[5].number_input("번호5", min_value=1, max_value=45, value=target_row_data[5], key="e_n5")
                e_n6 = cols[6].number_input("번호6", min_value=1, max_value=45, value=target_row_data[6], key="e_n6")
                e_bonus = cols[7].number_input("보너스", min_value=1, max_value=45, value=target_row_data[7], key="e_bonus")
                edit_submitted = st.form_submit_button("수정 완료")
                
            if edit_submitted:
                try:
                    sheet = client.open_by_url(SHEET_URL).sheet1
                    cell = sheet.find(str(target_edit), in_column=1)
                    if cell:
                        sheet.update(f'B{cell.row}:H{cell.row}', [[e_n1, e_n2, e_n3, e_n4, e_n5, e_n6, e_bonus]])
                        load_data_from_sheet.clear()
                        st.session_state.success_msg = f"🔄 **{target_edit}회차 수정 완료!**"
                        st.rerun()
                except Exception as e:
                    st.error(f"수정 실패: {e}")

with tab3:
    if current_data:
        last_added = current_data[-1]
        st.write(f"마지막 데이터: **{last_added[0]}회차**")
        if st.button("🚨 맨 아랫줄 삭제하기", type="primary"):
            try:
                sheet = client.open_by_url(SHEET_URL).sheet1
                sheet.delete_rows(len(current_data) + 1)
                load_data_from_sheet.clear()
                st.session_state.success_msg = f"🗑️ **{last_added[0]}회차 삭제 완료!**"
                st.rerun()
            except Exception as e:
                st.error(f"삭제 실패: {e}")

st.divider()

st.subheader("📊 누적 당첨번호 데이터베이스")
display_data = []
for i in range(len(current_data)):
    row = current_data[i]
    if i >= 4:
        prev_4 = current_data[i-4:i]
        appeared_nums = []
        for d in prev_4: appeared_nums.extend(d[1:8])
        freq = {n: 0 for n in range(1, 46)}
        for n in appeared_nums: freq[n] += 1
        wns = row[1:7]
        c0, c1, c2 = 0, 0, 0
        for w in wns:
            if freq[w] == 0: c0 += 1
            elif freq[w] == 1: c1 += 1
            else: c2 += 1
        pattern_str = f"{c0}:{c1}:{c2}"
    else:
        pattern_str = "-" 
    display_data.append(row + [pattern_str])

df_display = pd.DataFrame(display_data, columns=['회차', '번호1', '번호2', '번호3', '번호4', '번호5', '번호6', '보너스', '출현패턴'])
st.dataframe(df_display.sort_values(by='회차', ascending=False), use_container_width=True)
