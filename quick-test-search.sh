#!/bin/bash

# 快速测试搜索功能
# 使用方法: ./quick-test-search.sh

echo "🔍 测试DuckDuckGo搜索功能"
echo "================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3未安装"
    exit 1
fi

echo "✅ Python已安装"

# 进入后端目录
cd backend

echo ""
echo "📦 安装依赖..."
pip3 install beautifulsoup4 lxml httpx -q

echo ""
echo "🚀 运行搜索测试..."
echo "================================"
echo ""

python3 test_search.py

echo ""
echo "================================"
echo "✅ 测试完成!"
echo ""
echo "💡 下一步:"
echo "  1. 启动完整应用: cd .. && ./start-with-search.sh"
echo "  2. 访问: http://localhost:3212"
echo "  3. 测试搜索: '今天有什么AI新闻?'"
echo ""
