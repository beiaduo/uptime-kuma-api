#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uptime Kuma REST API 服务器

这个脚本将 Uptime Kuma Socket.IO API 封装成 REST API
其他程序可以通过 HTTP 请求获取监控信息

使用方法:
    首次运行: python rest_api_server.py --setup
    启动服务: python rest_api_server.py
    修改配置: python rest_api_server.py --config
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from uptime_kuma_api import UptimeKumaApi
from functools import wraps
import os
import json
import secrets
import random
import sys
import time
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 缓存配置
CACHE_TTL = 30  # 缓存30秒
cache = {}

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'api_config.json')

def generate_random_port():
    """生成随机端口 (49152-65535)"""
    return random.randint(49152, 65535)

def generate_random_token():
    """生成随机 API Token"""
    return secrets.token_hex(32)

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def setup_config():
    """交互式配置"""
    print("\n" + "=" * 50)
    print("  Uptime Kuma REST API - 配置向导")
    print("=" * 50 + "\n")

    config = {}

    # Uptime Kuma 配置
    config['uptime_kuma_url'] = input("Uptime Kuma URL: ").strip()
    config['uptime_kuma_username'] = input("Uptime Kuma 用户名: ").strip()
    config['uptime_kuma_password'] = input("Uptime Kuma 密码: ").strip()

    # API 配置
    use_random_port = input("\n使用随机端口? (y/n, 默认 y): ").strip().lower()
    if use_random_port in ['', 'y', 'yes']:
        config['api_port'] = generate_random_port()
        print(f"已生成随机端口: {config['api_port']}")
    else:
        port = input("API 端口 (默认 58273): ").strip()
        config['api_port'] = int(port) if port else 58273

    # Token 配置
    use_random_token = input("\n使用随机生成的 Token? (y/n, 默认 y): ").strip().lower()
    if use_random_token in ['', 'y', 'yes']:
        config['api_token'] = generate_random_token()
        print(f"已生成随机 Token: {config['api_token']}")
    else:
        config['api_token'] = input("API Token: ").strip()

    save_config(config)

    print("\n" + "=" * 50)
    print("  配置已保存!")
    print("=" * 50)
    print(f"  API 地址: http://localhost:{config['api_port']}/api/monitors/<id>")
    print(f"  Token: {config['api_token']}")
    print("=" * 50 + "\n")

def modify_config():
    """修改现有配置"""
    config = load_config()
    if not config:
        print("\n配置文件不存在，请先运行 --setup")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  修改配置 (留空保持不变)")
    print("=" * 50 + "\n")

    print(f"当前 Uptime Kuma URL: {config.get('uptime_kuma_url', 'N/A')}")
    new_url = input("新 URL: ").strip()
    if new_url:
        config['uptime_kuma_url'] = new_url

    print(f"\n当前用户名: {config.get('uptime_kuma_username', 'N/A')}")
    new_username = input("新用户名: ").strip()
    if new_username:
        config['uptime_kuma_username'] = new_username

    print(f"\n当前密码: {'*' * 8}")
    new_password = input("新密码: ").strip()
    if new_password:
        config['uptime_kuma_password'] = new_password

    print(f"\n当前端口: {config.get('api_port', 'N/A')}")
    new_port = input("新端口 (输入 'random' 生成随机端口): ").strip()
    if new_port == 'random':
        config['api_port'] = generate_random_port()
        print(f"已生成随机端口: {config['api_port']}")
    elif new_port:
        config['api_port'] = int(new_port)

    print(f"\n当前 Token: {config.get('api_token', 'N/A')[:16]}...")
    new_token = input("新 Token (输入 'random' 生成随机 Token): ").strip()
    if new_token == 'random':
        config['api_token'] = generate_random_token()
        print(f"已生成随机 Token: {config['api_token']}")
    elif new_token:
        config['api_token'] = new_token

    save_config(config)

    print("\n" + "=" * 50)
    print("  配置已更新!")
    print("=" * 50 + "\n")

# 加载配置（必须先运行 --setup）
config = load_config()
UPTIME_KUMA_URL = config.get('uptime_kuma_url') if config else None
UPTIME_KUMA_USERNAME = config.get('uptime_kuma_username') if config else None
UPTIME_KUMA_PASSWORD = config.get('uptime_kuma_password') if config else None
API_PORT = config.get('api_port') if config else None
API_TOKEN = config.get('api_token') if config else None

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


def get_cached_data(cache_key, fetch_func):
    """通用缓存函数"""
    current_time = time.time()

    # 检查缓存是否存在且未过期
    if cache_key in cache:
        cached_item = cache[cache_key]
        if current_time - cached_item['timestamp'] < CACHE_TTL:
            return cached_item['data']

    # 缓存不存在或已过期，重新获取数据
    data = fetch_func()

    # 更新缓存
    cache[cache_key] = {
        'data': data,
        'timestamp': current_time
    }

    return data


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


@app.route('/api/monitors/<int:monitor_id>', methods=['GET'])
@require_token
def get_monitor_performance(monitor_id):
    """获取监控器完整数据（缓存30秒）"""
    cache_key = f'monitor_{monitor_id}'

    def fetch_monitor_data():
        return _fetch_monitor_data(monitor_id)

    try:
        result = get_cached_data(cache_key, fetch_monitor_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _fetch_monitor_data(monitor_id):
    """实际获取监控器数据的函数"""
    try:
        api = get_api()

        # 获取系统信息
        info = api.info()

        # 获取监控器基本信息
        monitor = api.get_monitor(monitor_id)

        # 获取所有必要的数据
        all_uptime = api.uptime()
        all_avg_ping = api.avg_ping()

        # 获取不同时间段的心跳数据
        beats_1h = api.get_monitor_beats(monitor_id, 1)     # 1小时
        beats_3h = api.get_monitor_beats(monitor_id, 3)     # 3小时
        beats_6h = api.get_monitor_beats(monitor_id, 6)     # 6小时
        beats_24h = api.get_monitor_beats(monitor_id, 24)   # 24小时
        beats_1w = api.get_monitor_beats(monitor_id, 168)   # 1周
        beats_1m = api.get_monitor_beats(monitor_id, 720)   # 1个月 (30天)

        api.disconnect()

        # 提取当前监控器的数据
        uptime_data = all_uptime.get(monitor_id, {})
        avg_ping = all_avg_ping.get(monitor_id)

        # 获取当前 Ping
        current_ping = None
        if beats_1h:
            last_heartbeat = beats_1h[-1]
            current_ping = last_heartbeat.get('ping')

        # 获取服务器时区偏移（从 info 中获取）
        server_tz_offset = info.get('serverTimezoneOffset', '+00:00')  # 例如: "-08:00"

        # 解析时区偏移
        def parse_timezone_offset(offset_str):
            """解析时区偏移字符串，返回 timedelta 对象"""
            sign = 1 if offset_str[0] == '+' else -1
            hours, minutes = map(int, offset_str[1:].split(':'))
            return timedelta(hours=sign * hours, minutes=sign * minutes)

        tz_offset = parse_timezone_offset(server_tz_offset)

        # 时间格式化函数 - 将 UTC 时间转换为服务器本地时间
        def format_time(time_str):
            """将 UTC 时间转换为服务器本地时间"""
            if not time_str:
                return None
            try:
                # 解析 UTC 时间: "2025-11-14 07:39:34.818"
                dt_utc = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)

                # 转换为服务器本地时间
                dt_local = dt_utc + tz_offset

                # 返回格式化的本地时间字符串（精确到秒，不含毫秒）
                return dt_local.strftime("%Y-%m-%d %H:%M:%S")
            except:
                # 如果解析失败，返回原始值
                return time_str

        # 数据降采样函数
        def downsample_beats(beats, max_points=500):
            """如果数据点超过 max_points，进行均匀降采样"""
            if not beats or len(beats) <= max_points:
                return beats

            # 计算采样间隔
            step = len(beats) / max_points
            sampled = []

            for i in range(max_points):
                index = int(i * step)
                if index < len(beats):
                    sampled.append(beats[index])

            return sampled

        # 转换心跳数据的函数 - 只返回 ping, status, time
        def convert_heartbeats(beats, apply_downsampling=True):
            # 先降采样
            if apply_downsampling:
                beats = downsample_beats(beats)

            result = []
            for beat in beats:
                status = beat.get('status')
                status_value = status.value if hasattr(status, 'value') else status

                result.append({
                    'ping': beat.get('ping'),
                    'status': status_value,  # 1=UP, 0=DOWN
                    'time': format_time(beat.get('time'))  # 格式化为 ISO 8601
                })
            return result

        # 统计数据 - 使用清晰的英文键名
        stats = {
            'current_ping': round(current_ping, 2) if current_ping is not None else None,
            'avg_ping': round(avg_ping, 2) if avg_ping is not None else None,
            'uptime_one_day': round(uptime_data.get(24) * 100, 2) if uptime_data.get(24) is not None else None,
            'uptime_one_month': round(uptime_data.get(720) * 100, 2) if uptime_data.get(720) is not None else None,
            'uptime_one_year': round(uptime_data.get('1y') * 100, 2) if uptime_data.get('1y') is not None else None
        }

        # 简化的心跳数据 - 只包含 status 和 time（用于竖条图）
        def simplify_heartbeats(beats, max_points=60):
            """简化心跳数据，只保留状态和时间，限制最多返回 max_points 个"""
            # 限制数量：超过 max_points 只返回最后 max_points 个（最新的）
            if beats and len(beats) > max_points:
                beats = beats[-max_points:]

            result = []
            for beat in beats:
                status = beat.get('status')
                status_value = status.value if hasattr(status, 'value') else status

                result.append({
                    'status': status_value,  # 1=UP, 0=DOWN
                    'time': format_time(beat.get('time'))  # 格式化为 ISO 8601
                })
            return result

        return {
            'success': True,
            'info': info,
            'name': monitor.get('name'),
            'stats': stats,
            'chart': {
                'one_hour': convert_heartbeats(beats_1h),
                'three_hours': convert_heartbeats(beats_3h),
                'six_hours': convert_heartbeats(beats_6h),
                'one_day': convert_heartbeats(beats_24h),
                'one_week': convert_heartbeats(beats_1w),
                'one_month': convert_heartbeats(beats_1m)
            },
            'bar': simplify_heartbeats(beats_1h)
        }
    except Exception as e:
        raise e


if __name__ == '__main__':
    # 处理命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup':
            setup_config()
            sys.exit(0)
        elif sys.argv[1] == '--config':
            modify_config()
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print("\n使用方法:")
            print("  python rest_api_server.py --setup   # 初始化配置")
            print("  python rest_api_server.py --config  # 修改配置")
            print("  python rest_api_server.py           # 启动服务")
            sys.exit(0)

    # 检查配置文件
    if not load_config():
        print("\n⚠️  配置文件不存在，请先运行: python rest_api_server.py --setup\n")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  Uptime Kuma REST API Server")
    print("=" * 50)
    print(f"  API: http://localhost:{API_PORT}/api/monitors/<id>")
    print(f"  Token: {API_TOKEN[:16]}...")
    print("=" * 50 + "\n")

    app.run(host='0.0.0.0', port=API_PORT, debug=True)
