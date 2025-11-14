# Debian 部署指南

## 方式一：使用 systemd 服务（推荐）

### 1. 上传项目到服务器 

```bash
# 在本地打包
cd /Users/jason/PycharmProjects/uptime-kuma-api
tar -czf uptime-kuma-rest-api.tar.gz rest_api_server.py 安装.sh 启动REST_API.sh README.md

# 上传到服务器
scp uptime-kuma-rest-api.tar.gz user@your-server:/opt/

# SSH 到服务器
ssh user@your-server
```

### 2. 在服务器上解压并安装

```bash
cd /opt
sudo tar -xzf uptime-kuma-rest-api.tar.gz
sudo mkdir -p /opt/uptime-kuma-rest-api
sudo mv rest_api_server.py 安装.sh 启动REST_API.sh README.md /opt/uptime-kuma-rest-api/
cd /opt/uptime-kuma-rest-api

# 安装 Python 和依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 运行安装脚本
bash 安装.sh
```

### 3. 配置环境变量

```bash
# 创建配置文件
sudo nano /opt/uptime-kuma-rest-api/.env
```

填入以下内容（修改为你的实际值）：

```bash
UPTIME_KUMA_URL=http://your-uptimekuma-server:3001
UPTIME_KUMA_USERNAME=www.vircs.com
UPTIME_KUMA_PASSWORD=www.vircs.com
API_TOKEN=your-generated-random-token-here
```

生成随机 Token：
```bash
openssl rand -hex 32
```

### 4. 创建 systemd 服务

```bash
sudo nano /etc/systemd/system/uptime-kuma-rest-api.service
```

填入以下内容：

```ini
[Unit]
Description=Uptime Kuma REST API Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/uptime-kuma-rest-api
Environment="PATH=/opt/uptime-kuma-rest-api/.venv/bin"
EnvironmentFile=/opt/uptime-kuma-rest-api/.env
ExecStart=/opt/uptime-kuma-rest-api/.venv/bin/python /opt/uptime-kuma-rest-api/rest_api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5. 启动服务

```bash
# 修改文件权限
sudo chown -R www-data:www-data /opt/uptime-kuma-rest-api

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start uptime-kuma-rest-api

# 查看状态
sudo systemctl status uptime-kuma-rest-api

# 设置开机自启
sudo systemctl enable uptime-kuma-rest-api
```

### 6. 查看日志

```bash
# 实时查看日志
sudo journalctl -u uptime-kuma-rest-api -f

# 查看最近 100 行
sudo journalctl -u uptime-kuma-rest-api -n 100
```

### 7. 测试 API

```bash
# 在服务器上测试
curl -H "Authorization: Bearer your-api-token" http://localhost:58273/api/info

# 从外部测试（需要配置防火墙）
curl -H "Authorization: Bearer your-api-token" http://your-server-ip:58273/api/info
```

---

## 方式二：使用 Nginx 反向代理（推荐用于生产环境）

### 1. 安装 Nginx

```bash
sudo apt install -y nginx
```

### 2. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/uptime-kuma-rest-api
```

填入以下内容：

```nginx
server {
    listen 80;
    server_name api.your-domain.com;  # 修改为你的域名

    location / {
        proxy_pass http://127.0.0.1:58273;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 启用站点

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/uptime-kuma-rest-api /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4. （可选）配置 SSL

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d api.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 方式三：使用 Docker（最简单）

### 1. 创建 Dockerfile

```bash
cd /opt/uptime-kuma-rest-api
sudo nano Dockerfile
```

填入以下内容：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
RUN pip install flask flask-cors && \
    pip install git+https://github.com/markus-seidl/uptime-kuma-api.git@feature/upgrade-to-2

# 复制文件
COPY rest_api_server.py .

# 暴露端口
EXPOSE 58273

# 启动命令
CMD ["python", "rest_api_server.py"]
```

### 2. 构建并运行

```bash
# 构建镜像
sudo docker build -t uptime-kuma-rest-api .

# 运行容器
sudo docker run -d \
  --name uptime-kuma-rest-api \
  --restart always \
  -p 58273:58273 \
  -e UPTIME_KUMA_URL="http://your-uptimekuma-server:3001" \
  -e UPTIME_KUMA_USERNAME="www.vircs.com" \
  -e UPTIME_KUMA_PASSWORD="www.vircs.com" \
  -e API_TOKEN="your-generated-token" \
  uptime-kuma-rest-api

# 查看日志
sudo docker logs -f uptime-kuma-rest-api
```

---

## 防火墙配置

### 使用 ufw

```bash
# 允许 58273 端口
sudo ufw allow 58273/tcp

# 或者只允许特定 IP
sudo ufw allow from 192.168.1.0/24 to any port 58273

# 查看状态
sudo ufw status
```

### 使用 iptables

```bash
# 允许 58273 端口
sudo iptables -A INPUT -p tcp --dport 58273 -j ACCEPT

# 保存规则
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## 常用管理命令

```bash
# systemd 服务管理
sudo systemctl start uptime-kuma-rest-api    # 启动
sudo systemctl stop uptime-kuma-rest-api     # 停止
sudo systemctl restart uptime-kuma-rest-api  # 重启
sudo systemctl status uptime-kuma-rest-api   # 状态

# Docker 管理
sudo docker start uptime-kuma-rest-api       # 启动
sudo docker stop uptime-kuma-rest-api        # 停止
sudo docker restart uptime-kuma-rest-api     # 重启
sudo docker logs uptime-kuma-rest-api        # 日志
```

---

## 安全建议

1. **不要使用默认 Token** - 一定要生成随机 Token
2. **使用 HTTPS** - 通过 Nginx + SSL 加密传输
3. **限制访问 IP** - 通过防火墙只允许特定 IP 访问
4. **定期更新** - 及时更新 Python 依赖包
5. **监控日志** - 定期检查 systemd 或 Docker 日志

---

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
sudo journalctl -u uptime-kuma-rest-api -n 100 --no-pager

# 检查端口占用
sudo netstat -tulpn | grep 58273

# 手动测试
cd /opt/uptime-kuma-rest-api
source .venv/bin/activate
python rest_api_server.py
```

### 无法连接到 Uptime Kuma

```bash
# 测试网络连接
curl http://your-uptimekuma-server:3001

# 检查环境变量
sudo systemctl show uptime-kuma-rest-api -p Environment
```

### 权限问题

```bash
# 确保 www-data 用户有权限
sudo chown -R www-data:www-data /opt/uptime-kuma-rest-api
sudo chmod -R 755 /opt/uptime-kuma-rest-api
```
