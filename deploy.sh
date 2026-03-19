#!/bin/bash

# 生产环境部署脚本
# 部署到 your-server-ip:3212

set -e

# 配置
SERVER_IP="your-server-ip"
SERVER_USER="ubuntu"
SERVER_PASSWORD="your_password"
DEPLOY_DIR="/opt/llm-chat-platform"
PROJECT_NAME="llm-chat-platform"

echo "========================================"
echo "LLM Chat Platform 生产环境部署"
echo "========================================"
echo "服务器: $SERVER_IP"
echo "端口: 3212"
echo "========================================"

# 1. 打包项目
echo ""
echo "[1/6] 打包项目文件..."
tar czf ${PROJECT_NAME}-deploy.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='backend/data' \
  --exclude='backend/uploads' \
  --exclude='backend/logs' \
  --exclude='frontend/dist' \
  --exclude='frontend/node_modules' \
  --exclude='.git' \
  --exclude='*.md' \
  --exclude='*.tar.gz' \
  backend/ \
  frontend/ \
  nginx/ \
  docker-compose.prod.yml \
  .env.production \
  .dockerignore

echo "✓ 项目打包完成: ${PROJECT_NAME}-deploy.tar.gz"

# 2. 传输到服务器
echo ""
echo "[2/6] 传输文件到服务器..."
sshpass -p "$SERVER_PASSWORD" scp ${PROJECT_NAME}-deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

echo "✓ 文件传输完成"

# 3. 在服务器上执行部署
echo ""
echo "[3/6] 在服务器上准备环境..."
sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

# 创建部署目录
sudo mkdir -p /opt/llm-chat-platform
sudo chown ubuntu:ubuntu /opt/llm-chat-platform
cd /opt/llm-chat-platform

# 解压项目
tar xzf /tmp/llm-chat-platform-deploy.tar.gz

# 复制生产环境配置
cp .env.production backend/.env

# 创建必要的目录
mkdir -p backend/data backend/uploads backend/logs nginx/ssl

echo "✓ 环境准备完成"
ENDSSH

# 4. 检查 Docker
echo ""
echo "[4/6] 检查 Docker 环境..."
sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
if ! command -v docker &> /dev/null; then
    echo "⚠ Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    echo "✓ Docker 安装完成"
else
    echo "✓ Docker 已安装"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "⚠ Docker Compose 未安装，正在安装..."
    sudo apt update
    sudo apt install -y docker-compose-plugin
    echo "✓ Docker Compose 安装完成"
else
    echo "✓ Docker Compose 已安装"
fi
ENDSSH

# 5. 构建和启动容器
echo ""
echo "[5/6] 构建和启动服务..."
sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /opt/llm-chat-platform

# 停止旧容器
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 构建镜像
echo "正在构建 Docker 镜像..."
docker-compose -f docker-compose.prod.yml build

# 启动服务
echo "正在启动服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

echo "✓ 服务启动完成"
ENDSSH

# 6. 健康检查
echo ""
echo "[6/6] 健康检查..."
sleep 5

if curl -f http://${SERVER_IP}:3212/health &> /dev/null; then
    echo "✓ 健康检查通过"
else
    echo "⚠ 健康检查失败，请查看日志"
    sshpass -p "$SERVER_PASSWORD" ssh ${SERVER_USER}@${SERVER_IP} \
      "cd /opt/llm-chat-platform && docker compose -f docker-compose.prod.yml logs --tail 50"
fi

# 清理本地临时文件
rm -f ${PROJECT_NAME}-deploy.tar.gz

echo ""
echo "========================================"
echo "✓ 部署完成！"
echo "========================================"
echo "访问地址: http://${SERVER_IP}:3212"
echo "API 文档: http://${SERVER_IP}:3212/docs"
echo "健康检查: http://${SERVER_IP}:3212/health"
echo ""
echo "查看日志: ssh ${SERVER_USER}@${SERVER_IP} 'cd /opt/llm-chat-platform && docker-compose -f docker-compose.prod.yml logs -f'"
echo "========================================"
