FROM python:3.11-slim

ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 安装生产运行依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 复制应用代码
COPY app.py .
COPY pages/ ./pages/
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/

# Streamlit 默认端口
EXPOSE 8501

# 启动 Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
