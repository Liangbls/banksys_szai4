"""在线预测页面 (US-4).

提供点选式表单输入客户特征,实时预测认购意向。
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# 确保 src/ 在导入路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.predict import (  # noqa: E402
    CATEGORICAL_FEATURES,
    FEATURE_COLS,
    ModelLoadError,
    PredictionError,
    get_default_features,
    load_model,
    predict,
)

st.set_page_config(page_title="在线预测", page_icon="🔮", layout="wide")

st.title("🔮 在线认购预测")
st.markdown("填写客户特征信息,预测是否会认购定期存款。")
st.markdown("---")

# ── 模型加载 ────────────────────────────────────────────────────


@st.cache_resource
def get_pipeline() -> Optional[dict]:
    """缓存加载模型(全局单例)。"""
    try:
        return load_model()
    except ModelLoadError as e:
        st.session_state["_model_error"] = str(e)
        return None


pipeline = get_pipeline()

if pipeline is None:
    error_msg = st.session_state.get("_model_error", "模型加载失败")
    st.warning(
        f"⚠️ {error_msg}\n\n"
        "请先运行以下命令训练模型:\n\n"
        "```bash\n"
        "python src/model_train.py --data-path data --model-dir models\n"
        "```"
    )
    st.stop()

# ── 历史记录初始化 ──────────────────────────────────────────────

if "prediction_history" not in st.session_state:
    st.session_state["prediction_history"] = []

# ── 表单:特征输入 ───────────────────────────────────────────────

# 分类特征的可选值(从真实数据中提取)
CATEGORY_OPTIONS = {
    "job": [
        "admin.",
        "blue-collar",
        "technician",
        "services",
        "management",
        "retired",
        "entrepreneur",
        "self-employed",
        "housemaid",
        "student",
        "unemployed",
    ],
    "marital": ["married", "single", "divorced"],
    "education": [
        "high.school",
        "basic.9y",
        "professional.course",
        "university.degree",
        "basic.6y",
        "basic.4y",
    ],
    "default": ["no", "yes", "unknown"],
    "housing": ["yes", "no", "unknown"],
    "loan": ["no", "yes", "unknown"],
    "contact": ["cellular", "telephone"],
    "month": [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ],
    "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
    "poutcome": ["failure", "nonexistent", "success"],
}

defaults = get_default_features()

st.markdown("### 📝 客户特征")

# 使用多列布局提高利用率
features = {}

# ── 数值特征(3 列排列) ──
st.markdown("#### 数值特征")
num_features = [c for c in FEATURE_COLS if c not in CATEGORICAL_FEATURES]

for i in range(0, len(num_features), 3):
    cols = st.columns(3)
    for j, col_name in enumerate(num_features[i : i + 3]):
        with cols[j]:
            if col_name == "age":
                features[col_name] = st.slider("年龄", 18, 95, int(defaults[col_name]))
            elif col_name == "duration":
                features[col_name] = st.number_input(
                    "通话时长 (秒)", 0, 6000, int(defaults[col_name])
                )
            elif col_name == "campaign":
                features[col_name] = st.slider(
                    "本次营销联系次数", 0, 50, int(defaults[col_name])
                )
            elif col_name == "pdays":
                features[col_name] = st.number_input(
                    "距上次联系天数 (999=未联系)",
                    0,
                    999,
                    int(defaults[col_name]),
                )
            elif col_name == "previous":
                features[col_name] = st.slider(
                    "历史联系次数", 0, 10, int(defaults[col_name])
                )
            elif col_name == "emp_var_rate":
                features[col_name] = st.selectbox(
                    "就业变化率",
                    [-3.4, -2.9, -1.8, -0.1, 1.1, 1.4],
                    index=[-3.4, -2.9, -1.8, -0.1, 1.1, 1.4].index(defaults[col_name]),
                )
            elif col_name == "cons_price_index":
                features[col_name] = st.number_input(
                    "消费者价格指数",
                    85.0,
                    100.0,
                    float(defaults[col_name]),
                    step=0.1,
                )
            elif col_name == "cons_conf_index":
                features[col_name] = st.number_input(
                    "消费者信心指数",
                    -55.0,
                    -25.0,
                    float(defaults[col_name]),
                    step=0.1,
                )
            elif col_name == "lending_rate3m":
                features[col_name] = st.number_input(
                    "3月贷款利率",
                    0.0,
                    10.0,
                    float(defaults[col_name]),
                    step=0.01,
                )
            elif col_name == "nr_employed":
                features[col_name] = st.number_input(
                    "雇员数量",
                    4500.0,
                    5500.0,
                    float(defaults[col_name]),
                    step=1.0,
                )
            else:
                # 兜底: 通用 number_input
                features[col_name] = st.number_input(
                    col_name, value=float(defaults.get(col_name, 0))
                )

# ── 类别特征(3 列排列) ──
st.markdown("#### 类别特征")

for i in range(0, len(CATEGORICAL_FEATURES), 3):
    cols = st.columns(3)
    for j, col_name in enumerate(CATEGORICAL_FEATURES[i : i + 3]):
        with cols[j]:
            options = CATEGORY_OPTIONS.get(col_name, [])
            default_val = defaults.get(col_name, options[0] if options else "")
            if default_val not in options:
                default_val = options[0] if options else ""
            features[col_name] = st.selectbox(
                col_name,
                options,
                index=options.index(default_val),
            )

# ── 预测按钮 ─────────────────────────────────────────────────────

st.markdown("---")

col_btn, col_result = st.columns([1, 3])

with col_btn:
    predict_clicked = st.button("🔮 开始预测", type="primary", use_container_width=True)

if predict_clicked:
    try:
        result = predict(features, pipeline)

        # 记录历史
        history_entry = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "预测结果": "✅ 会认购" if result["prediction"] == "yes" else "❌ 不会认购",
            "认购概率": f"{result['probability']:.2%}",
            **{k: v for k, v in result["input_features"].items()},
        }
        st.session_state["prediction_history"].insert(0, history_entry)

        # 显示结果
        with col_result:
            if result["prediction"] == "yes":
                st.success(
                    f"### ✅ 预测: 会认购定期存款\n\n"
                    f"**认购概率: {result['probability']:.2%}**"
                )
            else:
                st.info(
                    f"### ❌ 预测: 不会认购定期存款\n\n"
                    f"**认购概率: {result['probability']:.2%}**"
                )

            # 概率进度条
            st.progress(result["probability"])

    except PredictionError as e:
        st.error(f"预测失败: {e}")

# ── 历史预测记录 ─────────────────────────────────────────────────

if st.session_state["prediction_history"]:
    st.markdown("---")
    st.markdown("### 📜 历史预测记录")
    history_df = pd.DataFrame(st.session_state["prediction_history"])

    # 只展示关键列
    display_cols = ["时间", "预测结果", "认购概率"]
    st.dataframe(
        history_df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    if st.button("🗑️ 清空历史记录"):
        st.session_state["prediction_history"] = []
        st.rerun()
