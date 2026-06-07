"""离线模型训练脚本 (US-3).

独立可执行的训练脚本,完成:
1. 数据加载与预处理(编码、标准化)
2. 多模型训练与对比(LogisticRegression / RandomForest)
3. 验证集 AUC 评估
4. 模型保存与特征重要性导出

用法:
    python src/model_train.py --data-path data --model-dir models
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── 常量 ─────────────────────────────────────────────────────────

TARGET_COL = "subscribe"
AUC_THRESHOLD = 0.70
RANDOM_SEED = 42

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

EXCLUDE_COLS = ["id"]


def load_data(data_path: str) -> pd.DataFrame:
    """加载训练数据。"""
    train_file = Path(data_path) / "train.csv"
    if not train_file.exists():
        raise FileNotFoundError(f"训练数据文件不存在: {train_file}")
    logger.info("加载数据: %s (%d 行)", train_file, pd.read_csv(train_file).shape[0])
    return pd.read_csv(train_file)


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, ColumnTransformer]:
    """预处理数据:编码类别特征、标准化数值特征。

    Returns:
        (X, y, preprocessor): 特征矩阵、目标数组、预处理器(用于后续预测)。
    """
    logger.info("开始数据预处理...")

    # 分离特征与目标
    y_raw = df[TARGET_COL].copy()
    X_raw = df.drop(columns=[TARGET_COL] + [c for c in EXCLUDE_COLS if c in df.columns])

    # 目标编码
    label_enc = LabelEncoder()
    y = label_enc.fit_transform(y_raw)  # yes → 1, no → 0
    logger.info("目标分布: yes=%d, no=%d", int(y.sum()), int((1 - y).sum()))

    # 识别列类型
    num_cols = X_raw.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in X_raw.columns]

    # 预处理器: 数值标准化 + 类别独热编码
    preprocessor = ColumnTransformer(
        [
            ("num", StandardScaler(), num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                cat_cols,
            ),
        ]
    )

    X = preprocessor.fit_transform(X_raw)
    logger.info(
        "预处理完成: X.shape=%s, num_cols=%d, cat_cols=%d",
        X.shape,
        len(num_cols),
        len(cat_cols),
    )

    return X, y, preprocessor


def train_and_evaluate(X: np.ndarray, y: np.ndarray) -> dict:
    """训练多个模型并评估,返回最佳模型及其信息。

    Returns:
        dict: 含 best_model, best_name, best_auc, metrics, feature_names 等。
    """
    # 划分训练/验证集
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=y,
    )
    logger.info("训练集: %d, 验证集: %d", len(X_train), len(X_val))

    # 候选模型
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=2000, random_state=RANDOM_SEED
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        ),
    }

    best_model = None
    best_name = ""
    best_auc = 0.0
    all_metrics = {}

    for name, model in models.items():
        logger.info("训练模型: %s", name)
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_val)[:, 1]
        y_pred = model.predict(X_val)
        auc_val = roc_auc_score(y_val, y_prob)

        all_metrics[name] = {
            "auc": round(float(auc_val), 4),
            "classification_report": classification_report(
                y_val,
                y_pred,
                target_names=["no", "yes"],
                output_dict=True,
            ),
        }

        logger.info("  %s AUC: %.4f", name, auc_val)

        if auc_val > best_auc:
            best_auc = auc_val
            best_model = model
            best_name = name

    logger.info("最佳模型: %s (AUC=%.4f)", best_name, best_auc)

    return {
        "best_model": best_model,
        "best_name": best_name,
        "best_auc": float(best_auc),
        "auc_threshold": AUC_THRESHOLD,
        "auc_check_passed": float(best_auc) >= AUC_THRESHOLD,
        "all_metrics": all_metrics,
        "y_val": y_val,
        "y_prob": best_model.predict_proba(X_val)[:, 1],
    }


def extract_feature_importance(
    model, preprocessor: ColumnTransformer, X_raw: pd.DataFrame
) -> list[dict]:
    """从模型中提取特征重要性(若支持)。

    Returns:
        按重要性降序排列的特征列表。
    """
    num_cols = X_raw.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in X_raw.columns]

    # 获取 OneHotEncoder 展开后的类别列名
    ohe = preprocessor.named_transformers_["cat"]
    if hasattr(ohe, "get_feature_names_out"):
        cat_cols_expanded = list(ohe.get_feature_names_out(cat_cols))
    else:
        cat_cols_expanded = cat_cols

    all_feature_names = num_cols + cat_cols_expanded

    # 提取重要性
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).flatten()
    else:
        return []

    result = sorted(
        [
            {"feature": str(name), "importance": round(float(imp), 6)}
            for name, imp in zip(all_feature_names, importances)
        ],
        key=lambda x: x["importance"],
        reverse=True,
    )
    return result[:20]


def save_model(model, preprocessor: ColumnTransformer, model_dir: str) -> str:
    """保存模型与预处理器到指定目录。

    Returns:
        保存的模型文件路径。
    """
    import joblib

    model_path = Path(model_dir)
    model_path.mkdir(parents=True, exist_ok=True)

    pipeline = {
        "model": model,
        "preprocessor": preprocessor,
    }
    save_path = model_path / "model.pkl"
    joblib.dump(pipeline, save_path)
    logger.info("模型已保存: %s", save_path)
    return str(save_path)


def run_training(data_path: str, model_dir: str) -> int:
    """执行完整训练流程。

    Returns:
        0 成功, 1 失败。
    """
    try:
        # 1. 加载
        df = load_data(data_path)

        # 2. 预处理
        X, y, preprocessor = preprocess(df)

        # 3. 训练 + 评估
        result = train_and_evaluate(X, y)

        # 4. AUC 检查
        if not result["auc_check_passed"]:
            logger.error(
                "AUC 未达标: %.4f < %.2f",
                result["best_auc"],
                AUC_THRESHOLD,
            )
            return 1

        logger.info("✓ AUC 达标: %.4f ≥ %.2f", result["best_auc"], AUC_THRESHOLD)

        # 5. 特征重要性
        X_raw = df.drop(
            columns=[TARGET_COL] + [c for c in EXCLUDE_COLS if c in df.columns],
        )
        importances = extract_feature_importance(
            result["best_model"],
            preprocessor,
            X_raw,
        )
        if importances:
            logger.info("Top 10 重要特征:")
            for item in importances[:10]:
                logger.info("  %s: %.6f", item["feature"], item["importance"])

            # 保存特征重要性
            imp_path = Path(model_dir) / "feature_importance.json"
            imp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(imp_path, "w", encoding="utf-8") as f:
                json.dump(importances, f, ensure_ascii=False, indent=2)
            logger.info("特征重要性已保存: %s", imp_path)

        # 6. 保存模型
        save_model(result["best_model"], preprocessor, model_dir)

        logger.info("=== 训练完成 ===")
        logger.info("最佳模型: %s", result["best_name"])
        logger.info("AUC: %.4f", result["best_auc"])

        return 0

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.exception("训练失败: %s", e)
        return 1


# ── CLI 入口 ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="银行营销认购预测模型离线训练")
    parser.add_argument(
        "--data-path",
        default="data",
        help="数据目录路径(含 train.csv),默认 data/",
    )
    parser.add_argument(
        "--model-dir",
        default="models",
        help="模型输出目录,默认 models/",
    )
    args = parser.parse_args()

    exit_code = run_training(args.data_path, args.model_dir)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
