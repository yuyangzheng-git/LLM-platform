#!/bin/bash

# 服务健康检查脚本
# 使用方法: ./check-services.sh

set -e

echo "========================================="
echo "  LLM Chat Platform 服务健康检查"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker
echo "📦 检查Docker状态..."
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker未运行${NC}"
    echo "   请启动Docker Desktop后重试"
    echo ""
    echo "   macOS: open -a Docker"
    echo "   等待30秒后重新运行此脚本"
    exit 1
else
    echo -e "${GREEN}✅ Docker: 运行中${NC}"
fi

echo ""
echo "🐳 检查Docker容器..."

# 检查容器状态
if docker-compose ps &> /dev/null; then
    docker-compose ps
else
    echo -e "${YELLOW}⚠️  无法连接到docker-compose服务${NC}"
fi

echo ""
echo "🔍 检查各服务健康状态..."

# 检查SearxNG
echo -n "SearxNG (搜索引擎): "
if curl -s http://localhost:8888/healthz &> /dev/null; then
    echo -e "${GREEN}✅ 运行中${NC}"

    # 测试搜索功能
    echo -n "  搜索功能测试: "
    if curl -s "http://localhost:8888/search?q=test&format=json" | grep -q "results"; then
        echo -e "${GREEN}✅ 正常${NC}"
    else
        echo -e "${YELLOW}⚠️  API响应异常${NC}"
    fi
else
    echo -e "${RED}❌ 未运行或不健康${NC}"
    echo "  排查: docker-compose logs searxng"
    echo "  修复: docker-compose restart searxng"
fi

# 检查后端
echo -n "后端API: "
if curl -s http://localhost:3211/health &> /dev/null; then
    echo -e "${GREEN}✅ 运行中${NC}"

    # 检查健康详情
    HEALTH=$(curl -s http://localhost:3211/health)
    VERSION=$(echo $HEALTH | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$VERSION" ]; then
        echo "  版本: $VERSION"
    fi
else
    echo -e "${RED}❌ 未运行${NC}"
    echo "  排查: docker-compose logs backend"
    echo "  修复: docker-compose restart backend"
fi

# 检查前端
echo -n "前端应用: "
if curl -s http://localhost:3212 &> /dev/null; then
    echo -e "${GREEN}✅ 运行中${NC}"
else
    echo -e "${RED}❌ 未运行${NC}"
    echo "  排查: docker-compose logs frontend"
    echo "  修复: docker-compose restart frontend"
fi

echo ""
echo "🔌 检查端口占用..."

check_port() {
    local port=$1
    local service=$2
    echo -n "端口 $port ($service): "
    if lsof -i :$port &> /dev/null; then
        echo -e "${GREEN}已占用${NC}"
    else
        echo -e "${YELLOW}未占用${NC}"
    fi
}

check_port 8888 "SearxNG"
check_port 3211 "后端API"
check_port 3212 "前端"

echo ""
echo "========================================="
echo "  检查完成"
echo "========================================="
echo ""

# 提供快速修复建议
echo "💡 快速操作:"
echo "  查看所有日志: docker-compose logs"
echo "  重启所有服务: docker-compose restart"
echo "  停止所有服务: docker-compose down"
echo "  启动所有服务: docker-compose up -d"
echo ""

# 提供访问链接
echo "🌐 访问链接:"
echo "  前端应用: http://localhost:3212"
echo "  后端API文档: http://localhost:3211/docs"
echo "  SearxNG搜索: http://localhost:8888"
echo ""

# 工具测试建议
echo "🧪 测试建议:"
echo "  搜索测试: '今天有什么AI新闻?'"
echo "  时间测试: '现在几点了?'"
echo "  地址测试: '北京在哪里?'"
echo ""
