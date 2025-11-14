# Release Notes

## v1.0.0 - uptimekuma (2025-11-13)

### 🎉 首次发布

Uptime Kuma REST API - 将 Uptime Kuma 2.x 的 Socket.IO API 封装成简单的 REST API。

### ✨ 主要特性

- ✅ **支持 Uptime Kuma 2.x** - 完全兼容最新版本
- ✅ **Bearer Token 认证** - 安全的 API 访问控制
- ✅ **完整的监控数据** - Ping、Uptime、心跳数据
- ✅ **多时间段数据** - 1h, 3h, 6h, 24h, 1周的心跳数据
- ✅ **Docker 一键部署** - 自动安装、配置、启动
- ✅ **健康检查** - 自动重启和状态监控
- ✅ **冷门端口** - 使用 58273 端口提高安全性

### 📦 API 端点

#### 1. 系统信息
```
GET /api/info
```
获取 Uptime Kuma 版本、数据库类型等信息。

#### 2. 监控器性能数据
```
GET /api/monitors/<id>/performance
```
获取完整的监控器数据，包括：
- 当前 Ping 和 24 小时平均 Ping
- 24小时、30天、1年在线率
- 5 个时间段的心跳数据
- 状态竖条图数据

### 🚀 快速开始

#### 一键部署

```bash
wget https://github.com/beiaduo/uptime-kuma-api/releases/download/uptimekuma/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动：
1. 检查并安装 Docker 和 docker-compose
2. 克隆代码到 `/opt/uptime-kuma-rest-api`
3. 配置环境变量（自动生成随机 Token）
4. 启动服务
5. 测试 API 连接

#### 手动部署

```bash
git clone https://github.com/beiaduo/uptime-kuma-api.git
cd uptime-kuma-api
cp .env.example .env
nano .env  # 配置 Uptime Kuma 地址和凭据
docker-compose up -d
```

### 📝 配置说明

需要在 `.env` 文件中配置以下参数：

```bash
UPTIME_KUMA_URL=http://your-uptimekuma-server:3001
UPTIME_KUMA_USERNAME=your-username
UPTIME_KUMA_PASSWORD=your-password
API_TOKEN=your-random-token
```

### 🔒 安全特性

- **Bearer Token 认证** - 所有 API 端点都需要认证
- **冷门端口 58273** - 减少被扫描的风险
- **自动生成 Token** - 部署时自动生成强随机 Token
- **环境变量配置** - 敏感信息不写入代码

### 📚 文档

- [README.md](README.md) - 快速开始和基本使用
- [USAGE.md](USAGE.md) - 详细的 API 使用指南
- [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - Docker 部署详细指南
- [DEPLOY.md](DEPLOY.md) - 完整部署指南（systemd/nginx/docker）

### 🛠️ 技术栈

- Python 3.11
- Flask 2.0+ (REST API 框架)
- Flask-CORS (跨域支持)
- python-socketio[client] 5.9+ (Socket.IO 客户端)
- Docker & docker-compose (容器化部署)

### 📊 数据格式

#### 响应示例

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

### 🔄 数据转换

从 Uptime Kuma 原始 API 到 REST API 的转换：

| 数据类型 | 原始格式 | REST API 格式 | 说明 |
|---------|---------|--------------|------|
| Uptime | 0-1 的小数 | 0-100 的百分比 | 乘以 100 |
| Status | 枚举对象 | 数字 (1/0) | .value 属性 |
| Heartbeats | 包含所有字段 | 精简必要字段 | 移除冗余字段 |
| Uptime Bars | - | 新增简化数组 | 只保留 status+time |

### 🌐 使用示例

#### Python
```python
import requests

headers = {"Authorization": "Bearer your-token"}
response = requests.get("http://localhost:58273/api/monitors/1/performance", headers=headers)
print(response.json())
```

#### JavaScript
```javascript
fetch("http://localhost:58273/api/monitors/1/performance", {
  headers: {"Authorization": "Bearer your-token"}
})
  .then(r => r.json())
  .then(data => console.log(data));
```

#### cURL
```bash
curl -H "Authorization: Bearer your-token" \
  http://localhost:58273/api/monitors/1/performance | jq
```

### 🐛 已知问题

无

### 🎯 下一步计划

- [ ] 添加更多 API 端点（列出所有监控器、添加/删除监控器等）
- [ ] 支持 WebSocket 实时推送
- [ ] 添加数据缓存机制
- [ ] 支持更多认证方式（API Key, JWT）
- [ ] 添加速率限制

### 📞 支持

- GitHub Issues: https://github.com/beiaduo/uptime-kuma-api/issues
- 文档: https://github.com/beiaduo/uptime-kuma-api

### 📄 许可证

MIT License

---

**完整更新日志**: https://github.com/beiaduo/uptime-kuma-api/commits/main
