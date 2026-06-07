# banksys_szai4 · 银行营销数据分析与预测系统

基于银行营销历史数据,提供交互式数据分析看板与在线认购预测系统。

## 功能

- **📊 数据分析**:探索性数据分析(EDA),特征分布、目标变量分析、相关性可视化。
- **🔮 在线预测**:点选式表单输入客户特征,实时预测认购意向。

## 技术栈

Python 3.11 · Streamlit · scikit-learn · plotly · Docker

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用 (端口 8004)
streamlit run app.py --server.port=8004
```

## 目录结构

```
banksys_szai4/
├── app.py              # Streamlit 主入口
├── src/                # 核心业务逻辑
├── pages/              # Streamlit 多页面
├── tests/              # 测试
├── data/               # 数据(不进 Git)
├── models/             # 模型产物(不进 Git)
├── standards/          # AI 项目规范与记忆
└── .github/workflows/  # CI/CD
```
