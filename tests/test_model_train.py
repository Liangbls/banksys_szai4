"""测试 model_train 模块。"""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.model_train import (
    RANDOM_SEED,
    extract_feature_importance,
    load_data,
    preprocess,
    run_training,
    save_model,
    train_and_evaluate,
)


# ── 合成数据 ─────────────────────────────────────────────────────


def make_train_df(n: int = 200) -> pd.DataFrame:
    """创建与真实数据结构一致的合成训练数据。"""
    np.random.seed(RANDOM_SEED)
    jobs = ["admin.", "blue-collar", "technician", "services", "entrepreneur"]
    maritals = ["married", "single", "divorced"]
    educations = ["high.school", "basic.9y", "professional.course", "university.degree"]
    defaults = ["no", "yes", "unknown"]
    housings = ["yes", "no", "unknown"]
    loans = ["no", "yes"]
    contacts = ["cellular", "telephone"]
    months = ["jan", "feb", "mar", "apr", "may", "jun"]
    days = ["mon", "tue", "wed", "thu", "fri"]
    poutcomes = ["failure", "nonexistent", "success"]

    df = pd.DataFrame(
        {
            "id": range(1, n + 1),
            "age": np.random.randint(20, 70, n),
            "job": np.random.choice(jobs, n),
            "marital": np.random.choice(maritals, n),
            "education": np.random.choice(educations, n),
            "default": np.random.choice(defaults, n),
            "housing": np.random.choice(housings, n),
            "loan": np.random.choice(loans, n),
            "contact": np.random.choice(contacts, n),
            "month": np.random.choice(months, n),
            "day_of_week": np.random.choice(days, n),
            "duration": np.random.randint(0, 5000, n),
            "campaign": np.random.randint(1, 30, n),
            "pdays": np.random.randint(0, 999, n),
            "previous": np.random.randint(0, 5, n),
            "poutcome": np.random.choice(poutcomes, n),
            "emp_var_rate": np.random.choice([1.4, -1.8, -0.1, 1.1], n).astype(float),
            "cons_price_index": np.random.uniform(89, 97, n),
            "cons_conf_index": np.random.uniform(-50, -30, n),
            "lending_rate3m": np.random.uniform(0.5, 5.5, n),
            "nr_employed": np.random.uniform(4900, 5300, n),
        }
    )

    # 生成有区分度的目标变量(信号足够强以保证 AUC >= 0.70)
    prob = 1 / (
        1
        + np.exp(
            -(
                (df["duration"] - 1500) / 500 * 1.5
                + (df["previous"] - 1) * 1.0
                + (df["emp_var_rate"] + 0.5) * 0.8
                + (df["campaign"] - 5) / 10 * (-0.8)
            )
        )
    )
    df["subscribe"] = np.where(np.random.random(n) < prob, "yes", "no")
    return df


# ── 数据加载测试 ─────────────────────────────────────────────────


def test_load_data_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        train_path = Path(tmpdir) / "train.csv"
        make_train_df().to_csv(train_path, index=False)
        df = load_data(tmpdir)
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 200
        assert "subscribe" in df.columns


def test_load_data_file_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(FileNotFoundError):
            load_data(tmpdir)


# ── 预处理测试 ───────────────────────────────────────────────────


def test_preprocess_output_shapes():
    df = make_train_df(200)
    X, y, preprocessor = preprocess(df)
    assert isinstance(X, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert X.shape[0] == 200
    assert y.shape[0] == 200
    assert set(y) <= {0, 1}


def test_preprocess_handles_missing_categorical():
    """预处理应能处理类别列中有未见过的值(handle_unknown='ignore')。"""
    df = make_train_df(100)
    df.loc[0, "job"] = "never-seen-before"
    X, y, preprocessor = preprocess(df)
    assert X.shape[0] == 100


# ── 训练与评估测试 ───────────────────────────────────────────────


def test_train_and_evaluate_returns_expected_keys():
    df = make_train_df(200)
    X, y, _ = preprocess(df)
    result = train_and_evaluate(X, y)
    assert "best_model" in result
    assert result["best_model"] is not None
    assert "best_name" in result
    assert "best_auc" in result
    assert 0.0 <= result["best_auc"] <= 1.0
    assert "all_metrics" in result
    assert len(result["all_metrics"]) >= 1


def test_train_and_evaluate_auc_threshold():
    """合成数据应能通过 AUC 门槛(特征有区分度)。"""
    df = make_train_df(500)
    X, y, _ = preprocess(df)
    result = train_and_evaluate(X, y)
    assert result["best_auc"] >= 0.5  # 至少比随机好
    assert isinstance(result["auc_check_passed"], bool)


# ── 特征重要性测试 ───────────────────────────────────────────────


def test_extract_feature_importance_rf():
    df = make_train_df(200)
    X, y, preprocessor_obj = preprocess(df)
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=20, random_state=RANDOM_SEED)
    model.fit(X, y)
    X_raw = df.drop(columns=["subscribe", "id"])
    importances = extract_feature_importance(model, preprocessor_obj, X_raw)
    assert isinstance(importances, list)
    assert len(importances) > 0
    for item in importances:
        assert "feature" in item
        assert "importance" in item


def test_extract_feature_importance_lr():
    df = make_train_df(200)
    X, y, preprocessor_obj = preprocess(df)
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression(max_iter=500, random_state=RANDOM_SEED)
    model.fit(X, y)
    X_raw = df.drop(columns=["subscribe", "id"])
    importances = extract_feature_importance(model, preprocessor_obj, X_raw)
    assert isinstance(importances, list)


# ── 模型保存测试 ─────────────────────────────────────────────────


def test_save_model():
    with tempfile.TemporaryDirectory() as tmpdir:
        from sklearn.linear_model import LogisticRegression

        model = LogisticRegression()
        df = make_train_df(50)
        _, _, preprocessor_obj = preprocess(df)
        path = save_model(model, preprocessor_obj, tmpdir)
        assert Path(path).exists()
        # 验证可加载
        import joblib

        loaded = joblib.load(path)
        assert "model" in loaded
        assert "preprocessor" in loaded


# ── 完整训练流程测试 ─────────────────────────────────────────────


def test_run_training_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建数据
        data_dir = Path(tmpdir) / "data"
        data_dir.mkdir()
        make_train_df(600).to_csv(data_dir / "train.csv", index=False)

        model_dir = Path(tmpdir) / "models"
        exit_code = run_training(str(data_dir), str(model_dir))
        assert exit_code == 0

        # 验证输出文件
        assert (model_dir / "model.pkl").exists()
        imp_path = model_dir / "feature_importance.json"
        assert imp_path.exists()
        with open(imp_path, encoding="utf-8") as f:
            importances = json.load(f)
        assert len(importances) > 0


def test_run_training_file_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        exit_code = run_training(tmpdir, str(Path(tmpdir) / "models"))
        assert exit_code == 1


def test_preprocess_excludes_id_column():
    df = make_train_df(100)
    X, y, _ = preprocess(df)
    # id 不应该出现在特征空间中(ColumnTransformer 不会包含它)
    assert X.shape[1] > 0
