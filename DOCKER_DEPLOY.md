# Docker 部署指南（超简单）

## 方式一：直接在服务器构建（推荐）

### 1. 上传文件到服务器

```bash
# 在本地打包需要的文件
cd /Users/jason/PycharmProjects/uptime-kuma-api
tar -czf uptime-kuma-rest-api.tar.gz \
  Dockerfile \
  docker-compose.yml \
  .env.example \
  rest_api_server.py \
  README.md

# 上传到服务器
scp uptime-kuma-rest-api.tar.gz user@your-debian-server:/opt/
```

### 2. 在服务器上部署

```bash
# SSH 到服务器
ssh user@your-debian-server

# 解压文件
cd /opt
tar -xzf uptime-kuma-rest-api.tar.gz
cd uptime-kuma-rest-api  # 或者你解压后的目录名

# 复制并编辑配置文件
cp .env.example .env
nano .env
```

编辑 `.env` 文件，修改为你的实际配置：

```bash
UPTIME_KUMA_URL=http://your-uptime-kuma-server:3001
UPTIME_KUMA_USERNAME=www.vircs.com
UPTIME_KUMA_PASSWORD=www.vircs.com
API_TOKEN=请生成随机token
```

生成随机 Token：
```bash
openssl rand -hex 32
```

### 3. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 测试
curl -H "Authorization: Bearer your-token" http://localhost:58273/api/info
```

---

## 方式二：使用预构建镜像（如果推送到 Docker Hub）

### 1. 在本地构建并推送镜像

```bash
# 构建镜像
cd /Users/jason/PycharmProjects/uptime-kuma-api
docker build -t your-dockerhub-username/uptime-kuma-rest-api:latest .

# 推送到 Docker Hub
docker login
docker push your-dockerhub-username/uptime-kuma-rest-api:latest
```

### 2. 在服务器上直接运行

```bash
# 在服务器上直接运行
docker run -d \
  --name uptime-kuma-rest-api \
  --restart always \
  -p 58273:58273 \
  -e UPTIME_KUMA_URL="http://your-server:3001" \
  -e UPTIME_KUMA_USERNAME="www.vircs.com" \
  -e UPTIME_KUMA_PASSWORD="www.vircs.com" \
  -e API_TOKEN="your-random-token" \
  your-dockerhub-username/uptime-kuma-rest-api:latest
```

---

## 常用管理命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志（实时）
docker-compose logs -f

# 查看日志（最近100行）
docker-compose logs --tail=100

# 查看容器状态
docker-compose ps

# 进入容器
docker-compose exec uptime-kuma-rest-api bash

# 重新构建镜像
docker-compose build --no-cache

# 更新并重启
docker-compose pull
docker-compose up -d
```

---

## 测试 API

```bash
# 设置 Token
TOKEN="your-api-token"

# 测试系统信息
curl -H "Authorization: Bearer $TOKEN" http://localhost:58273/api/info | jq

# 测试性能数据
curl -H "Authorization: Bearer $TOKEN" http://localhost:58273/api/monitors/1/performance | jq
```

---

## 配置反向代理（可选）

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://localhost:58273;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用 Traefik（docker-compose）

```yaml
version: '3.8'

services:
  uptime-kuma-rest-api:
    build: .
    container_name: uptime-kuma-rest-api
    restart: always
    environment:
      - UPTIME_KUMA_URL=${UPTIME_KUMA_URL}
      - UPTIME_KUMA_USERNAME=${UPTIME_KUMA_USERNAME}
      - UPTIME_KUMA_PASSWORD=${UPTIME_KUMA_PASSWORD}
      - API_TOKEN=${API_TOKEN}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.uptime-api.rule=Host(`api.your-domain.com`)"
      - "traefik.http.services.uptime-api.loadbalancer.server.port=58273"
    networks:
      - traefik

networks:
  traefik:
    external: true
```

---

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs

# 检查配置文件
cat .env

# 手动测试连接 Uptime Kuma
curl http://your-uptime-kuma-server:3001
```

### 无法访问 API

```bash
# 检查端口占用
netstat -tulpn | grep 58273

# 检查防火墙
sudo ufw status
sudo ufw allow 58273/tcp

# 检查容器状态
docker ps
docker-compose ps
```

### 更新代码后重新部署

```bash
# 停止并删除容器
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 启动新容器
docker-compose up -d

# 查看日志确认
docker-compose logs -f
```

---

## 安全建议

1. **不要使用默认 Token** - 必须生成随机 Token
2. **限制访问** - 使用防火墙或反向代理限制访问
3. **使用 HTTPS** - 通过 Nginx/Traefik 配置 SSL
4. **定期更新** - 定期重新构建镜像以获取最新依赖
5. **监控日志** - 定期检查 `docker-compose logs`

---

## 完整部署示例

```bash
# 1. 在服务器上创建目录
mkdir -p /opt/uptime-kuma-rest-api
cd /opt/uptime-kuma-rest-api

# 2. 上传文件（从本地）
# 见上面的 tar + scp 命令

# 3. 配置环境变量
cp .env.example .env
nano .env
# 填入你的配置

# 4. 启动
docker-compose up -d

# 5. 查看日志确认
docker-compose logs -f

# 6. 测试
TOKEN="your-token"
curl -H "Authorization: Bearer $TOKEN" http://localhost:58273/api/info

# 完成！
```
