#!/bin/bash

# LLM Chat Platform - 实时联网功能启动脚本
# 使用方法: ./start-with-search.sh

set -e

echo "🚀 启动 LLM Chat Platform (带实时搜索功能)"
echo "================================================"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装"
    echo "请先安装Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker未运行"
    echo "请启动Docker Desktop后重试"
    exit 1
fi

echo "✅ Docker检查通过"

# 切换到项目目录
cd "$(dirname "$0")"

echo ""
echo "📦 启动服务..."
echo "- SearxNG (搜索引擎): http://localhost:8888"
echo "- 后端API: http://localhost:3211"
echo "- 前端应用: http://localhost:3212"
echo ""

# 启动Docker服务
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."

# 检查SearxNG
if curl -s http://localhost:8888/healthz &> /dev/null; then
    echo "✅ SearxNG: 运行中"
else
    echo "⚠️  SearxNG: 正在启动..."
fi

# 检查后端
if curl -s http://localhost:3211/health &> /dev/null; then
    echo "✅ 后端API: 运行中"
else
    echo "⚠️  后端API: 正在启动..."
fi

# 检查前端
if curl -s http://localhost:3212 &> /dev/null; then
    echo "✅ 前端应用: 运行中"
else
    echo "⚠️  前端应用: 正在启动..."
fi

echo ""
echo "================================================"
echo "🎉 服务启动完成！"
echo ""
echo "📖 访问应用: http://localhost:3212"
echo "📊 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo ""
echo "💡 测试搜索功能:"
echo "   输入: '今天有什么AI新闻?'"
echo "   应该会看到搜索过程和结果"
echo ""
echo "================================================"
