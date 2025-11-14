#!/bin/bash
# REST API 启动脚本

echo "======================================================"
echo "  启动 Uptime Kuma REST API 服务器"
echo "======================================================"

# 检查 Uptime Kuma 是否运行
if ! curl -s http://127.0.0.1:3001 > /dev/null; then
    echo "❌ Uptime Kuma 未运行"
    echo "   请先启动: docker run -d -p 3001:3001 louislam/uptime-kuma"
    exit 1
fi

echo "✅ Uptime Kuma 正在运行"

# 激活虚拟环境
source .venv/bin/activate

# 启动服务器
echo ""
echo "启动 REST API 服务器..."
echo "访问: http://localhost:58273/api/monitors"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "======================================================="
echo ""

python rest_api_server.py
