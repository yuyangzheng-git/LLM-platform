#!/bin/bash
# V2 版本 - 文件上传修复一键部署脚本

cd /opt/llm-chat-platform

echo "=========================================="
echo "  文件上传修复 V2 部署"
echo "=========================================="
echo ""

# 解压文件
echo "📦 1/4 解压更新包..."
tar xzf llm-chat-upload-fix-v2.tar.gz
echo "✅ 文件已解压"
echo ""

# 重新构建后端
echo "🔨 2/4 重新构建后端镜像..."
docker compose -f docker-compose.final.yml build backend
echo "✅ 镜像构建完成"
echo ""

# 重启服务
echo "🔄 3/4 重启服务..."
docker compose -f docker-compose.final.yml restart backend
docker compose -f docker-compose.final.yml restart nginx
echo "✅ 服务已重启"
echo ""

# 检查状态
echo "🔍 4/4 检查服务状态..."
docker compose -f docker-compose.final.yml ps
echo ""

echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📝 V2 版本改进："
echo "  • 基于文件扩展名验证（更宽松）"
echo "  • 支持 application/octet-stream"
echo "  • 添加详细日志记录"
echo ""
echo "🧪 测试建议："
echo "  1. 上传一个 .docx 文件"
echo "  2. 上传一个 .xlsx 文件"
echo "  3. 检查日志: docker logs llm-chat-backend --tail 30"
echo ""
echo "🔍 如果还有问题，请查看详细日志："
echo "  docker logs llm-chat-backend | grep '📁 上传文件'"
echo ""
