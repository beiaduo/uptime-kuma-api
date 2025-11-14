FROM python:3.11-slim

LABEL maintainer="Uptime Kuma REST API"
LABEL description="REST API wrapper for Uptime Kuma 2.x"

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件和库
COPY rest_api_server.py .
COPY uptime_kuma_api uptime_kuma_api

# 暴露端口
EXPOSE 58273

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:58273/', timeout=5)" || exit 1

# 启动应用
CMD ["python", "-u", "rest_api_server.py"]
