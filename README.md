# Uptime Kuma REST API

将 Uptime Kuma 2.x 的 Socket.IO API 封装成简单的 REST API，方便其他程序通过 HTTP 获取监控数据。

## 🚀 一键部署

```bash
wget https://github.com/beiaduo/uptime-kuma-api/releases/download/uptimekuma/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动完成：
1. 安装 Docker 和 docker-compose（如果没有）
2. 克隆代码到 `/opt/uptime-kuma-rest-api`
3. 配置环境变量（自动生成随机 Token）
4. 启动服务
5. 显示 API Token（请保存）

## 📊 API 功能说明

### 端点 1：获取系统信息

```bash
GET /api/info
```

**用途**: 获取 Uptime Kuma 版本、数据库类型等基本信息

**示例**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:58273/api/info
```

**返回数据**:
```json
{
  "success": true,
  "data": {
    "version": "2.0.2",
    "dbType": "sqlite",
    "serverTimezone": "UTC"
  }
}
```

### 端点 2：获取监控器性能数据

```bash
GET /api/monitors/<monitor_id>/performance
```

**用途**: 获取指定监控器的完整性能数据

**示例**:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:58273/api/monitors/1/performance
```

**返回数据**:
```json
{
  "success": true,
  "monitor_id": 1,
  "stats": {
    "ping": {
      "current": 25.5,      // 当前 Ping (ms)
      "avg_24h": 28.82      // 24小时平均 Ping (ms)
    },
    "uptime": {
      "24": 100,            // 24小时在线率 (%)
      "720": 100,           // 30天在线率 (%)
      "1y": 100             // 1年在线率 (%)
    }
  },
  "heartbeats": {
    "recent_1h": [...],     // 最近1小时的心跳数据
    "recent_3h": [...],     // 最近3小时的心跳数据
    "recent_6h": [...],     // 最近6小时的心跳数据
    "recent_24h": [...],    // 最近24小时的心跳数据
    "recent_1w": [...]      // 最近1周的心跳数据
  },
  "uptime_bars": [
    {
      "status": 1,          // 状态: 1=在线, 0=离线
      "time": "2025-11-14 02:16:19.658"
    }
  ]
}
```

## 📈 数据说明

### stats - 统计数据
- **ping.current**: 当前 Ping 值（毫秒）
- **ping.avg_24h**: 24小时平均 Ping（毫秒）
- **uptime.24**: 24小时在线率（百分比）
- **uptime.720**: 30天在线率（百分比）
- **uptime.1y**: 1年在线率（百分比）

### heartbeats - 详细心跳数据
每个心跳记录包含：
- `id`: 心跳 ID
- `status`: 状态（1=在线, 0=离线）
- `status_name`: 状态名称（"UP"/"DOWN"）
- `ping`: Ping 值（毫秒）
- `time`: 时间戳
- `duration`: 持续时间
- `msg`: 消息
- `important`: 是否重要
- `down_count`: 宕机次数

### uptime_bars - 状态竖条数据
用于绘制状态时间线图表，只包含：
- `status`: 1=在线, 0=离线
- `time`: 时间戳

## 💻 使用示例

### Python
```python
import requests

API_URL = "http://localhost:58273"
TOKEN = "your-api-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 获取监控器 1 的性能数据
response = requests.get(f"{API_URL}/api/monitors/1/performance", headers=headers)
data = response.json()

print(f"当前 Ping: {data['stats']['ping']['current']} ms")
print(f"24小时在线率: {data['stats']['uptime']['24']}%")
print(f"最近1小时心跳数: {len(data['heartbeats']['recent_1h'])}")
```

### JavaScript
```javascript
const API_URL = "http://localhost:58273";
const TOKEN = "your-api-token";

fetch(`${API_URL}/api/monitors/1/performance`, {
  headers: {"Authorization": `Bearer ${TOKEN}`}
})
  .then(r => r.json())
  .then(data => {
    console.log("当前 Ping:", data.stats.ping.current, "ms");
    console.log("24小时在线率:", data.stats.uptime["24"], "%");
  });
```

### cURL
```bash
TOKEN="your-api-token"

# 获取性能数据
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:58273/api/monitors/1/performance | jq

# 只获取当前 Ping
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:58273/api/monitors/1/performance | jq '.stats.ping.current'

# 只获取在线率
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:58273/api/monitors/1/performance | jq '.stats.uptime'
```

## 🔧 管理

### 查看 Token
```bash
cat /opt/uptime-kuma-rest-api/.env | grep API_TOKEN
```

### 查看日志
```bash
cd /opt/uptime-kuma-rest-api
docker-compose logs -f
```

### 重启服务
```bash
cd /opt/uptime-kuma-rest-api
docker-compose restart
```

### 更新代码
```bash
cd /opt/uptime-kuma-rest-api
git pull
docker-compose up -d --build
```

## 🔒 安全特性

- ✅ **Bearer Token 认证** - 所有 API 都需要认证
- ✅ **无信息泄露** - 未认证访问返回 404
- ✅ **冷门端口** - 使用 58273 端口
- ✅ **随机 Token** - 部署时自动生成强随机 Token

## 📦 技术栈

- Python 3.11
- Flask (REST API 框架)
- Socket.IO (与 Uptime Kuma 通信)
- Docker (容器化部署)

## 📄 许可证

MIT
