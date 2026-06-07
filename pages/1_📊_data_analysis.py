"""数据分析交互页面 (US-2).

提供银行营销数据的探索性分析功能:
- 数据总览
- 目标变量分布
- 数值特征分析
- 类别特征分析
- 相关性分析
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# 确保 src/ 在导入路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis import (  # noqa: E402
    compute_categorical_subscribe_rate,
    compute_correlation_matrix,
    get_feature_importance_summary,
    get_top_correlated_features,
)
from src.data_loader import (  # noqa: E402
    get_categorical_cols,
    get_data_summary,
    get_numeric_cols,
    get_numeric_stats,
    get_target_distribution,
    load_train,
)

st.set_page_config(page_title="数据分析", page_icon="📊", layout="wide")

st.title("📊 数据分析")
st.markdown("探索银行营销数据,了解客户特征与认购规律。")
st.markdown("---")

# ── 数据加载 ────────────────────────────────────────────────────


@st.cache_data
def load_data() -> pd.DataFrame | None:
    """缓存加载训练数据。"""
    try:
        return load_train()
    except FileNotFoundError:
        return None


df = load_data()

if df is None:
    st.warning("⚠️ 数据文件未找到。请将 `train.csv` 放入 `data/` 目录后刷新页面。")
    st.stop()

# ── 侧边栏:分析选项 ──────────────────────────────────────────────

with st.sidebar:
    st.header("🔍 分析选项")
    analysis_section = st.radio(
        "选择分析类型",
        [
            "📋 数据总览",
            "🎯 目标变量分布",
            "📈 数值特征分析",
            "📊 类别特征分析",
            "🔗 相关性分析",
        ],
    )

# ── 数据总览 ─────────────────────────────────────────────────────

if analysis_section == "📋 数据总览":
    st.subheader("数据总览")

    summary = get_data_summary(df)
    feature_info = get_feature_importance_summary(df)

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("总样本数", f"{summary['shape'][0]:,}")
    with col_b:
        st.metric("总列数", summary["shape"][1])
    with col_c:
        st.metric("数值特征", feature_info["numeric_count"])
    with col_d:
        st.metric("类别特征", feature_info["categorical_count"])

    st.markdown("---")

    # 各列信息
    st.markdown("#### 列信息")
    col_info = pd.DataFrame(
        {
            "列名": summary["columns"],
            "数据类型": [summary["dtypes"][c] for c in summary["columns"]],
            "缺失数": [summary["missing"][c] for c in summary["columns"]],
        }
    )
    st.dataframe(col_info, use_container_width=True, hide_index=True)

    if summary["missing_total"] > 0:
        st.warning(f"⚠️ 共存在 {summary['missing_total']} 个缺失值")
    else:
        st.success("✅ 数据完整,无缺失值")

    # 数据预览
    st.markdown("#### 数据预览(前 20 行)")
    st.dataframe(df.head(20), use_container_width=True)

# ── 目标变量分布 ────────────────────────────────────────────────

elif analysis_section == "🎯 目标变量分布":
    st.subheader("目标变量分布: subscribe (认购)")

    dist = get_target_distribution(df)
    counts = dist["counts"]
    proportions = dist["proportions"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 计数")
        fig_bar = px.bar(
            x=list(counts.keys()),
            y=list(counts.values()),
            labels={"x": "认购", "y": "样本数"},
            color=list(counts.keys()),
            color_discrete_map={"yes": "#2ecc71", "no": "#95a5a6"},
            text_auto=True,
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("#### 比例")
        fig_pie = px.pie(
            names=list(proportions.keys()),
            values=list(proportions.values()),
            color=list(proportions.keys()),
            color_discrete_map={"yes": "#2ecc71", "no": "#95a5a6"},
            hole=0.4,
        )
        fig_pie.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_pie, use_container_width=True)

# ── 数值特征分析 ─────────────────────────────────────────────────

elif analysis_section == "📈 数值特征分析":
    st.subheader("数值特征分析")

    num_cols = [c for c in get_numeric_cols(df) if c not in ("id", "subscribe")]
    selected_num = st.selectbox("选择数值特征", num_cols)

    if selected_num:
        stats = get_numeric_stats(df, selected_num)

        # 描述性统计表
        st.markdown("#### 描述性统计")
        stats_df = pd.DataFrame(
            {
                "统计量": list(stats.keys()),
                "值": [
                    round(v, 2) if isinstance(v, float) else v for v in stats.values()
                ],
            }
        )
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        # 直方图 + 箱线图
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 直方图")
            fig_hist = px.histogram(
                df,
                x=selected_num,
                nbins=40,
                color_discrete_sequence=["#3498db"],
                marginal="rug",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_b:
            st.markdown("#### 箱线图(按认购分组)")
            fig_box = px.box(
                df,
                y=selected_num,
                x="subscribe",
                color="subscribe",
                color_discrete_map={"yes": "#2ecc71", "no": "#95a5a6"},
            )
            st.plotly_chart(fig_box, use_container_width=True)

# ── 类别特征分析 ─────────────────────────────────────────────────

elif analysis_section == "📊 类别特征分析":
    st.subheader("类别特征分析")

    cat_cols = get_categorical_cols(df)
    selected_cat = st.selectbox("选择类别特征", cat_cols)

    if selected_cat:
        rate_df = compute_categorical_subscribe_rate(df, selected_cat)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 频次分布")
            counts = df[selected_cat].value_counts().reset_index()
            counts.columns = [selected_cat, "count"]
            fig_bar = px.bar(
                counts,
                x=selected_cat,
                y="count",
                text_auto=True,
                color_discrete_sequence=["#3498db"],
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_b:
            if not rate_df.empty:
                st.markdown("#### 认购率(Yes 占比)")
                fig_rate = px.bar(
                    rate_df,
                    x=selected_cat,
                    y="yes_rate",
                    text_auto=".1%",
                    color_discrete_sequence=["#2ecc71"],
                )
                fig_rate.update_layout(yaxis_tickformat=".0%")
                st.plotly_chart(fig_rate, use_container_width=True)

        # 详细表
        if not rate_df.empty:
            st.markdown("#### 交叉分组详情")
            display_df = rate_df.rename(
                columns={
                    selected_cat: "类别",
                    "total": "总数",
                    "yes_count": "认购数",
                    "no_count": "未认购数",
                    "yes_rate": "认购率",
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── 相关性分析 ───────────────────────────────────────────────────

elif analysis_section == "🔗 相关性分析":
    st.subheader("相关性分析")

    # 与目标变量的相关性排名
    st.markdown("#### 特征与认购(subscribe)的相关性排名")
    top_feats = get_top_correlated_features(df, top_n=15)
    if top_feats:
        top_df = pd.DataFrame(top_feats)
        fig_top = px.bar(
            top_df,
            x="correlation",
            y="feature",
            orientation="h",
            color="correlation",
            color_continuous_scale="RdBu",
            text="correlation",
        )
        fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # 数值特征相关性矩阵热力图
    st.markdown("#### 数值特征相关性矩阵")
    corr_matrix = compute_correlation_matrix(df, method="pearson")
    if not corr_matrix.empty:
        fig_heat = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # 两特征散点图
    st.markdown("---")
    st.markdown("#### 两特征散点图")
    num_cols = [c for c in get_numeric_cols(df) if c not in ("id", "subscribe")]
    if len(num_cols) >= 2:
        col_x, col_y = st.columns(2)
        with col_x:
            x_col = st.selectbox("X 轴", num_cols, index=0)
        with col_y:
            y_col = st.selectbox("Y 轴", num_cols, index=min(1, len(num_cols) - 1))
        fig_scatter = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color="subscribe",
            color_discrete_map={"yes": "#2ecc71", "no": "#95a5a6"},
            opacity=0.6,
            marginal_x="histogram",
            marginal_y="histogram",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
