import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import os
 
# 1. 페이지 설정
st.set_page_config(page_title="분석3: MZ세대 고립 분석", layout="wide")
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.insight-box {
    background: #f8f9fa; border-left: 5px solid #e63946;
    padding: 14px 18px; border-radius: 4px; margin-top: 8px;
    font-size: 0.9rem; color: #333; line-height: 1.8;
}
.sql-box {
    background: #1e1e2e; color: #cdd6f4;
    padding: 14px 18px; border-radius: 6px;
    font-family: 'Courier New', monospace; font-size: 0.82rem;
    line-height: 1.7; margin-top: 8px; white-space: pre;
}
.kpi-box {
    background: #1a1a2e; color: white;
    padding: 20px 16px; border-radius: 8px; text-align: center;
}
.kpi-num { font-size: 2.2rem; font-weight: 900; color: #e63946; }
.kpi-label { font-size: 0.78rem; color: #aaa; margin-top: 4px; }
.limit-box {
    background: #fff8e1; border: 1px solid #ffe082;
    border-radius: 6px; padding: 12px 16px;
    font-size: 0.82rem; color: #555; margin-top: 24px; line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)
 
# 2. DB 연결
DB_FILE = "isolation2023.db"
if not os.path.exists(DB_FILE):
    st.error(f"🚨 '{DB_FILE}' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 DB 파일을 넣어주세요.")
    st.stop()
 
@st.cache_data
def run_query(query):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql(query, conn)
 
# 3. 헤더
st.title("분석3: 저소득층에게 음주의 자리를 대체한 것은 무엇인가?")
st.markdown("**📊 데이터:** 한국인의 행복조사 2023 (KOSSDA) | 대상: MZ세대 19~39세 (n=4,626명)")
st.info("""
**🔍 분석 배경** \n분석2는 저소득 비음주 MZ세대의 단체참여가 전 집단 중 가장 낮다는 패턴을 확인했으나,
이를 **"수 있음"** 수준의 주장으로 남겼습니다.
분석3은 이를 실증합니다 — 음주도 없고 단체참여도 없는 사람이 **실제로 얼마나 존재하는가.**
""")
 
# KPI 카드
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="kpi-box"><div class="kpi-num">16.9%</div><div class="kpi-label">저소득 이중배제율</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="kpi-box"><div class="kpi-num">4.3%</div><div class="kpi-label">고소득 이중배제율</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="kpi-box"><div class="kpi-num">4배</div><div class="kpi-label">저소득 / 고소득 격차</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="kpi-box"><div class="kpi-num">p&lt;0.001</div><div class="kpi-label">χ²=40.9 (통계적 유의)</div></div>', unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
COLORS = {'저소득': '#e63946', '중간': '#457b9d', '고소득': '#2a9d8f'}
ORDER = ['저소득', '중간', '고소득']
 
def make_bar(df, x_col, y_col, title):
    df = df.set_index(x_col).loc[ORDER].reset_index()
    fig = go.Figure(go.Bar(
        x=df[x_col], y=df[y_col],
        marker_color=[COLORS[g] for g in df[x_col]],
        text=[f"{v:.1f}%" for v in df[y_col]],
        textposition='outside',
        textfont=dict(size=14),
        width=0.45
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color='#1a1a2e')),
        yaxis=dict(showgrid=True, gridcolor='#eee', range=[0, df[y_col].max()*1.3]),
        xaxis=dict(showgrid=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=320, margin=dict(t=40, b=20, l=40, r=20),
        showlegend=False
    )
    return fig
 
st.markdown("---")
 
# ── 차트 1 ──────────────────────────────────────────
st.header("1. 소득그룹별 음주율 비교")
 
sql1 = """SELECT 소득그룹,
       ROUND(AVG(CASE WHEN 음주여부 = '음주' THEN 1.0 ELSE 0 END) * 100, 1) AS 음주율
FROM mz_isolation
GROUP BY 소득그룹"""
 
df1 = run_query(sql1)
st.plotly_chart(make_bar(df1, '소득그룹', '음주율', '소득그룹별 음주율 (%)'), use_container_width=True)
 
st.markdown('<div class="sql-box">' + sql1 + '</div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-box">
💡 <b>인사이트</b><br>
저소득층 음주율(67.6%)은 고소득층(83.8%)보다 <b>16.2%p 낮습니다.</b>
"가난할수록 술에 의존한다"는 통념과 정반대입니다.
저소득층은 경제적 부담으로 음주 자체를 덜 합니다.
그렇다면 술 대신 다른 방식으로 교류하고 있을까요?
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── 차트 2 ──────────────────────────────────────────
st.header("2. 소득그룹별 단체참여율 비교")
 
sql2 = """SELECT 소득그룹,
       ROUND(AVG(단체참여여부) * 100, 1) AS 참여율
FROM mz_isolation
GROUP BY 소득그룹"""
 
df2 = run_query(sql2)
st.plotly_chart(make_bar(df2, '소득그룹', '참여율', '소득그룹별 단체참여율 (%)'), use_container_width=True)
 
st.markdown('<div class="sql-box">' + sql2 + '</div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-box">
💡 <b>인사이트</b><br>
저소득층 단체참여율(48.1%)은 고소득층(69.1%)보다 <b>21%p 낮습니다.</b>
"술 대신 다른 모임에 참여한다"는 반박이 데이터로 부정됩니다.
저소득층은 음주도 적고, 단체활동도 적습니다. <b>대안이 없는 것입니다.</b>
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── 차트 3 (핵심) ────────────────────────────────────
st.header("3. 사회적 이중배제율 — 핵심 발견")
 
sql3 = """SELECT 소득그룹,
       ROUND(AVG(이중배제) * 100, 1) AS 이중배제율
FROM mz_isolation
GROUP BY 소득그룹"""
 
df3 = run_query(sql3)
st.plotly_chart(make_bar(df3, '소득그룹', '이중배제율', '이중배제율: 음주도 없고 단체참여도 없는 비율 (%)'), use_container_width=True)
 
st.markdown('<div class="sql-box">' + sql3 + '</div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-box">
💡 <b>핵심 발견 (χ²=40.9, p&lt;0.001)</b><br>
저소득 MZ의 <b>16.9%</b>는 음주도 없고 단체참여도 없습니다 — 고소득(4.3%)의 <b>약 4배.</b><br>
저소득 MZ 6명 중 1명은 한국 사회의 주요 교류 수단 <b>모두에서 배제</b>되어 있습니다.<br>
분석2의 결론 <b>"금주 트렌드가 저소득층에게는 고립으로 이어질 수 있음"</b>이 수치로 실증되었습니다.
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
 
# ── 차트 4 ──────────────────────────────────────────
st.header("4. 소득분위별 이중배제율 추이")
 
sql4 = """SELECT 소득코드, 소득레이블,
       ROUND(AVG(이중배제) * 100, 1) AS 이중배제율,
       COUNT(*) AS n
FROM mz_isolation
WHERE 소득코드 <= 7
GROUP BY 소득코드
ORDER BY 소득코드"""
 
df4 = run_query(sql4)
 
fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=df4['소득레이블'], y=df4['이중배제율'],
    mode='lines+markers+text',
    line=dict(color='#e63946', width=3),
    marker=dict(size=10, color='#e63946', line=dict(color='white', width=2)),
    text=[f"{v}%" for v in df4['이중배제율']],
    textposition='top center',
    textfont=dict(size=12)
))
fig4.update_layout(
    title=dict(text='소득이 낮아질수록 심화되는 이중배제', font=dict(size=13, color='#1a1a2e')),
    yaxis=dict(title='이중배제율 (%)', showgrid=True, gridcolor='#eee', range=[0, df4['이중배제율'].max()*1.3]),
    xaxis=dict(title='소득 구간', showgrid=False),
    plot_bgcolor='white', paper_bgcolor='white',
    height=360, margin=dict(t=40, b=40, l=40, r=20)
)
st.plotly_chart(fig4, use_container_width=True)
 
st.markdown('<div class="sql-box">' + sql4 + '</div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-box">
💡 <b>인사이트</b><br>
소득이 낮아질수록 이중배제율이 상승하는 패턴이 뚜렷합니다.
소득없음 구간(19.4%)에서 가장 높고, 소득이 오를수록 감소합니다.
<b>경제적 빈곤이 사회적 관계의 빈곤으로 이어지는 구조</b>가 데이터로 확인됩니다.
</div>
""", unsafe_allow_html=True)
 
st.markdown("---")
st.markdown("""
<div class="limit-box">
⚠️ <b>분석 한계</b> &nbsp;|&nbsp;
본 분석은 횡단면 데이터로 인과관계가 아닌 <b>동반 패턴</b>을 확인한 결과입니다.
이중배제의 원인이 저소득인지, 학력·고용상태 등 다른 요인의 영향인지는 추가 분석이 필요합니다.
데이터는 한국인의 행복조사 2023 (KOSSDA) 기준이며, MZ세대(19~39세) n=4,626명 표본입니다.
</div>
""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Developed with Python + Streamlit + SQLite | 한국인의 행복조사 2023 (KOSSDA)")
