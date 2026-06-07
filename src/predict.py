"""在线预测模块 (US-4).

提供模型加载与单条样本推理功能。
预测时从 models/model.pkl 加载已训练模型,接受特征 dict,
返回预测类别与概率。
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# 模型预测所需的全部特征列(不含 id 和 subscribe)
FEATURE_COLS = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

CATEGORICAL_FEATURES = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

DEFAULT_MODEL_PATH = "models/model.pkl"


class ModelLoadError(Exception):
    """模型加载失败异常。"""

    pass


class PredictionError(Exception):
    """预测过程异常。"""

    pass


def _resolve_model_path(model_path: Optional[str] = None) -> Path:
    """解析模型文件路径。"""
    if model_path:
        return Path(model_path)
    return Path(__file__).resolve().parent.parent / DEFAULT_MODEL_PATH


def load_model(model_path: Optional[str] = None) -> dict:
    """加载已训练的模型与预处理器。

    Args:
        model_path: 模型文件路径,为 None 时使用默认路径。

    Returns:
        dict: 含 model 和 preprocessor 键。

    Raises:
        ModelLoadError: 模型文件不存在或加载失败。
    """
    import joblib

    path = _resolve_model_path(model_path)
    if not path.exists():
        raise ModelLoadError(
            f"模型文件不存在: {path}。请先运行 src/model_train.py 训练模型。"
        )
    try:
        pipeline = joblib.load(path)
        if "model" not in pipeline or "preprocessor" not in pipeline:
            raise ModelLoadError("模型文件格式无效,缺少 model 或 preprocessor。")
        logger.info("模型加载成功: %s", path)
        return pipeline
    except Exception as e:
        raise ModelLoadError(f"模型加载失败: {e}") from e


def predict(features: dict, pipeline: dict) -> dict:
    """对单条样本进行预测。

    Args:
        features: 特征 dict,键为列名,值为特征值。
        pipeline: load_model 返回的 dict,含 model 和 preprocessor。

    Returns:
        dict: 含 prediction ("yes"/"no"), probability (float, 0~1),
              input_features (原始输入)。

    Raises:
        PredictionError: 特征格式不符或推理失败。
    """
    try:
        # 构建单行 DataFrame,缺失列用默认值填充
        row = dict(features)
        for col in FEATURE_COLS:
            if col not in row:
                # 类别列默认 'unknown',数值列默认 0
                if col in CATEGORICAL_FEATURES:
                    row[col] = "unknown"
                else:
                    row[col] = 0

        df = pd.DataFrame([row])
        feature_order = [c for c in FEATURE_COLS if c in df.columns]
        df = df[feature_order]

        # 类型转换: 数值列
        num_cols = df.select_dtypes(
            include=["int64", "float64", "int", "float"]
        ).columns
        df[num_cols] = df[num_cols].astype(float)

    except Exception as e:
        raise PredictionError(f"特征处理失败: {e}") from e

    try:
        preprocessor = pipeline["preprocessor"]
        model = pipeline["model"]

        X = preprocessor.transform(df)
        prob = float(model.predict_proba(X)[0, 1])
        pred_label = "yes" if prob >= 0.5 else "no"

        return {
            "prediction": pred_label,
            "probability": round(prob, 4),
            "input_features": features,
        }
    except Exception as e:
        raise PredictionError(f"模型推理失败: {e}") from e


def get_default_features() -> dict:
    """返回各特征的合理默认值,供预测页面初始化使用。

    Returns:
        按 FEATURE_COLS 顺序的特征默认值 dict。
    """
    return {
        "age": 40,
        "job": "admin.",
        "marital": "married",
        "education": "high.school",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "duration": 500,
        "campaign": 1,
        "pdays": 999,
        "previous": 0,
        "poutcome": "nonexistent",
        "emp_var_rate": -1.8,
        "cons_price_index": 93.0,
        "cons_conf_index": -40.0,
        "lending_rate3m": 3.0,
        "nr_employed": 5000.0,
    }
