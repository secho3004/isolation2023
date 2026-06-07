import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정 및 데이터베이스 확인
st.set_page_config(page_title='분석3: 저소득층 고립 분석', layout='wide')

DB_PATH = 'isolation2023.db'

def get_connection():
    if not os.path.exists(DB_PATH):
        st.error('🚨 데이터베이스 파일(isolation2023.db)을 찾을 수 없습니다. 파일 경로를 확인해주세요.')
        return None
    return sqlite3.connect(DB_PATH)

# 색상 정의 (분석2와 동일)
color_map = {'저소득': '#636EFA', '중간': '#EF553B', '고소득': '#00CC96'}

# 2. 타이틀 및 분석 배경
st.title('분석3: 저소득층에게 음주의 자리를 대체한 것은 무엇인가?')

col_bg1, col_bg2 = st.columns(2)
with col_bg1:
    st.subheader('📍 분석2의 결론(한계)')
    st.markdown('''
    - 저소득층은 타 소득 계층에 비해 음주 빈도가 상대적으로 낮게 나타남
    - 하지만 이것이 건강한 생활을 의미하는지, 아니면 사회적 단절을 의미하는지 추가 확인 필요
    ''')
with col_bg2:
    st.subheader('🔍 분석3의 역할(실증)')
    st.markdown('''
    - 음주도 하지 않고 사회적 단체 참여도 없는 '이중배제' 상태를 분석
    - 소득이 낮아질수록 고립이 심화되는 '고립의 경제적 양극화' 현상을 데이터로 증명
    ''')

# 3. 핵심 KPI 카드
conn = get_connection()
if conn:
    st.divider()
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric('저소득 이중배제율', '16.9%')
    kpi2.metric('고소득 이중배제율', '4.3%')
    kpi3.metric('격차', '약 4배')
    kpi4.metric('통계적 유의성', 'p < 0.001', 'χ²=40.9')

    # --- 차트 1 섹션 ---
    st.divider()
    st.subheader('차트1. 소득그룹별 이중배제율 비교')
    
    query1 = '''
    SELECT 
        소득그룹, 
        AVG(이중배제) * 100 AS 이중배제율
    FROM mz_isolation
    GROUP BY 소득그룹
    ORDER BY CASE 소득그룹 WHEN '저소득' THEN 1 WHEN '중간' THEN 2 ELSE 3 END
    '''
    df1 = pd.read_sql(query1, conn)
    
    fig1 = px.bar(
        df1, 
        x='소득그룹', 
        y='이중배제율',
        color='소득그룹',
        color_discrete_map=color_map,
        text_auto='.1f',
        title='소득그룹별 이중배제(음주X, 단체X) 비율 (%)'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.code(query1, language='sql')
    st.markdown('''
    - 저소득층의 이중배제율은 16.9%로, 고소득층(4.3%)에 비해 약 4배나 높은 수치를 기록함
    - 음주라는 사교 활동조차 경제적 여력에 따라 박탈될 수 있으며, 이를 대체할 사회적 관계망(단체참여) 또한 부재함을 시사함
    ''')

    # --- 차트 2 섹션 ---
    st.divider()
    st.subheader('차트2. 소득분위별 이중배제율 추이')
    
    query2 = '''
    SELECT 
        소득코드, 
        AVG(이중배제) * 100 AS 이중배제율
    FROM mz_isolation
    GROUP BY 소득코드
    ORDER BY 소득코드
    '''
    df2 = pd.read_sql(query2, conn)
    
    fig2 = px.line(
        df2, 
        x='소득코드', 
        y='이중배제율',
        markers=True,
        title='소득분위(1~7)에 따른 이중배제율 변화 추이'
    )
    # 라인 색상 고정 (저소득층 강조를 위해 기본 색상 사용)
    fig2.update_traces(line_color='#636EFA')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.code(query2, language='sql')
    st.markdown('''
    - 소득코드가 1(최저소득)에서 7(최고소득)로 증가함에 따라 이중배제율이 급격히 감소하는 선형적 패턴이 관찰됨
    - 특히 소득코드 1~2 구간에서 고립율이 가파르게 상승하며, 빈곤이 고립의 직접적인 원인이 될 수 있음을 보여줌
    ''')

    # 4. 분석3 요약 섹션
    st.divider()
    st.subheader('📝 분석3 요약')
    st.markdown('''
    1. **핵심 발견**: 저소득층은 비음주 비율이 높지만, 그것이 단체 참여로 이어지지 못하고 '사회적 고립'으로 귀결됨
    2. **결론**: 경제적 취약성은 단순히 소비의 위축을 넘어 사교와 연대라는 인간의 기본적 활동 영역까지 위협함
    3. **한계**: 본 데이터는 2023년 단년도 조사로, 소득 감소가 고립을 부르는지 혹은 고립이 경제활동 저해를 부르는지의 인과관계는 추가 연구가 필요함
    ''')

    conn.close()
