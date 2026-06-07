
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os
 
st.set_page_config(page_title="분석3: MZ세대 고립 분석", layout="wide")
 
DB_FILE = "isolation2023.db"
if not os.path.exists(DB_FILE):
    st.error(f"🚨 '{DB_FILE}' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 DB 파일을 넣어주세요.")
    st.stop()
 
@st.cache_data
def run_query(query):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(query, conn)
 
# ── 헤더 ──────────────────────────────────────────────
st.title("분석3: 저소득층에게 음주의 자리를 대체한 것은 무엇인가?")
st.markdown("**데이터:** 한국인의 행복조사 2023 (KOSSDA)")
st.markdown("**대상:** MZ세대 (19~39세), n=4,626명")
st.markdown("**목적:** 분석2의 결론('고립으로 이어질 수 있음')을 이중배제 수치로 직접 실증")
 
st.markdown("---")
 
# ── 분석 배경 ──────────────────────────────────────────
st.header("0. 분석 배경 및 위치")
 
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 분석2의 결론 (한계)")
    st.markdown("""
- 저소득 비음주자의 단체참여가 전 집단 중 최저
- 소득·음주 모두 단체참여에 유의한 정적 영향
- **"금주 트렌드가 저소득층에게는 고립으로 이어질 수 있음"**
""")
    st.error("결과: '수 있음' 수준의 주장으로 남겨짐")
 
with col2:
    st.markdown("#### 분석3의 역할 (실증)")
    st.markdown("""
- 음주도 없고 단체참여도 없는 사람이 **실제로 얼마나 존재하는가**
- 소득그룹별 이중배제율을 직접 산출
- 소득이 낮아질수록 고립이 심화되는 패턴 확인
""")
    st.success("결과: 저소득 16.9% vs 고소득 4.3%, 4배 차이 (p<0.001)")
 
st.markdown("---")
 
# ── KPI ───────────────────────────────────────────────
st.header("1. 핵심 수치")
k1, k2, k3, k4 = st.columns(4)
k1.metric("저소득 이중배제율", "16.9%")
k2.metric("고소득 이중배제율", "4.3%")
k3.metric("저소득 / 고소득 격차", "약 4배")
k4.metric("통계적 유의성", "χ²=40.9, p<0.001")
 
st.markdown("---")
 
COLOR_LOW  = '#636EFA'
COLOR_MID  = '#EF553B'
COLOR_HIGH = '#00CC96'
ORDER = ['저소득', '중간', '고소득']
CMAP = {'저소득': COLOR_LOW, '중간': COLOR_MID, '고소득': COLOR_HIGH}
 
def make_bar(df, x_col, y_col, title):
    df = df.set_index(x_col).loc[ORDER].reset_index()
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col],
        marker_color=[CMAP[g] for g in df[x_col]],
        text=[f"{v:.1f}" for v in df[y_col]],
        textposition='outside',
        width=0.5
    ))
    fig.update_layout(
        title=title,
        yaxis=dict(showgrid=True, gridcolor='#eee', range=[0, df[y_col].max()*1.3]),
        xaxis=dict(showgrid=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=350, margin=dict(t=40, b=20, l=40, r=20),
        showlegend=False
    )
    return fig
 
# ── 차트 1: 이중배제율 ────────────────────────────────
st.header("2. 소득그룹별 이중배제율 (음주X & 단체참여X)")
 
sql1 = """-- 소득그룹별 이중배제 현황
SELECT 소득그룹,
       COUNT(*) AS 전체인원,
       SUM(이중배제) AS 이중배제인원,
       ROUND(AVG(이중배제) * 100, 1) AS 이중배제율
FROM mz_isolation
GROUP BY 소득그룹
ORDER BY CASE 소득그룹
    WHEN '저소득' THEN 1
    WHEN '중간'   THEN 2
    WHEN '고소득' THEN 3
END"""
 
df1 = run_query(sql1)
st.plotly_chart(make_bar(df1, '소득그룹', '이중배제율', '소득그룹별 이중배제율 (%)'), use_container_width=True)
 
st.code(sql1, language='sql')
st.markdown("""
**해석:** 저소득층의 이중배제율(16.9%)은 고소득층(4.3%)보다 약 **4배 높습니다.**
저소득 MZ 6명 중 1명은 음주도, 단체참여도 둘 다 없습니다.
분석2의 "고립으로 이어질 수 있음"이 수치로 실증됩니다.
""")
 
st.markdown("---")
 
# ── 차트 2: 소득분위별 추이 ───────────────────────────
st.header("3. 소득분위별 이중배제율 추이")
 
sql2 = """-- 소득분위별 이중배제율 추이 (표본 10명 이상 구간)
SELECT 소득코드,
       소득레이블,
       COUNT(*) AS 인원수,
       SUM(이중배제) AS 이중배제인원,
       ROUND(AVG(이중배제) * 100, 1) AS 이중배제율
FROM mz_isolation
WHERE 소득코드 <= 7
GROUP BY 소득코드, 소득레이블
ORDER BY 소득코드 ASC"""
 
df2 = run_query(sql2)
 
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df2['소득레이블'], y=df2['이중배제율'],
    mode='lines+markers+text',
    line=dict(color=COLOR_LOW, width=2),
    marker=dict(size=8, color=COLOR_LOW),
    text=[f"{v}%" for v in df2['이중배제율']],
    textposition='top center',
    textfont=dict(size=11)
))
fig2.update_layout(
    title='소득이 낮아질수록 심화되는 고립',
    yaxis=dict(title='이중배제율 (%)', showgrid=True, gridcolor='#eee',
               range=[0, df2['이중배제율'].max() * 1.35]),
    xaxis=dict(title='소득 구간', showgrid=False),
    plot_bgcolor='white', paper_bgcolor='white',
    height=360, margin=dict(t=40, b=40, l=40, r=20)
)
st.plotly_chart(fig2, use_container_width=True)
 
st.code(sql2, language='sql')
st.markdown("""
**해석:** 소득이 낮아질수록 이중배제율이 상승하는 패턴이 뚜렷합니다.
소득없음 구간(19.4%)에서 가장 높고, 소득이 오를수록 감소합니다.
경제적 빈곤이 사회적 관계의 빈곤으로 이어지는 구조가 확인됩니다.
""")
 
st.markdown("---")
 
# ── 요약 ──────────────────────────────────────────────
st.header("4. 분석3 요약")
st.markdown("""
**핵심 발견:**
 
1. **이중배제율 격차 (χ²=40.9, p<0.001):** 저소득 MZ의 16.9%는 음주도 없고 단체참여도 없음 — 고소득(4.3%)의 약 4배
2. **소득분위별 패턴:** 소득이 낮아질수록 이중배제율 상승. 소득없음 구간 19.4%로 최고
 
**결론:** 저소득층에게 음주의 자리를 대체한 것은 '건강한 교류'가 아니라 **'고립'이었습니다.**
분석2의 가설 '금주 트렌드가 저소득층에게는 고립으로 이어질 수 있음'이 수치로 실증되었습니다.
 
**한계:** 본 분석은 횡단면 데이터로 인과관계가 아닌 동반 패턴을 확인한 결과입니다.
이중배제의 원인이 저소득인지, 학력·고용상태 등 다른 요인의 영향인지는 추가 분석이 필요합니다.
""")
 
