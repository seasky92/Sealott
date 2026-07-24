import streamlit as st
import pandas as pd
import random
import gspread
from google.oauth2.service_account import Credentials

# 기본 세팅
st.set_page_config(page_title="로또 분석", layout="centered")
SHEET_URL = "lot0723-2@lot-bot2.iam.gserviceaccount.com" # 여기에 본인의 시트 주소 붙여넣기!

# 구글 인증
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(creds)

# 데이터 로드
@st.cache_data(ttl=5)
def get_data():
    sheet = client.open_by_url(SHEET_URL).sheet1
    return sheet.get_all_values()

data = get_data()
df = pd.DataFrame(data[1:], columns=data[0])

st.title("🎯 로또 번호 추천기")

# 번호 추천 (단순 랜덤)
if st.button("행운 번호 추천받기"):
    nums = random.sample(range(1, 46), 6)
    st.success(f"추천 번호: {sorted(nums)}")

# 데이터 확인
with st.expander("저장된 데이터 보기"):
    st.dataframe(df)

# 간단한 데이터 입력
with st.form("add_form"):
    st.write("새 회차 입력")
    row = [st.text_input(f"번호{i+1}") for i in range(7)]
    if st.form_submit_button("저장"):
        client.open_by_url(SHEET_URL).sheet1.append_row(row)
        st.rerun()
