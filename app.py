import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title='분석3: 저소득층 고립 분석', layout='wide')

# 2. 데이터베이스 연결 확인
DB_PATH = 'isolation2023.db'

if not os.path.exists(DB_PATH):
    st.error('🚨 데이터베이스 파일(isolation2023.db)을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.')
    st.stop()

def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

# 3. 페이지 제목
st.title('분석3: 저소득층에게 음주의 자리를 대체한 것은 무엇인가?')

# 4. 분석 배경 섹션 (2컬럼)
st.markdown('### 💡 분석 배경')
col_bg1, col_bg2 = st.columns(2)
with col_bg1:
    st.info('**분석2의 한계**  \n기존 분석에서는 소득과 음주 빈도의 단순 상관관계만 확인하여, 음주를 하지 않는 저소득층이 처한 사회적 고립 상태를 구체적으로 포착하지 못함.')
with col_bg2:
    st.success('**분석3의 역할**  \n음주도 하지 않고 단체 활동도 참여하지 않는 \'이중배제\' 상태를 정의하여, 저소득층이 처한 실질적인 사회적 고립의 깊이를 실증적으로 분석함.')

st.divider()

# 5. 핵심 KPI 카드
st.markdown('### 📊 주요 지표 (Key Metrics)')
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric('저소득 이중배제율', '16.9%')
kpi2.metric('고소득 이중배제율', '4.3%')
kpi3.metric('격차', '약 4배')
kpi4.metric('통계적 유의성', 'p < 0.001', 'χ²=40.9')

st.divider()

# 6. 차트1: 소득그룹별 이중배제율 비교
st.subheader('차트1. 소득그룹별 이중배제율 비교')

sql1 = '''
SELECT 
    소득그룹, 
    AVG(이중배제) * 100 as 이중배제율 
FROM mz_isolation 
GROUP BY 소득그룹
'''
df1 = run_query(sql1)

# 순서 정렬 (저소득 -> 중간 -> 고소득)
df1['소득그룹'] = pd.Categorical(df1['소득그룹'], categories=['저소득', '중간', '고소득'], ordered=True)
df1 = df1.sort_values('소득그룹')

fig1 = px.bar(
    df1, x='소득그룹', y='이중배제율',
    color='소득그룹',
    color_discrete_map={'저소득': '#636EFA', '중간': '#EF553B', '고소득': '#00CC96'},
    text_auto='.1f',
    title='소득그룹별 이중배제(음주X, 단체참여X) 비율 (%)'
)
st.plotly_chart(fig1, use_container_width=True)

st.code(sql1, language='sql')
st.markdown('- 저소득층의 이중배제율은 16.9%로 고소득층(4.3%)에 비해 약 4배나 높게 나타납니다.')
st.markdown('- 이는 저소득층이 단순히 술을 안 마시는 것이 아니라, 사회적 관계망에서도 심각하게 소외되어 있음을 시사합니다.')

st.divider()

# 7. 차트2: 소득분위별 이중배제율 추이
st.subheader('차트2. 소득분위별 이중배제율 추이')

sql2 = '''
SELECT 
    소득코드, 
    AVG(이중배제) * 100 as 이중배제율 
FROM mz_isolation 
GROUP BY 소득코드
ORDER BY 소득코드
'''
df2 = run_query(sql2)

fig2 = px.line(
    df2, x='소득코드', y='이중배제율',
    markers=True,
    title='소득코드(1-7)별 이중배제율 변화 추이 (%)'
)
fig2.update_traces(line_color='#636EFA')
st.plotly_chart(fig2, use_container_width=True)

st.code(sql2, language='sql')
st.markdown('- 소득이 낮아질수록(소득코드 1에 가까울수록) 이중배제율이 급격히 상승하는 계단식 고립 패턴이 확인됩니다.')
st.markdown('- 단, 500-600만 원 구간인 소득코드 5의 경우 표본 수가 57명으로 상대적으로 적어 수치가 일시적으로 튀는 불안정성을 보일 수 있음에 유의해야 합니다.')

st.divider()

# 8. 분석3 요약 섹션
st.markdown('### 📝 분석3 요약')
st.markdown('1. 저소득층의 고립 특성: 저소득층은 비음주 상태일 때 건전한 사회적 참여로 연결되는 것이 아니라, 아예 사회적 관계가 단절되는 고립 상태로 빠질 확률이 매우 높음.')
st.markdown('2. 경제적 불평등의 전이: 경제적 자산의 부족이 사회적 자본(인적 네트워크)의 빈곤으로 직결되는 현상을 데이터로 증명함.')
st.markdown('3. 결론: 저소득층의 고립 해소를 위해서는 단순한 경제적 지원을 넘어, 음주를 대체할 수 있는 지역사회 기반의 커뮤니티 활성화 정책이 절실함.')
st.markdown('4. 한계: 본 분석에 사용된 데이터 중 특정 소득 구간(500-600만 원)의 표본 수가 적어 해당 구간의 해석에는 주의가 필요하며, 향후 보충 조사가 요구됨.')
