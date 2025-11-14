#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uptime Kuma REST API 服务器

这个脚本将 Uptime Kuma Socket.IO API 封装成 REST API
其他程序可以通过 HTTP 请求获取监控信息

使用方法:
    python rest_api_server.py

然后可以用 cURL/浏览器访问:
    http://localhost:58273/api/info
    http://localhost:58273/api/monitors/<id>/performance
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from uptime_kuma_api import UptimeKumaApi
from functools import wraps
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPTIME_KUMA_URL = os.getenv('UPTIME_KUMA_URL', 'http://127.0.0.1:3001')
UPTIME_KUMA_USERNAME = os.getenv('UPTIME_KUMA_USERNAME', 'admin')
UPTIME_KUMA_PASSWORD = os.getenv('UPTIME_KUMA_PASSWORD', 'admin')

# API 认证 Token（修改为你自己的随机字符串）
API_TOKEN = os.getenv('API_TOKEN', '3f9a8c7e2d1b5a4f6e8c9d0a7b3e1f2a4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f')

def require_token(f):
    """API Token 认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取 token
        token = request.headers.get('Authorization')

        # 检查 token 格式：Bearer <token>
        if token and token.startswith('Bearer '):
            token = token[7:]  # 移除 "Bearer " 前缀

        # 验证 token
        if not token or token != API_TOKEN:
            return jsonify({
                'success': False,
                'error': 'Unauthorized: Invalid or missing API token'
            }), 401

        return f(*args, **kwargs)
    return decorated_function


def get_api():
    """获取 API 连接"""
    api = UptimeKumaApi(UPTIME_KUMA_URL)
    api.login(UPTIME_KUMA_USERNAME, UPTIME_KUMA_PASSWORD)
    return api


@app.route('/')
def index():
    """禁止未认证访问"""
    return '', 404


@app.errorhandler(404)
def not_found(e):
    """所有未定义的路由返回 404，不泄露任何信息"""
    return '', 404


@app.route('/health', methods=['GET'])
def health_check():
    """内部健康检查端点（仅用于 Docker 健康检查）"""
    return 'OK', 200


@app.route('/api/info', methods=['GET'])
@require_token
def get_info():
    """获取系统信息"""
    try:
        api = get_api()
        info = api.info()
        api.disconnect()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitors/<int:monitor_id>/performance', methods=['GET'])
@require_token
def get_monitor_performance(monitor_id):
    """获取监控器性能数据（包含4个关键指标和不同时间段的心跳数据）"""
    try:
        api = get_api()

        # 获取所有必要的数据
        all_uptime = api.uptime()
        all_avg_ping = api.avg_ping()

        # 获取不同时间段的心跳数据
        # API 只能获取"最近X小时"的数据，无法获取特定区间
        # 所以我们获取完整数据，然后在程序中过滤
        beats_1h = api.get_monitor_beats(monitor_id, 1)    # 0-60分钟
        beats_3h = api.get_monitor_beats(monitor_id, 3)    # 0-3小时
        beats_6h = api.get_monitor_beats(monitor_id, 6)    # 0-6小时
        beats_24h = api.get_monitor_beats(monitor_id, 24)  # 0-24小时
        beats_1w = api.get_monitor_beats(monitor_id, 168)  # 0-1周

        api.disconnect()

        # 提取当前监控器的数据
        uptime_data = all_uptime.get(monitor_id, {})
        avg_ping = all_avg_ping.get(monitor_id)

        # 获取当前 Ping
        current_ping = None
        if beats_1h:
            last_heartbeat = beats_1h[-1]
            current_ping = last_heartbeat.get('ping')

        # 转换心跳数据的函数
        def convert_heartbeats(beats):
            result = []
            for beat in beats:
                status = beat.get('status')
                status_value = status.value if hasattr(status, 'value') else status
                status_name = status.name if hasattr(status, 'name') else str(status)

                result.append({
                    'id': beat.get('id'),
                    'status': status_value,
                    'status_name': status_name,
                    'ping': beat.get('ping'),
                    'time': beat.get('time'),
                    'duration': beat.get('duration'),
                    'msg': beat.get('msg'),
                    'important': beat.get('important'),
                    'down_count': beat.get('down_count')
                })
            return result

        # 统计数据 - 返回原始数据
        # 需要将 uptime_data 的键统一转换为字符串，并转换为百分比
        uptime_formatted = {}
        for key, value in uptime_data.items():
            key_str = str(key)  # 确保键是字符串
            uptime_formatted[key_str] = value * 100 if value is not None else None

        stats = {
            'ping': {
                'current': current_ping,
                'avg_24h': avg_ping
            },
            'uptime': uptime_formatted  # 格式化后的 uptime 数据
        }

        # 简化的心跳数据 - 只包含 status 和 time（用于竖条图）
        def simplify_heartbeats(beats):
            """简化心跳数据，只保留状态和时间"""
            result = []
            for beat in beats:
                status = beat.get('status')
                status_value = status.value if hasattr(status, 'value') else status

                result.append({
                    'status': status_value,  # 1=UP, 0=DOWN
                    'time': beat.get('time')
                })
            return result

        return jsonify({
            'success': True,
            'monitor_id': monitor_id,
            'stats': stats,
            'heartbeats': {
                'recent_1h': convert_heartbeats(beats_1h),   # 最近1小时 (60分钟)
                'recent_3h': convert_heartbeats(beats_3h),   # 最近3小时
                'recent_6h': convert_heartbeats(beats_6h),   # 最近6小时
                'recent_24h': convert_heartbeats(beats_24h), # 最近24小时
                'recent_1w': convert_heartbeats(beats_1w)    # 最近1周
            },
            'uptime_bars': simplify_heartbeats(beats_24h)  # 24小时的竖条状态数据
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  Uptime Kuma REST API Server (精简版)")
    print("=" * 60)
    print(f"\n  Uptime Kuma URL: {UPTIME_KUMA_URL}")
    print(f"  Uptime Kuma 版本: 2.x")
    print(f"  REST API 地址: http://localhost:58273")

    # 检查是否使用默认 Token
    if API_TOKEN == 'your-secret-token-change-me':
        print(f"\n  ⚠️  警告: 正在使用默认 API Token!")
        print(f"  请修改 rest_api_server.py 中的 API_TOKEN")
        print(f"  或设置环境变量: export API_TOKEN='your-random-token'")
    else:
        print(f"\n  ✅ API Token 已设置")

    print(f"\n  可用端点 (需要认证):")
    print(f"    GET  http://localhost:58273/api/info")
    print(f"    GET  http://localhost:58273/api/monitors/<id>/performance")
    print(f"\n  测试命令 (带认证):")
    print(f"    curl -H 'Authorization: Bearer {API_TOKEN}' http://localhost:58273/api/info")
    print(f"    curl -H 'Authorization: Bearer {API_TOKEN}' http://localhost:58273/api/monitors/1/performance")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=58273, debug=True)
