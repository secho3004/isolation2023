import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="MZ세대 고립 분석 리포트", layout="wide")

st.title("분석3: 저소득층에게 음주의 자리를 대체한 것은 무엇인가?")
st.subheader("데이터로 보는 MZ세대 저소득층의 고립 실태")

# 데이터 출처 및 배경 설명
st.info("""
**📊 데이터 출처:** 한국인의 행복조사 2023 (KOSSDA), MZ세대 19~39세 (n=4,626명)  
**🔍 분석 배경:** 지난 분석에서 '금주 트렌드'를 확인했습니다. 하지만 이 트렌드가 모두에게 긍정적일까요? 
저소득층에게 술이 사라진 자리에 '건강한 취미'가 채워졌는지, 아니면 '사회적 고립'이 채워졌는지 실증합니다.
""")

# 2. DB 연결 및 데이터 로드 함수
DB_FILE = "isolation2023.db"

def run_query(query):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(query, conn)

# DB 파일 존재 확인
if not os.path.exists(DB_FILE):
    st.error(f"🚨 '{DB_FILE}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# 소득그룹 순서 정의 (차트 정렬용)
income_order = ["저소득", "중간", "고소득"]

# --- 분석 1: 소득그룹별 음주율 ---
st.markdown("---")
st.header("1. 소득그룹별 음주율 비교")

sql1 = """
SELECT 소득그룹, 
       AVG(CASE WHEN 음주여부 = '예' THEN 1 ELSE 0 END) * 100 as 음주율
FROM mz_isolation
GROUP BY 소득그룹
"""
df1 = run_query(sql1)
df1['소득그룹'] = pd.Categorical(df1['소득그룹'], categories=income_order, ordered=True)
df1 = df1.sort_values('소득그룹')

fig1 = px.bar(df1, x='소득그룹', y='음주율', text_auto='.1f', color='소득그룹',
             color_discrete_map={'저소득':'#EF553B', '중간':'#636EFA', '고소득':'#00CC96'})
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql1, language='sql')
    st.write("- **인사이트:** 저소득층의 음주율이 고소득층보다 낮거나 비슷하게 나타납니다. '가난할수록 술에 의존한다'는 통념과 달리, 실제 데이터는 저소득층이 경제적 부담 등으로 인해 술을 덜 마시는 경향을 보여줍니다.")

# --- 분석 2: 소득그룹별 단체참여율 ---
st.header("2. 소득그룹별 단체참여율 비교")

sql2 = """
SELECT 소득그룹, 
       AVG(단체참여여부) * 100 as 참여율
FROM mz_isolation
GROUP BY 소득그룹
"""
df2 = run_query(sql2)
df2['소득그룹'] = pd.Categorical(df2['소득그룹'], categories=income_order, ordered=True)
df2 = df2.sort_values('소득그룹')

fig2 = px.bar(df2, x='소득그룹', y='참여율', text_auto='.1f', color='소득그룹',
             color_discrete_sequence=['#FFA15A'])
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql2, language='sql')
    st.write("- **인사이트:** 음주를 하지 않는다면 다른 모임에 참여할까요? 데이터는 그렇지 않다고 말합니다. 저소득층의 단체 참여율은 고소득층에 비해 현저히 낮아, 술 대신 선택할 수 있는 사회적 연결망이 부족함을 보여줍니다.")

# --- 분석 3: 이중배제율 비교 (핵심) ---
st.header("3. 사회적 이중배제율 (음주X & 단체X)")

sql3 = """
SELECT 소득그룹, 
       AVG(이중배제) * 100 as 이중배제율
FROM mz_isolation
GROUP BY 소득그룹
"""
df3 = run_query(sql3)
df3['소득그룹'] = pd.Categorical(df3['소득그룹'], categories=income_order, ordered=True)
df3 = df3.sort_values('소득그룹')

fig3 = px.bar(df3, x='소득그룹', y='이중배제율', text_auto='.1f', color='소득그룹',
             color_discrete_map={'저소득':'#FF4B4B', '중간':'#AB63FA', '고소득':'#19D3AF'})
st.plotly_chart(fig3, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql3, language='sql')
    st.write(f"- **인사이트:** 이번 분석의 핵심입니다. **저소득층의 이중배제율은 16.9%**로, 고소득층(4.3%)보다 약 4배나 높습니다. 이는 저소득층에게 술의 부재가 곧 '고립'으로 직결될 위험이 크다는 것을 의미합니다.")

# --- 분석 4: 소득분위별 이중배제율 추이 ---
st.header("4. 소득분위별 이중배제율 추이")

sql4 = """
SELECT 소득코드, 
       AVG(이중배제) * 100 as 이중배제율
FROM mz_isolation
GROUP BY 소득코드
ORDER BY 소득코드
"""
df4 = run_query(sql4)

fig4 = px.line(df4, x='소득코드', y='이중배제율', markers=True, 
              title="소득이 낮아질수록 가팔라지는 고립의 곡선")
st.plotly_chart(fig4, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql4, language='sql')
    st.write("- **인사이트:** 소득코드(1~7)가 낮아질수록(소득이 적을수록) 이중배제율이 계단식으로 상승하는 뚜렷한 패턴을 보입니다. 경제적 빈곤이 사회적 관계의 빈곤으로 이어지는 '고립의 공식'이 데이터로 증명되었습니다.")

st.markdown("---")
st.caption("Developed by Senior Developer Mentor | Python + Streamlit + SQLite")