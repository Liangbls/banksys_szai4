"""测试 analysis 模块。"""

import pandas as pd
import pytest

from src.analysis import (
    compute_categorical_subscribe_rate,
    compute_correlation_matrix,
    get_feature_importance_summary,
    get_top_correlated_features,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """创建含目标列和混合特征类型的测试数据。"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6],
            "age": [30, 45, 25, 50, 35, 40],
            "duration": [100, 200, 150, 300, 250, 180],
            "campaign": [1, 2, 1, 3, 2, 1],
            "job": [
                "admin.",
                "blue-collar",
                "admin.",
                "technician",
                "blue-collar",
                "technician",
            ],
            "marital": [
                "married",
                "single",
                "married",
                "divorced",
                "single",
                "married",
            ],
            "subscribe": ["no", "yes", "no", "yes", "no", "yes"],
        }
    )


@pytest.fixture
def df_no_target() -> pd.DataFrame:
    """不含目标列的测试数据。"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "age": [30, 45, 25],
            "duration": [100, 200, 150],
            "job": ["admin.", "blue-collar", "admin."],
        }
    )


# ── 相关性矩阵 ──────────────────────────────────────────────────


def test_compute_correlation_matrix(sample_df):
    corr = compute_correlation_matrix(sample_df)
    assert isinstance(corr, pd.DataFrame)
    assert "age" in corr.columns
    assert "duration" in corr.columns
    # 对角线应为 1.0
    assert abs(corr.loc["age", "age"] - 1.0) < 1e-9


def test_compute_correlation_matrix_spearman(sample_df):
    corr = compute_correlation_matrix(sample_df, method="spearman")
    assert isinstance(corr, pd.DataFrame)
    assert "age" in corr.columns


def test_compute_correlation_matrix_no_numeric(df_no_target):
    """仅有少量数值列也应该能计算。"""
    corr = compute_correlation_matrix(df_no_target)
    assert isinstance(corr, pd.DataFrame)
    assert "age" in corr.columns


# ── Top 相关特征 ────────────────────────────────────────────────


def test_get_top_correlated_features(sample_df):
    result = get_top_correlated_features(sample_df, top_n=3)
    assert isinstance(result, list)
    assert len(result) <= 3
    assert all("feature" in item for item in result)
    assert all("correlation" in item for item in result)
    assert all("abs_correlation" in item for item in result)


def test_get_top_correlated_features_sorted(sample_df):
    result = get_top_correlated_features(sample_df, top_n=10)
    if len(result) >= 2:
        for i in range(len(result) - 1):
            assert result[i]["abs_correlation"] >= result[i + 1]["abs_correlation"]


def test_get_top_correlated_features_no_target(df_no_target):
    result = get_top_correlated_features(df_no_target)
    assert result == []


# ── 类别认购率 ──────────────────────────────────────────────────


def test_compute_categorical_subscribe_rate(sample_df):
    rate_df = compute_categorical_subscribe_rate(sample_df, "job")
    assert isinstance(rate_df, pd.DataFrame)
    assert "job" in rate_df.columns
    assert "total" in rate_df.columns
    assert "yes_rate" in rate_df.columns
    assert len(rate_df) == 3  # admin, blue-collar, technician


def test_compute_categorical_subscribe_rate_no_target(df_no_target):
    rate_df = compute_categorical_subscribe_rate(df_no_target, "job")
    assert rate_df.empty


def test_compute_categorical_subscribe_rate_invalid_col(sample_df):
    rate_df = compute_categorical_subscribe_rate(sample_df, "ghost")
    assert rate_df.empty


# ── 特征概览 ────────────────────────────────────────────────────


def test_get_feature_importance_summary(sample_df):
    summary = get_feature_importance_summary(sample_df)
    assert summary["target_col"] == "subscribe"
    assert summary["numeric_count"] >= 2
    assert summary["categorical_count"] >= 1
    assert summary["total_features"] >= 3


def test_get_feature_importance_summary_no_target(df_no_target):
    summary = get_feature_importance_summary(df_no_target)
    assert summary["target_col"] is None
