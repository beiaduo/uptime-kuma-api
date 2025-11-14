# Uptime Kuma REST API 使用指南

## 快速开始

### 一键部署

```bash
wget https://raw.githubusercontent.com/beiaduo/uptime-kuma-api/master/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

## API 端点

### 基本信息

- **端口**: 58273
- **认证**: Bearer Token
- **格式**: JSON

### 1. 获取系统信息

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:58273/api/info
```

**响应示例**:
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

### 2. 获取监控器性能数据

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:58273/api/monitors/1/performance
```

**响应示例**:
```json
{
  "success": true,
  "monitor_id": 1,
  "stats": {
    "ping": {
      "current": 25.5,
      "avg_24h": 28.82
    },
    "uptime": {
      "24": 100,
      "720": 100,
      "1y": 100
    }
  },
  "heartbeats": {
    "recent_1h": [...],
    "recent_3h": [...],
    "recent_6h": [...],
    "recent_24h": [...],
    "recent_1w": [...]
  },
  "uptime_bars": [
    {
      "status": 1,
      "time": "2025-11-14 02:16:19.658"
    }
  ]
}
```

## 数据说明

### stats.ping
- `current`: 当前 Ping 值 (ms)
- `avg_24h`: 24小时平均 Ping (ms)

### stats.uptime
- `24`: 24小时在线率 (%)
- `720`: 30天在线率 (%)
- `1y`: 1年在线率 (%)

### heartbeats
每个心跳记录包含：
- `id`: 心跳 ID
- `status`: 状态 (1=在线, 0=离线)
- `status_name`: 状态名称 ("UP"/"DOWN")
- `ping`: Ping 值 (ms)
- `time`: 时间戳
- `duration`: 持续时间
- `msg`: 消息
- `important`: 是否重要
- `down_count`: 宕机次数

### uptime_bars
简化的状态数据，用于绘制竖条图：
- `status`: 1=在线, 0=离线
- `time`: 时间戳

## 使用示例

### Python

```python
import requests

# 配置
API_URL = "http://localhost:58273"
TOKEN = "your-api-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 获取系统信息
response = requests.get(f"{API_URL}/api/info", headers=headers)
print(response.json())

# 获取监控器性能数据
response = requests.get(f"{API_URL}/api/monitors/1/performance", headers=headers)
data = response.json()

# 打印统计信息
print(f"当前 Ping: {data['stats']['ping']['current']} ms")
print(f"24小时在线率: {data['stats']['uptime']['24']}%")

# 获取最近1小时的心跳数据
recent_heartbeats = data['heartbeats']['recent_1h']
print(f"最近1小时心跳数: {len(recent_heartbeats)}")
```

### JavaScript

```javascript
const API_URL = "http://localhost:58273";
const TOKEN = "your-api-token";

// 获取系统信息
fetch(`${API_URL}/api/info`, {
  headers: {
    "Authorization": `Bearer ${TOKEN}`
  }
})
  .then(response => response.json())
  .then(data => console.log(data));

// 获取监控器性能数据
fetch(`${API_URL}/api/monitors/1/performance`, {
  headers: {
    "Authorization": `Bearer ${TOKEN}`
  }
})
  .then(response => response.json())
  .then(data => {
    console.log("当前 Ping:", data.stats.ping.current, "ms");
    console.log("24小时在线率:", data.stats.uptime["24"], "%");
    console.log("最近1小时心跳数:", data.heartbeats.recent_1h.length);
  });
```

### cURL

```bash
# 设置变量
API_URL="http://localhost:58273"
TOKEN="your-api-token"

# 获取系统信息
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/info | jq

# 获取监控器1的性能数据
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/monitors/1/performance | jq

# 只获取统计信息
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/monitors/1/performance | jq '.stats'

# 只获取当前 Ping
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/monitors/1/performance | jq '.stats.ping.current'

# 获取最近1小时的心跳数
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/monitors/1/performance | jq '.heartbeats.recent_1h | length'
```

## 管理命令

### Docker 部署

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码并重启
git pull
docker-compose up -d --build
```

### 查看配置

```bash
# 查看 API Token
cat /opt/uptime-kuma-rest-api/.env

# 查看服务状态
docker-compose ps

# 查看容器日志
docker-compose logs --tail=100
```

## 错误处理

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized: Invalid or missing API token"
}
```
**解决**: 检查 Token 是否正确，确保请求头格式为 `Authorization: Bearer YOUR_TOKEN`

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "unable to connect"
}
```
**解决**: 检查 Uptime Kuma 服务器地址、用户名和密码是否正确

## 常见问题

### 如何获取 API Token？

Token 在部署时自动生成，可以通过以下方式查看：
```bash
cat /opt/uptime-kuma-rest-api/.env | grep API_TOKEN
```

### 如何更改 API Token？

1. 编辑 `.env` 文件
2. 重启服务：`docker-compose restart`

### 如何更改端口？

端口已设置为 58273（冷门端口，更安全），如需更改：
1. 修改 `docker-compose.yml` 中的端口映射
2. 修改 `rest_api_server.py` 中的端口
3. 重新构建：`docker-compose up -d --build`

### 如何添加防火墙规则？

```bash
# UFW
sudo ufw allow 58273/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 58273 -j ACCEPT
```

## 安全建议

1. ✅ 使用强随机 Token（部署时自动生成）
2. ✅ 通过防火墙限制访问 IP
3. ✅ 使用 Nginx 反向代理配置 SSL
4. ✅ 不要将 `.env` 文件提交到 Git
5. ✅ 定期更新依赖包

## 技术栈

- Python 3.11
- Flask (REST API 框架)
- Socket.IO (与 Uptime Kuma 通信)
- Docker (容器化部署)
- Uptime Kuma 2.x

## 项目地址

- GitHub: https://github.com/beiaduo/uptime-kuma-api
- 部署脚本: https://raw.githubusercontent.com/beiaduo/uptime-kuma-api/master/deploy.sh
