# Uptime Kuma REST API

将 Uptime Kuma Socket.IO API 封装成 REST API，通过 HTTP 获取监控数据。

## 快速安装

### Docker 部署

```bash
# 1. 克隆代码
git clone https://github.com/yourusername/uptime-kuma-api.git
cd uptime-kuma-api

# 2. 配置
docker run --rm -it -v $(pwd):/app python:3.11-slim python /app/rest_api_server.py --setup

# 3. 启动
docker-compose up -d

# 4. 查看配置
cat api_config.json
```

配置向导会询问：
- Uptime Kuma URL（例如：https://status.example.com）
- 用户名和密码
- API 端口（可选随机生成，推荐）
- API Token（可选随机生成，推荐）

## API 使用

### 端点

```
GET /api/monitors/<id>
```

### 示例

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:YOUR_PORT/api/monitors/1
```

### 返回数据

```json
{
  "success": true,                    // 请求是否成功
  "info": {                           // Uptime Kuma 系统信息
    "version": "2.0.2",               // 版本号
    "primaryBaseURL": "xxxxxx"  // ⚠️ 域名（建议隐藏）
  },
  "name": "xxxxxx",        // ⚠️ 监控器名称（隐藏）
  "stats": {                          // 统计数据
    "current_ping": 16.70,            // 当前 Ping 值（毫秒）
    "avg_ping": 16.42,                // 24小时平均 Ping 值（毫秒）
    "uptime_one_day": 100.00,         // 在线率，24小时（百分比，保留2位小数）
    "uptime_one_month": 99.97,        // 在线率，30天（百分比，保留2位小数）
    "uptime_one_year": 99.97          // 在线率，1年（百分比，保留2位小数）
  },
  "chart": {                          // 图表数据，包含 ping、status、time
    "one_hour": [                     // 最近1小时的心跳数据
      {
        "ping": 16.7,                 // 响应时间（毫秒）
        "status": 1,                  // 状态（1=在线, 0=离线）
        "time": "2025-11-14 05:33:14.496"  // 时间戳
      }
    ],
    "three_hours": [...],             // 最近3小时的心跳数据
    "six_hours": [...],               // 最近6小时的心跳数据
    "one_day": [...],                 // 最近24小时的心跳数据
    "one_week": [...],                // 最近1周的心跳数据
    "one_month": [...]                // 最近1个月的心跳数据
  },
  "bar": [                            // 状态条数据，最近1小时（仅 status、time）
    {
      "status": 1,                    // 状态（1=在线, 0=离线）
      "time": "2025-11-14 05:33:14.496"
    }
  ]
}
```

**字段说明**:
- `stats`: 所有数值保留2位小数，uptime 为百分比格式
- `chart`: 每条记录包含 `ping`(毫秒)、`status`(1=在线/0=离线)、`time`(时间戳)
  - **智能降采样**: 每个时间范围独立判断，超过 500 个点时自动按时间均匀采样，否则返回全部数据
  - 保证图表渲染性能的同时，短时间范围保留完整细节
- `bar`: 简化版数据，仅包含 `status` 和 `time`，用于绘制状态条（同样应用降采样规则）

**⚠️ 隐私提醒**: `info.primaryBaseURL` 和 `name` 字段可能包含敏感信息（域名、IP地址），公开展示前建议进行处理。参考下方"数据隐私"章节。

## 管理

### 查看配置

```bash
cat api_config.json
```

### 修改配置

```bash
docker run --rm -it -v $(pwd):/app python:3.11-slim python /app/rest_api_server.py --config
docker-compose restart
```

可以修改任意配置项：
- 留空保持不变
- 输入 `random` 重新生成随机端口/Token

### 查看日志

```bash
docker-compose logs -f
```

### 重启服务

```bash
docker-compose restart
```

### 更新代码

```bash
git pull
docker-compose up -d --build
```

## 使用示例

### Python

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("http://localhost:PORT/api/monitors/1", headers=headers)
data = response.json()

print(f"监控器: {data['name']}")
print(f"当前 Ping: {data['stats']['current_ping']} ms")
print(f"24小时在线率: {data['stats']['uptime_one_day']}%")
```

### JavaScript

```javascript
fetch("http://localhost:PORT/api/monitors/1", {
  headers: {"Authorization": "Bearer YOUR_TOKEN"}
})
  .then(r => r.json())
  .then(data => {
    console.log("监控器:", data.name);
    console.log("当前 Ping:", data.stats.current_ping, "ms");
    console.log("24小时在线率:", data.stats.uptime_one_day, "%");
  });
```

## 安全特性

- ✅ **配置文件存储** - 所有敏感信息存储在 `api_config.json`（已加入 .gitignore）
- ✅ **Bearer Token 认证** - 所有 API 都需要认证
- ✅ **随机端口/Token** - 安装时可自动生成
- ✅ **无信息泄露** - 未认证访问返回 404
- ✅ **纯净源码** - Python 代码中不包含任何敏感信息

## 数据隐私

**需要隐藏的字段**：
- `info.primaryBaseURL` - 域名
- `name` - 可能包含 IP 或主机名

**处理示例**（Python）：
```python
import re
data['info']['primaryBaseURL'] = 'https://status.example.com'
data['name'] = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'x.x.x.x', data['name'])
```

**处理示例**（JavaScript）：
```javascript
data.info.primaryBaseURL = 'https://status.example.com'
data.name = data.name.replace(/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/g, 'x.x.x.x')
```

## 技术栈

- Python 3.11
- Flask (REST API 框架)
- Socket.IO (与 Uptime Kuma 通信)
- Docker (容器化部署)

## 许可证

MIT
