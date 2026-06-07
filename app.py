"""banksys_szai4 · 银行营销数据分析与预测系统。

Streamlit 主入口 —— 提供项目首页与多页面导航。
通过 `pages/` 目录自动发现子页面。
"""

import streamlit as st

st.set_page_config(
    page_title="银行营销数据分析与预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 侧边栏 ──────────────────────────────────────────────────────

with st.sidebar:
    st.title("🏦 银行营销系统")
    st.markdown("---")
    st.markdown("### 📍 导航")
    st.markdown("- **🏠 首页** (当前)")
    st.markdown("- 📊 数据分析")
    st.markdown("- 🔮 在线预测")
    st.markdown("---")
    st.caption("banksys_szai4 v0.1.0")

# ── 主页内容 ────────────────────────────────────────────────────

st.title("🏦 银行营销数据分析与预测系统")
st.markdown("### *Bank Marketing Analysis & Prediction System*")
st.markdown("---")

# 两栏布局
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 数据分析")
    st.markdown(
        """
        探索银行营销历史数据,直观了解客户特征分布与认购规律:
        - 数据总览与质量检查
        - 特征分布可视化
        - 目标变量分析
        - 特征相关性探索
        """
    )
    st.page_link(
        "pages/1_📊_data_analysis.py",
        label="→ 进入数据分析",
        icon="📊",
    )

with col2:
    st.markdown("### 🔮 在线预测")
    st.markdown(
        """
        基于训练好的机器学习模型,实时预测客户认购意向:
        - 点选式表单输入客户特征
        - 实时预测认购概率
        - 历史预测记录查看
        """
    )
    st.page_link(
        "pages/2_🔮_prediction.py",
        label="→ 进入在线预测",
        icon="🔮",
    )

st.markdown("---")

# 底部信息
st.markdown("### 📋 项目信息")

info_col1, info_col2, info_col3 = st.columns(3)
with info_col1:
    st.metric("训练数据样本", "22,500 条")
with info_col2:
    st.metric("特征数量", "20 个")
with info_col3:
    st.metric("预测目标", "认购 (Yes/No)")

st.markdown("---")
st.caption(
    "数据来源: UCI Bank Marketing Dataset 变体 · "
    "技术栈: Python 3.11 + Streamlit + scikit-learn + Docker"
)
