"""数据分析模块。

提供与 UI 无关的纯数据分析计算函数,包括:
- 相关性矩阵计算
- 数值特征分布统计
- 类别特征与目标变量的关联分析
"""

import numpy as np
import pandas as pd

from src.data_loader import TARGET_COL, get_categorical_cols, get_numeric_cols


def compute_correlation_matrix(
    df: pd.DataFrame, method: str = "pearson"
) -> pd.DataFrame:
    """计算数值型特征之间的相关性矩阵。

    Args:
        df: 包含数值列的数据。
        method: 相关性方法 ('pearson', 'spearman', 'kendall')。

    Returns:
        数值型列的相关性矩阵。
    """
    num_cols = get_numeric_cols(df)
    if not num_cols:
        return pd.DataFrame()
    return df[num_cols].corr(method=method, numeric_only=True)


def get_top_correlated_features(df: pd.DataFrame, top_n: int = 10) -> list[dict]:
    """找出与目标变量相关性最强的特征。

    将 subscribe 编码为 0/1 后,计算各数值特征与它的相关系数,
    按绝对值降序排列,返回 top_n。

    Args:
        df: 含目标列的训练数据。
        top_n: 返回前 N 个特征。

    Returns:
        列表每项含 feature, correlation, abs_correlation。
    """
    if TARGET_COL not in df.columns:
        return []
    df_copy = df.copy()
    df_copy["_target_num"] = (df_copy[TARGET_COL] == "yes").astype(int)
    num_cols = get_numeric_cols(df_copy)
    correlations = []
    for col in num_cols:
        if col == TARGET_COL or col == "_target_num":
            continue
        corr = df_copy[col].corr(df_copy["_target_num"])
        if not np.isnan(corr):
            correlations.append(
                {
                    "feature": col,
                    "correlation": round(float(corr), 4),
                    "abs_correlation": round(abs(float(corr)), 4),
                }
            )
    correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)
    return correlations[:top_n]


def compute_categorical_subscribe_rate(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """计算某类别特征各取值对应的认购率。

    Args:
        df: 含目标列的数据。
        col: 类别列名。

    Returns:
        含 value, total, yes_count, yes_rate 的 DataFrame。
    """
    if col not in df.columns or TARGET_COL not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby(col, observed=False)[TARGET_COL].agg(
        total="count",
        yes_count=lambda x: (x == "yes").sum(),
    )
    grouped["yes_rate"] = (grouped["yes_count"] / grouped["total"]).round(4)
    grouped["no_count"] = grouped["total"] - grouped["yes_count"]
    return grouped.reset_index()


def get_feature_importance_summary(df: pd.DataFrame) -> dict:
    """汇总各特征类型和基本信息,供 UI 展示。

    Returns:
        dict: 含 numeric_features, categorical_features,
              total_features, target_col 等字段。
    """
    num_cols = [c for c in get_numeric_cols(df) if c not in ("id", TARGET_COL)]
    cat_cols = [c for c in get_categorical_cols(df) if c != TARGET_COL]
    return {
        "numeric_count": len(num_cols),
        "numeric_features": num_cols,
        "categorical_count": len(cat_cols),
        "categorical_features": cat_cols,
        "total_features": len(num_cols) + len(cat_cols),
        "target_col": TARGET_COL if TARGET_COL in df.columns else None,
    }
