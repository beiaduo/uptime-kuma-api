# Uptime Kuma REST API

将远程 Uptime Kuma 2.x 服务器的 Socket.IO API 封装成简单的 REST API，方便其他程序获取监控数据。

## 特性

- ✅ 支持 Uptime Kuma 2.x
- ✅ Bearer Token 认证保护
- ✅ 完整的监控数据（Ping、Uptime、心跳）
- ✅ 多时间段心跳数据（1h, 3h, 6h, 24h, 1周）
- ✅ Docker 一键部署
- ✅ 健康检查和自动重启

## 快速部署（推荐）

### 方式一：一键部署脚本

**步骤 1**: 下载部署脚本
```bash
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/master/deploy.sh
chmod +x deploy.sh
```

**步骤 2**: 运行部署
```bash
./deploy.sh
```

脚本会自动：
1. 检查并安装 Docker 和 docker-compose
2. 克隆代码
3. 配置环境变量（会自动生成随机 Token）
4. 启动服务
5. 测试 API

> **注意**: 将 `YOUR_USERNAME/YOUR_REPO` 替换为你的 GitHub 用户名和仓库名

### 方式二：手动 Docker 部署

```bash
# 1. 克隆仓库（替换为你的仓库地址）
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 3. 启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

## 本地开发

### 1. 安装依赖

```bash
./安装.sh
```

或手动安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

编辑 `rest_api_server.py`，修改配置：

```python
# Uptime Kuma 服务器地址和登录凭据
UPTIME_KUMA_URL = 'http://your-server-ip:3001'
UPTIME_KUMA_USERNAME = 'your-username'
UPTIME_KUMA_PASSWORD = 'your-password'

# API 认证 Token（重要！修改为随机字符串）
API_TOKEN = 'your-secret-token-change-me'
```

或使用环境变量（推荐）：

```bash
export UPTIME_KUMA_URL="http://your-server-ip:3001"
export UPTIME_KUMA_USERNAME="your-username"
export UPTIME_KUMA_PASSWORD="your-password"
export API_TOKEN="your-random-secret-token-here"
```

**生成随机 Token**：
```bash
# 使用 openssl 生成随机 token
openssl rand -hex 32
```

### 3. 启动 REST API

```bash
./启动REST_API.sh
```

或手动启动：

```bash
source .venv/bin/activate
python rest_api_server.py
```

REST API 将运行在 http://localhost:58273

## API 端点

所有 API 端点都需要在请求头中携带 Token：

```
Authorization: Bearer <your-api-token>
```

### 1. 获取系统信息

```bash
GET http://localhost:58273/api/info
Header: Authorization: Bearer <your-api-token>
```

**请求示例**：
```bash
curl -H 'Authorization: Bearer your-api-token' http://localhost:58273/api/info
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "version": "2.0.2",
    "dbType": "sqlite",
    "serverTimezone": "America/Los_Angeles"
  }
}
```

**认证失败响应**：
```json
{
  "success": false,
  "error": "Unauthorized: Invalid or missing API token"
}
```

### 2. 获取监控器性能数据

```bash
GET http://localhost:58273/api/monitors/<monitor_id>/performance
Header: Authorization: Bearer <your-api-token>
```

**响应示例**：
```json
{
  "success": true,
  "monitor_id": 1,
  "stats": [
    {
      "label": "Ping (Current)",
      "value": 26.9,
      "unit": "ms"
    },
    {
      "label": "Avg. Ping (24-hour)",
      "value": 42.25,
      "unit": "ms"
    },
    {
      "label": "Uptime (24-hour)",
      "value": 100,
      "unit": "%"
    },
    {
      "label": "Uptime (30-day)",
      "value": 100,
      "unit": "%"
    }
  ],
  "heartbeats": {
    "recent_3h": [...],
    "recent_6h": [...],
    "recent_24h": [...],
    "recent_1w": [...]
  }
}
```

每个心跳记录包含：
- `id`: 心跳 ID
- `status`: 状态值 (1=UP, 0=DOWN)
- `status_name`: 状态名称
- `ping`: Ping 值 (ms)
- `time`: 时间戳
- `duration`: 持续时间
- `msg`: 消息
- `important`: 是否重要
- `down_count`: 宕机次数

## 在其他程序中使用

### Python

```python
import requests

# 设置认证头
headers = {'Authorization': 'Bearer your-api-token'}

# 获取系统信息
response = requests.get('http://localhost:58273/api/info', headers=headers)
data = response.json()
print(f"Uptime Kuma 版本: {data['data']['version']}")

# 获取监控器性能数据
response = requests.get('http://localhost:58273/api/monitors/1/performance', headers=headers)
data = response.json()
for stat in data['stats']:
    print(f"{stat['label']}: {stat['value']} {stat['unit']}")
```

### JavaScript

```javascript
// 获取性能数据
fetch('http://localhost:58273/api/monitors/1/performance', {
  headers: {
    'Authorization': 'Bearer your-api-token'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('Stats:', data.stats);
    console.log('Recent 3h heartbeats:', data.heartbeats.recent_3h.length);
  });
```

### cURL

```bash
# 设置 Token
TOKEN="your-api-token"

# 获取系统信息
curl -H "Authorization: Bearer $TOKEN" http://localhost:58273/api/info | jq

# 获取性能数据
curl -H "Authorization: Bearer $TOKEN" http://localhost:58273/api/monitors/1/performance | jq
```

## 版本信息

- **Uptime Kuma**: 2.x
- **Python**: 3.8+
- **uptime-kuma-api**: 来自 PR #86 (支持 2.x)

## 文件说明

- `rest_api_server.py` - REST API 服务器主文件
- `启动REST_API.sh` - 一键启动脚本
- `.archive/` - 归档的测试文件和文档

## License

MIT
