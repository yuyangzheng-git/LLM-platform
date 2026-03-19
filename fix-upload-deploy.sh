#!/bin/bash
# 文件上传修复 - 部署脚本
# 此脚本修复了文件上传失败的问题

set -e

echo "======================================"
echo "文件上传修复 - 部署到生产服务器"
echo "======================================"

SERVER="ubuntu@your-server-ip"
REMOTE_DIR="/opt/llm-chat-platform"
PACKAGE="llm-chat-upload-fix.tar.gz"

echo ""
echo "📦 修复内容："
echo "  1. 扩展支持的文件类型：DOC, DOCX, XLS, XLSX, PPT, PPTX, CSV 等"
echo "  2. 增加文件大小限制到 100MB"
echo "  3. 改进错误提示信息（中文）"
echo "  4. 批量上传失败时显示详细错误"
echo ""

# 检查包是否存在
if [ ! -f "$PACKAGE" ]; then
    echo "❌ 错误: $PACKAGE 不存在"
    exit 1
fi

echo "🚀 步骤 1/4: 传输文件到服务器..."
scp "$PACKAGE" "$SERVER:$REMOTE_DIR/"

echo ""
echo "🚀 步骤 2/4: 解压并覆盖文件..."
ssh "$SERVER" << 'EOF'
cd /opt/llm-chat-platform
tar xzf llm-chat-upload-fix.tar.gz
echo "✅ 文件已更新"
EOF

echo ""
echo "🚀 步骤 3/4: 重新构建后端镜像..."
ssh "$SERVER" << 'EOF'
cd /opt/llm-chat-platform
docker compose -f docker-compose.final.yml build backend
echo "✅ 后端镜像已重建"
EOF

echo ""
echo "🚀 步骤 4/4: 重启服务..."
ssh "$SERVER" << 'EOF'
cd /opt/llm-chat-platform
docker compose -f docker-compose.final.yml restart backend
docker compose -f docker-compose.final.yml restart nginx
echo "✅ 服务已重启"
EOF

echo ""
echo "======================================"
echo "✅ 部署完成！"
echo "======================================"
echo ""
echo "📝 现在支持的文件类型："
echo "  • 图片: PNG, JPEG, GIF, WebP, BMP, SVG"
echo "  • 文档: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX"
echo "  • 文本: TXT, MD, CSV, HTML, JSON, XML"
echo ""
echo "📏 文件大小限制: 100MB"
echo ""
echo "🧪 测试建议："
echo "  1. 尝试上传 Word 文档 (.docx)"
echo "  2. 尝试上传 Excel 表格 (.xlsx)"
echo "  3. 尝试上传大文件（50-100MB）"
echo "  4. 检查错误提示是否清晰"
echo ""
echo "🔍 查看日志："
echo "  docker logs llm-chat-backend --tail 50"
echo ""
