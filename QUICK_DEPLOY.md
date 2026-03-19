# 文件上传修复 - 快速部署指南（V2）

## ⚡ 一键部署

### 步骤 1: 传输文件

```bash
scp llm-chat-upload-fix-v2.tar.gz ubuntu@your-server-ip:/opt/llm-chat-platform/
```
密码: `your_password`

### 步骤 2: SSH 登录服务器

```bash
ssh ubuntu@your-server-ip
```
密码: `your_password`

### 步骤 3: 执行部署命令（复制粘贴全部）

```bash
cd /opt/llm-chat-platform && \
tar xzf llm-chat-upload-fix-v2.tar.gz && \
docker compose -f docker-compose.final.yml build backend && \
docker compose -f docker-compose.final.yml restart backend nginx && \
echo "✅ 部署完成！" && \
docker compose -f docker-compose.final.yml ps
```

---

## 🔧 V2 版本改进

### 主要变化：
1. ✅ **基于文件扩展名验证**（而不是严格的 MIME 类型）
2. ✅ **支持 application/octet-stream**（通用二进制流）
3. ✅ **添加多种 MIME 类型变体**（兼容不同浏览器）
4. ✅ **详细的上传日志**（记录每个文件的 MIME 类型）

### 现在支持的文件扩展名：
```
.png, .jpg, .jpeg, .gif, .webp, .bmp, .svg
.pdf
.doc, .docx
.xls, .xlsx
.ppt, .pptx
.txt, .md, .csv, .html, .json, .xml
```

### 验证策略（宽松模式）：
- ✅ 只要文件扩展名在支持列表中，就允许上传
- ✅ 忽略浏览器发送的 MIME 类型差异
- ✅ 支持 `application/octet-stream`（Safari/Chrome 常用）

---

## 🧪 测试步骤

### 1. 测试 Word 文档
- 准备一个 `.docx` 文件
- 在聊天界面上传
- ✅ 应该显示进度条并成功上传

### 2. 测试 Excel 表格
- 准备一个 `.xlsx` 文件
- 上传测试
- ✅ 应该成功并显示"已上传"

### 3. 查看详细日志

如果还是失败，执行：
```bash
docker logs llm-chat-backend --tail 50 | grep "上传文件"
```

您会看到类似输出：
```
📁 上传文件: test.docx, MIME类型: application/vnd.openxmlformats-officedocument.wordprocessingml.document
✅ 文件已成功上传
```

或者如果失败：
```
📁 上传文件: test.docx, MIME类型: application/octet-stream
❌ 文件上传失败 - test.docx (类型:application/octet-stream): 文件扩展名 .docx 不支持
```

---

## 📊 故障排查

### 问题 1: 显示"文件类型不支持"

**可能原因**: 旧版本仍在运行

**解决方法**:
```bash
# 强制重建并重启
cd /opt/llm-chat-platform
docker compose -f docker-compose.final.yml down
docker compose -f docker-compose.final.yml up -d --build
```

### 问题 2: 显示"文件扩展名 .docx 不支持"

**可能原因**: 代码未更新

**解决方法**:
```bash
# 检查文件是否已更新
cd /opt/llm-chat-platform
cat backend/app/utils/file_validator.py | grep -A 5 "supported_extensions ="
```

应该看到：
```python
supported_extensions = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
```

### 问题 3: 上传卡住不动

**可能原因**: Nginx 缓冲问题

**解决方法**:
```bash
# 重启 Nginx
docker compose -f docker-compose.final.yml restart nginx
```

---

## 📝 完整验证清单

部署后请逐项测试：

- [ ] 上传 .docx 文件 ✅ 成功
- [ ] 上传 .xlsx 文件 ✅ 成功
- [ ] 上传 .pdf 文件 ✅ 成功
- [ ] 上传 .png 文件 ✅ 成功
- [ ] 上传 50MB+ 文件 ✅ 成功（进度条显示）
- [ ] 查看后端日志看到"📁 上传文件"记录
- [ ] 失败时看到详细中文错误提示

---

## 🔍 获取帮助

如果仍然无法上传 DOC/DOCX 文件，请提供：

1. **后端日志**（最近 50 行）:
   ```bash
   docker logs llm-chat-backend --tail 50
   ```

2. **具体错误信息**: 浏览器显示的错误内容

3. **文件信息**:
   - 文件名
   - 文件大小
   - 文件扩展名
