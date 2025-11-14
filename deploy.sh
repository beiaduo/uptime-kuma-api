#!/bin/bash
set -e

# =============================================================================
# Uptime Kuma REST API - 一键部署脚本
# =============================================================================
#
# 使用方法:
#   bash <(curl -s https://raw.githubusercontent.com/你的用户名/项目名/master/deploy.sh)
#
# 或者下载后运行:
#   wget https://raw.githubusercontent.com/你的用户名/项目名/master/deploy.sh
#   chmod +x deploy.sh
#   ./deploy.sh
#
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
INSTALL_DIR="/opt/uptime-kuma-rest-api"
GITHUB_REPO="CHANGE_ME"  # ⚠️ 请在上传到 GitHub 后修改为你的仓库地址，例如: https://github.com/username/repo.git

# 打印函数
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# 1. 检查依赖
# =============================================================================
print_step "检查系统依赖..."

if ! command_exists docker; then
    print_error "未检测到 Docker，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    print_success "Docker 安装完成"
else
    print_success "Docker 已安装"
fi

if ! command_exists docker-compose; then
    print_error "未检测到 docker-compose，正在安装..."
    if command_exists apt-get; then
        apt-get update
        apt-get install -y docker-compose
    elif command_exists yum; then
        yum install -y docker-compose
    else
        # 手动安装
        curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    print_success "docker-compose 安装完成"
else
    print_success "docker-compose 已安装"
fi

# =============================================================================
# 2. 克隆或更新代码
# =============================================================================
print_step "获取最新代码..."

if [ -d "$INSTALL_DIR/.git" ]; then
    print_warning "检测到已存在的安装，正在更新..."
    cd "$INSTALL_DIR"
    git pull
    print_success "代码更新完成"
else
    print_step "克隆代码仓库..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_success "代码克隆完成"
fi

# =============================================================================
# 3. 配置环境变量
# =============================================================================
print_step "配置环境变量..."

if [ -f "$INSTALL_DIR/.env" ]; then
    print_warning "检测到已有配置文件 .env"
    read -p "是否覆盖现有配置? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "跳过配置，使用现有 .env 文件"
        SKIP_CONFIG=1
    fi
fi

if [ -z "$SKIP_CONFIG" ]; then
    echo ""
    echo "请输入配置信息："
    echo "==============================================="

    # Uptime Kuma URL
    read -p "Uptime Kuma 服务器地址 (例: http://192.168.1.100:3001): " KUMA_URL

    # Username
    read -p "Uptime Kuma 用户名: " KUMA_USER

    # Password (隐藏输入)
    read -s -p "Uptime Kuma 密码: " KUMA_PASS
    echo

    # API Token
    echo ""
    print_step "生成 API Token..."
    if command_exists openssl; then
        API_TOKEN=$(openssl rand -hex 32)
        print_success "已自动生成随机 Token"
    else
        read -p "请输入 API Token (或按回车自动生成): " API_TOKEN
        if [ -z "$API_TOKEN" ]; then
            API_TOKEN=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
            print_success "已自动生成 Token"
        fi
    fi

    # 写入 .env 文件
    cat > "$INSTALL_DIR/.env" <<EOF
# Uptime Kuma 服务器配置
UPTIME_KUMA_URL=$KUMA_URL
UPTIME_KUMA_USERNAME=$KUMA_USER
UPTIME_KUMA_PASSWORD=$KUMA_PASS

# REST API 认证 Token
API_TOKEN=$API_TOKEN
EOF

    chmod 600 "$INSTALL_DIR/.env"
    print_success "配置文件已创建: $INSTALL_DIR/.env"

    echo ""
    echo "==============================================="
    echo -e "${GREEN}重要！请保存以下 API Token：${NC}"
    echo -e "${YELLOW}$API_TOKEN${NC}"
    echo "==============================================="
    echo ""
fi

# =============================================================================
# 4. 启动服务
# =============================================================================
print_step "启动 Docker 容器..."

cd "$INSTALL_DIR"

# 停止旧容器（如果存在）
if docker ps -a | grep -q uptime-kuma-rest-api; then
    print_warning "停止并删除旧容器..."
    docker-compose down
fi

# 构建并启动
docker-compose up -d --build

print_success "服务启动成功！"

# =============================================================================
# 5. 等待服务就绪
# =============================================================================
print_step "等待服务启动..."

for i in {1..30}; do
    if curl -s http://localhost:58273/ > /dev/null 2>&1; then
        print_success "服务已就绪！"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        print_error "服务启动超时，请检查日志: docker-compose logs"
        exit 1
    fi
done

# =============================================================================
# 6. 测试 API
# =============================================================================
print_step "测试 API 连接..."

# 读取 Token
source "$INSTALL_DIR/.env"

# 测试 info 接口
if curl -s -H "Authorization: Bearer $API_TOKEN" http://localhost:58273/api/info | grep -q "success"; then
    print_success "API 测试通过！"
else
    print_warning "API 测试失败，请检查配置和日志"
fi

# =============================================================================
# 7. 显示结果
# =============================================================================
echo ""
echo "==============================================="
echo -e "${GREEN}部署完成！${NC}"
echo "==============================================="
echo ""
echo "服务信息："
echo "  - 安装目录: $INSTALL_DIR"
echo "  - 监听端口: 58273"
echo "  - API Token: $API_TOKEN"
echo ""
echo "可用端点："
echo "  - GET  http://localhost:58273/api/info"
echo "  - GET  http://localhost:58273/api/monitors/<id>/performance"
echo ""
echo "测试命令："
echo "  curl -H 'Authorization: Bearer $API_TOKEN' http://localhost:58273/api/info"
echo ""
echo "管理命令："
echo "  - 查看日志: cd $INSTALL_DIR && docker-compose logs -f"
echo "  - 停止服务: cd $INSTALL_DIR && docker-compose down"
echo "  - 重启服务: cd $INSTALL_DIR && docker-compose restart"
echo "  - 更新代码: cd $INSTALL_DIR && git pull && docker-compose up -d --build"
echo ""
echo "配置文件："
echo "  - 环境变量: $INSTALL_DIR/.env"
echo ""
echo "==============================================="

# 询问是否查看日志
read -p "是否查看实时日志? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi
