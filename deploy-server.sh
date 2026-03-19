#!/bin/bash

# LLM Chat Platform - 服务器端部署脚本

set -e

echo "========================================="
echo "LLM Chat Platform - 服务器部署"
echo "========================================="

# 检查当前目录
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 创建必要的目录
echo "创建目录结构..."
mkdir -p backend/data backend/uploads backend/logs

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo "错误: backend/.env 文件不存在"
    echo "请从 backend/.env.example 复制并配置"
    exit 1
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker 已安装，请重新登录后再次运行此脚本"
    exit 0
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "安装 Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 停止旧容器
echo "停止现有容器..."
docker-compose down 2>/dev/null || true

# 构建并启动
echo "构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 健康检查
echo "执行健康检查..."
if curl -f http://localhost:3211/health > /dev/null 2>&1; then
    echo "✅ 后端健康检查通过"
else
    echo "⚠️  后端健康检查失败"
    echo "查看日志: docker-compose logs backend"
fi

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "访问地址:"
echo "  前端: http://$(hostname -I | awk '{print $1}'):3212"
echo "  后端: http://$(hostname -I | awk '{print $1}'):3211"
echo "  文档: http://$(hostname -I | awk '{print $1}'):3211/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  重启服务: docker-compose restart"
echo "  停止服务: docker-compose down"
echo ""
echo "========================================="
