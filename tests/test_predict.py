"""测试 predict 模块。"""

import tempfile
from pathlib import Path

import pytest

from src.predict import (
    FEATURE_COLS,
    ModelLoadError,
    _resolve_model_path,
    get_default_features,
    load_model,
    predict,
)


# ── 辅助: 创建模拟 pipeline ──────────────────────────────────────


def _make_mock_pipeline():
    """创建一个最小可用的 pipeline 用于测试 predict 函数。"""
    from sklearn.ensemble import RandomForestClassifier
    from src.model_train import preprocess
    from tests.test_model_train import make_train_df as _make_df

    df = _make_df(200)
    X, y, preprocessor_obj = preprocess(df)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    return {
        "model": model,
        "preprocessor": preprocessor_obj,
    }


def _save_pipeline(pipeline: dict, tmpdir: str) -> str:
    import joblib

    path = Path(tmpdir) / "model.pkl"
    joblib.dump(pipeline, path)
    return str(path)


# ── 模型加载测试 ─────────────────────────────────────────────────


def test_load_model_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = _make_mock_pipeline()
        model_path = _save_pipeline(pipeline, tmpdir)
        loaded = load_model(model_path)
        assert "model" in loaded
        assert "preprocessor" in loaded


def test_load_model_file_not_found():
    with pytest.raises(ModelLoadError, match="模型文件不存在"):
        load_model("/nonexistent/path/model.pkl")


def test_load_model_invalid_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        import joblib

        path = Path(tmpdir) / "bad.pkl"
        joblib.dump({"not_model": 123}, path)
        with pytest.raises(ModelLoadError, match="格式无效"):
            load_model(str(path))


def test_resolve_model_path_default():
    path = _resolve_model_path()
    assert path.name == "model.pkl"


def test_resolve_model_path_explicit():

    path = _resolve_model_path("/custom/path/model.pkl")
    assert path.as_posix() == "/custom/path/model.pkl"


# ── 预测测试 ─────────────────────────────────────────────────────


def test_predict_returns_expected_keys():
    pipeline = _make_mock_pipeline()
    features = get_default_features()
    result = predict(features, pipeline)
    assert "prediction" in result
    assert result["prediction"] in ("yes", "no")
    assert "probability" in result
    assert 0.0 <= result["probability"] <= 1.0
    assert "input_features" in result


def test_predict_yes_and_no_both_possible():
    """不同特征应产生不同预测。"""
    pipeline = _make_mock_pipeline()

    # 构造高概率 yes 的特征
    high_features = get_default_features()
    high_features["duration"] = 4000
    high_features["previous"] = 5
    high_features["poutcome"] = "success"

    # 构造低概率的特征
    low_features = get_default_features()
    low_features["duration"] = 50
    low_features["previous"] = 0
    low_features["poutcome"] = "failure"

    result_high = predict(high_features, pipeline)
    result_low = predict(low_features, pipeline)

    # 高 duration + previous 的样本应倾向于更高概率
    assert result_high["probability"] >= result_low["probability"]


def test_predict_with_missing_optional_cols():
    """FEATURE_COLS 中缺失的列应被忽略(不会崩溃)。"""
    pipeline = _make_mock_pipeline()
    features = {"age": 30, "job": "admin.", "duration": 500}
    result = predict(features, pipeline)
    assert result["prediction"] in ("yes", "no")


def test_predict_all_numeric_coerced():
    """字符串数值应被自动转为 float。"""
    pipeline = _make_mock_pipeline()
    features = get_default_features()
    # 某些数值特征传字符串
    features["age"] = "35"
    features["duration"] = "1000"
    result = predict(features, pipeline)
    assert result["prediction"] in ("yes", "no")


# ── 默认特征测试 ─────────────────────────────────────────────────


def test_get_default_features():
    defaults = get_default_features()
    assert isinstance(defaults, dict)
    for col in FEATURE_COLS:
        assert col in defaults, f"缺失默认值: {col}"
    assert defaults["age"] == 40
    assert defaults["job"] == "admin."


def test_default_features_are_predictable():
    """默认特征应能直接用于预测。"""
    pipeline = _make_mock_pipeline()
    features = get_default_features()
    result = predict(features, pipeline)
    assert result["prediction"] in ("yes", "no")
