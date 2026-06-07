# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_szai4`
- **一句话目标**:基于银行营销历史数据,提供交互式数据分析看板与在线认购预测系统,辅助银行精准营销决策。
- **使用者/受益者**:银行客户经理 / 营销人员 — 通过可视化探索数据特征,并通过点选式表单快速预测目标客户是否会认购定期存款。
- **核心功能**:
  - **数据分析交互页面**:对银行营销数据进行探索性分析(EDA),含数据概览、特征分布、目标变量分析、特征相关性等可视化。
  - **离线模型训练**:基于历史数据训练二分类模型,预测客户是否认购(subscribe)。
  - **在线预测系统**:用户通过 Web 页面点选输入客户特征,调用已训练模型实时返回认购预测结果(会/不会)。
- **输入/数据**(如有):
  - 数据来源:`D:\黑马AI\claw1\part1\day02\数据\data\`
  - 文件:`train.csv`(22,500 行 × 22 列,含目标列 `subscribe`) + `test.csv`(7,500 行 × 21 列,无目标列)
  - 目标变量:`subscribe`(yes/no,二分类)
  - 特征:age, job, marital, education, default, housing, loan, contact, month, day_of_week, duration, campaign, pdays, previous, poutcome, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed
  - 数据不进 Git(通过 `.gitignore` 排除);模型产物 `.pkl` 也不进 Git。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程指定版本,ML 生态成熟 |
| Web/应用框架 | Streamlit | 适合数据应用快速搭建,内置交互组件,支持多页面 |
| 数据处理 | pandas, numpy | 表格数据操作标准库 |
| 可视化 | plotly / altair | 与 Streamlit 集成良好,交互式图表 |
| 机器学习 | scikit-learn | 经典分类模型(逻辑回归/随机森林/XGBoost),可序列化部署 |
| 测试 | pytest | Python 事实标准测试框架 |
| 格式/静态检查 | ruff | 统一格式(format)与 lint(check),替代 flake8+isort+black |
| 打包/运行 | Docker | 容器化部署,环境可复现 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_szai4/
├── standards/                   # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
├── app.py                       # Streamlit 主入口(主页 + 导航)
├── pages/                       # Streamlit 多页面
│   ├── 1_📊_data_analysis.py    # 数据分析交互页面
│   └── 2_🔮_prediction.py       # 在线预测页面
├── src/                         # 核心业务逻辑(纯 Python,与 UI 解耦)
│   ├── __init__.py
│   ├── data_loader.py           # 数据加载与预处理
│   ├── analysis.py              # 数据分析/统计计算函数
│   ├── model_train.py           # 模型离线训练脚本
│   └── predict.py               # 模型加载与预测推理
├── tests/                       # 测试
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_analysis.py
│   ├── test_model_train.py
│   └── test_predict.py
├── data/                        # 数据目录(不进 Git,本地挂载)
├── models/                      # 模型产物(不进 Git)
├── requirements.txt             # 生产运行依赖
├── requirements-dev.txt         # 本地/CI 检查依赖
├── Dockerfile                   # 容器构建文件
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov=src --cov-fail-under=80` |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | 模型 AUC ≥ 0.70(离线训练时自动检查) |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集(`data/`)、模型产物(`models/`)不进 Git,**通过 `.gitignore` 排除**。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 数据文件从本地路径加载,不硬编码绝对路径(通过配置/环境变量指定)。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys` | 服务器部署目录 |
| `<PORT>` | `8004` | 服务端口(容器内固定 8501,主机映射 8004) |
| `<PORT_MAX>` | `8014` | 主机端口回退区间的上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 自带健康检查端点 |
| `<SSH_USER>` | `root` | 部署用户(按实际服务器调整) |
| `<SSH_HOST>` | `<服务器公网 IP>` | 按实际部署环境填写 |
