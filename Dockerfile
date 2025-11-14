FROM python:3.11-slim

LABEL maintainer="Uptime Kuma REST API"
LABEL description="REST API wrapper for Uptime Kuma 2.x"

WORKDIR /app

# 安装 curl（用于健康检查）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件和库
COPY rest_api_server.py .
COPY uptime_kuma_api uptime_kuma_api

# 启动应用
CMD ["python", "-u", "rest_api_server.py"]
