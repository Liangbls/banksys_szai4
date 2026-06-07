"""测试 data_loader 模块。"""

import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    CATEGORICAL_COLS,
    TARGET_COL,
    _resolve_data_dir,
    get_categorical_counts,
    get_categorical_cols,
    get_data_summary,
    get_numeric_cols,
    get_numeric_stats,
    get_target_distribution,
    load_test,
    load_train,
)


# ── 测试用合成数据 ──────────────────────────────────────────────


def make_train_csv() -> pd.DataFrame:
    """创建最小训练数据集,含全部 22 列。"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "age": [51, 50, 48, 26],
            "job": ["admin.", "services", "blue-collar", "entrepreneur"],
            "marital": ["divorced", "married", "divorced", "single"],
            "education": [
                "professional.course",
                "high.school",
                "basic.9y",
                "high.school",
            ],
            "default": ["no", "unknown", "no", "yes"],
            "housing": ["yes", "yes", "no", "yes"],
            "loan": ["yes", "no", "no", "yes"],
            "contact": ["cellular", "cellular", "cellular", "cellular"],
            "month": ["aug", "may", "apr", "aug"],
            "day_of_week": ["mon", "mon", "wed", "fri"],
            "duration": [4621, 4715, 171, 359],
            "campaign": [1, 1, 0, 26],
            "pdays": [112, 412, 1027, 998],
            "previous": [2, 2, 1, 0],
            "poutcome": ["failure", "nonexistent", "failure", "nonexistent"],
            "emp_var_rate": [1.4, -1.8, -1.8, 1.4],
            "cons_price_index": [90.81, 96.33, 96.33, 97.08],
            "cons_conf_index": [-35.53, -40.58, -44.74, -35.55],
            "lending_rate3m": [0.69, 4.05, 1.5, 5.11],
            "nr_employed": [5219.74, 4974.79, 5022.61, 5222.87],
            "subscribe": ["no", "yes", "no", "yes"],
        }
    )


def make_test_csv() -> pd.DataFrame:
    """创建最小测试数据集,含 21 列(无 subscribe)。"""
    df = make_train_csv()
    return df.drop(columns=["subscribe"])


# ── 文件加载测试 ────────────────────────────────────────────────


def test_load_train_success():
    """加载正常的 train.csv 应成功返回 DataFrame。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        train_path = Path(tmpdir) / "train.csv"
        make_train_csv().to_csv(train_path, index=False)
        df = load_train(data_dir=tmpdir)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (4, 22)
        assert TARGET_COL in df.columns


def test_load_train_file_not_found():
    """train.csv 不存在时应抛出 FileNotFoundError。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError, match="训练数据文件不存在"):
            load_train(data_dir=tmpdir)


def test_load_test_success():
    """加载正常的 test.csv 应成功返回 DataFrame,不含目标列。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test.csv"
        make_test_csv().to_csv(test_path, index=False)
        df = load_test(data_dir=tmpdir)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (4, 21)
        assert TARGET_COL not in df.columns


def test_load_test_file_not_found():
    """test.csv 不存在时应抛出 FileNotFoundError。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError, match="测试数据文件不存在"):
            load_test(data_dir=tmpdir)


def test_load_train_resolves_data_dir_from_env():
    """DATA_DIR 环境变量应被优先使用。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        train_path = Path(tmpdir) / "train.csv"
        make_train_csv().to_csv(train_path, index=False)
        os.environ["DATA_DIR"] = tmpdir
        try:
            df = load_train()
            assert df.shape == (4, 22)
        finally:
            del os.environ["DATA_DIR"]


def test_categorical_dtype_set_on_load():
    """加载后已知类别列应被设为 category dtype。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        train_path = Path(tmpdir) / "train.csv"
        make_train_csv().to_csv(train_path, index=False)
        df = load_train(data_dir=tmpdir)
        for col in CATEGORICAL_COLS:
            assert str(df[col].dtype) == "category", f"{col} 应为 category dtype"


# ── 特征分类测试 ────────────────────────────────────────────────


def test_get_numeric_cols():
    df = make_train_csv()
    nums = get_numeric_cols(df)
    assert "age" in nums
    assert "duration" in nums
    assert "subscribe" not in nums  # object 列不出现


def test_get_categorical_cols():
    df = make_train_csv()
    cats = get_categorical_cols(df)
    assert "job" in cats
    assert "subscribe" in cats  # object col


# ── 数据总览测试 ─────────────────────────────────────────────────


def test_get_data_summary():
    df = make_train_csv()
    summary = get_data_summary(df)
    assert summary["shape"] == (4, 22)
    assert len(summary["columns"]) == 22
    assert summary["missing_total"] == 0


def test_get_data_summary_with_missing():
    df = make_train_csv()
    df.loc[0, "age"] = None
    summary = get_data_summary(df)
    assert summary["missing"]["age"] == 1
    assert summary["missing_total"] == 1


# ── 目标分布测试 ─────────────────────────────────────────────────


def test_get_target_distribution():
    df = make_train_csv()
    dist = get_target_distribution(df)
    assert dist["counts"] == {"no": 2, "yes": 2}
    assert dist["proportions"] == {"no": 0.5, "yes": 0.5}


def test_get_target_distribution_no_col():
    df = make_test_csv()
    dist = get_target_distribution(df)
    assert dist == {"counts": {}, "proportions": {}}


# ── 数值统计测试 ─────────────────────────────────────────────────


def test_get_numeric_stats():
    df = make_train_csv()
    stats = get_numeric_stats(df, "age")
    assert "mean" in stats
    assert stats["count"] == 4
    assert stats["min"] == 26.0
    assert stats["max"] == 51.0


def test_get_numeric_stats_invalid_col():
    df = make_train_csv()
    with pytest.raises(ValueError, match="列"):
        get_numeric_stats(df, "not_a_column")


# ── 类别频次测试 ─────────────────────────────────────────────────


def test_get_categorical_counts():
    df = make_train_csv()
    counts, crosstab = get_categorical_counts(df, "job")
    assert len(counts) == 4  # 4 个不同 job
    # 交叉表含 yes / no 列
    assert "yes" in crosstab.columns
    assert "no" in crosstab.columns


def test_get_categorical_counts_no_target():
    df = make_test_csv()
    counts, crosstab = get_categorical_counts(df, "job")
    assert len(counts) == 4
    assert crosstab.empty


def test_get_categorical_counts_invalid_col():
    df = make_train_csv()
    with pytest.raises(ValueError, match="列"):
        get_categorical_counts(df, "ghost")


# ── 路径解析测试 ─────────────────────────────────────────────────


def test_resolve_data_dir_default():
    path = _resolve_data_dir()
    assert path.name == "data"
    assert path.parent.name == "banksys_szai4"
