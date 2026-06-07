"""数据加载与预处理模块。

支持从 CSV 文件加载银行营销数据,提供数据概览、特征分类等函数。
数据路径优先从环境变量 `DATA_DIR` 读取,未设置时回退到默认路径。
"""

import os
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


# 目标变量列名
TARGET_COL = "subscribe"

# 已知类别型特征(模型训练时需编码)
CATEGORICAL_COLS = [
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


def _resolve_data_dir() -> Path:
    """解析数据目录路径。"""
    env_dir = os.environ.get("DATA_DIR")
    if env_dir:
        return Path(env_dir)
    # 默认回退:项目根下的 data/
    return Path(__file__).resolve().parent.parent / "data"


def load_train(data_dir: Optional[str] = None) -> pd.DataFrame:
    """加载训练数据 (train.csv)。

    Args:
        data_dir: 数据目录路径,为 None 时从环境变量或默认路径读取。

    Returns:
        包含 22 列的 DataFrame,含目标列 `subscribe`。

    Raises:
        FileNotFoundError: 当 train.csv 不存在时。
    """
    data_path = (Path(data_dir) if data_dir else _resolve_data_dir()) / "train.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"训练数据文件不存在: {data_path}")
    df = pd.read_csv(data_path)
    # 将已知类别列转为 category dtype
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def load_test(data_dir: Optional[str] = None) -> pd.DataFrame:
    """加载测试数据 (test.csv,无目标列)。

    Args:
        data_dir: 数据目录路径,为 None 时从环境变量或默认路径读取。

    Returns:
        包含 21 列的 DataFrame,不含目标列 `subscribe`。
    """
    data_path = (Path(data_dir) if data_dir else _resolve_data_dir()) / "test.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {data_path}")
    df = pd.read_csv(data_path)
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")
    return df


def get_numeric_cols(df: pd.DataFrame) -> list[str]:
    """返回 DataFrame 中所有数值型列名。"""
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()


def get_categorical_cols(df: pd.DataFrame) -> list[str]:
    """返回 DataFrame 中所有类别型列名(含 category dtype 和 object)。"""
    return df.select_dtypes(include=["category", "object", "string"]).columns.tolist()


def get_data_summary(df: pd.DataFrame) -> dict:
    """获取数据总览信息。

    Returns:
        dict: 含 shape, dtypes, missing 等字段。
    """
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
        "missing_total": int(df.isnull().sum().sum()),
    }


def get_target_distribution(df: pd.DataFrame) -> dict:
    """获取目标变量 subscribe 的分布。

    Returns:
        dict: 含 counts(各类计数) 和 proportions(各类比例)。
    """
    if TARGET_COL not in df.columns:
        return {"counts": {}, "proportions": {}}
    value_counts = df[TARGET_COL].value_counts()
    return {
        "counts": value_counts.to_dict(),
        "proportions": (value_counts / value_counts.sum()).round(4).to_dict(),
    }


def get_numeric_stats(df: pd.DataFrame, col: str) -> dict:
    """获取单个数值列的描述性统计。

    Returns:
        dict: count, mean, std, min, 25%, 50%, 75%, max。
    """
    if col not in df.columns:
        raise ValueError(f"列 '{col}' 不存在")
    stats = df[col].describe()
    return stats.to_dict()


def get_categorical_counts(
    df: pd.DataFrame, col: str
) -> Tuple[pd.Series, pd.DataFrame]:
    """获取类别列频次及与 target 的交叉分组。

    Returns:
        (频次 Series, 交叉表 DataFrame)。
    """
    if col not in df.columns:
        raise ValueError(f"列 '{col}' 不存在")
    value_counts = df[col].value_counts()
    crosstab = pd.DataFrame()
    if TARGET_COL in df.columns:
        crosstab = pd.crosstab(df[col], df[TARGET_COL], normalize="index").round(4)
    return value_counts, crosstab
