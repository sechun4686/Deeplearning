import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="가상 사용자 리서치 대시보드", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("dummy_data.csv")

df = load_data()

# 사이드바 필터
st.sidebar.title("필터")
gender_filter = st.sidebar.multiselect("성별", df['gender'].unique(), default=df['gender'].unique())
region_filter = st.sidebar.multiselect("지역", df['region'].unique(), default=df['region'].unique())
age_min, age_max = st.sidebar.slider("나이 범위", 19, 99, (19, 99))

filtered_df = df[
    (df['gender'].isin(gender_filter)) &
    (df['region'].isin(region_filter)) &
    (df['age'] >= age_min) &
    (df['age'] <= age_max)
]

# 타이틀
st.title("가상 사용자 리서치 대시보드")
st.caption(f"총 {len(filtered_df)}명 페르소나 분석 결과")

# 지표 카드
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 페르소나 수", len(filtered_df))
col2.metric("군집 수", filtered_df['cluster'].nunique())
col3.metric("평균 나이", f"{filtered_df['age'].mean():.1f}세")
col4.metric("지역 수", filtered_df['region'].nunique())

st.divider()

# 차트 1: 군집별 분포 (바 차트)
col1, col2 = st.columns(2)

with col1:
    st.subheader("군집별 페르소나 수")
    cluster_counts = filtered_df.groupby(['cluster', 'cluster_summary']).size().reset_index(name='count')
    fig1 = px.bar(
        cluster_counts, x='cluster_summary', y='count',
        color='cluster_summary',
        labels={'cluster_summary': '군집', 'count': '페르소나 수'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_layout(showlegend=False, xaxis_tickangle=-20)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("성별 분포")
    gender_counts = filtered_df['gender'].value_counts().reset_index()
    fig2 = px.pie(
        gender_counts, values='count', names='gender',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig2, use_container_width=True)

# 차트 2: 히트맵 (지역 x 군집)
st.subheader("지역 × 군집 히트맵")
heatmap_data = filtered_df.groupby(['region', 'cluster_summary']).size().unstack(fill_value=0)
fig3 = px.imshow(
    heatmap_data,
    labels=dict(x="군집", y="지역", color="페르소나 수"),
    color_continuous_scale="Blues",
    text_auto=True
)
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# 차트 3: 나이대 분포
st.subheader("나이대별 분포")
filtered_df['age_group'] = pd.cut(
    filtered_df['age'],
    bins=[19, 29, 39, 49, 99],
    labels=['20대', '30대', '40대', '50대+']
)
age_cluster = filtered_df.groupby(['age_group', 'cluster_summary']).size().reset_index(name='count')
fig4 = px.bar(
    age_cluster, x='age_group', y='count',
    color='cluster_summary',
    barmode='group',
    labels={'age_group': '나이대', 'count': '페르소나 수', 'cluster_summary': '군집'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig4, use_container_width=True)

# 원본 데이터 테이블
st.subheader("페르소나 응답 데이터")
st.dataframe(filtered_df[['persona_id', 'age', 'gender', 'region', 'cluster_summary', 'response']], use_container_width=True)

st.divider()

# Export
st.subheader("📥 Export")
col1, col2 = st.columns(2)

with col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("CSV 다운로드", csv, "results.csv", "text/csv")

with col2:
    html_str = fig3.to_html(include_plotlyjs='cdn')
    st.download_button("히트맵 HTML 다운로드", html_str, "heatmap.html", "text/html")