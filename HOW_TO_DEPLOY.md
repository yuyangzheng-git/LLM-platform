# 🚀 部署到服务器 - 完整步骤

## 方法一：使用 SCP 传输（推荐）

### 步骤 1: 打开终端，传输文件

**在本地执行（复制粘贴）：**

```bash
# 传输部署包
scp llm-chat-complete-fix.tar.gz ubuntu@your-server-ip:/opt/llm-chat-platform/

# 传输部署脚本
scp deploy-on-server.sh ubuntu@your-server-ip:/opt/llm-chat-platform/
```

**密码：** `your_password`

---

### 步骤 2: SSH 登录服务器

```bash
ssh ubuntu@your-server-ip
```

**密码：** `your_password`

---

### 步骤 3: 在服务器上执行部署

**在服务器上执行（复制粘贴）：**

```bash
cd /opt/llm-chat-platform
chmod +x deploy-on-server.sh
./deploy-on-server.sh
```

**完成！** 等待约 2-3 分钟构建完成。

---

## 方法二：手动命令（如果脚本失败）

如果脚本执行失败，在服务器上手动执行：

```bash
cd /opt/llm-chat-platform

# 1. 解压文件
tar xzf llm-chat-complete-fix.tar.gz

# 2. 重新构建所有服务
docker compose -f docker-compose.final.yml build

# 3. 重启服务
docker compose -f docker-compose.final.yml down
docker compose -f docker-compose.final.yml up -d

# 4. 检查状态
docker compose -f docker-compose.final.yml ps

# 5. 查看日志
docker logs llm-chat-backend --tail 30
docker logs llm-chat-nginx --tail 20
```

---

## ✅ 部署成功标志

服务状态应该显示：

```
NAME                 STATUS    PORTS
llm-chat-backend     Up        0.0.0.0:3211->3211/tcp
llm-chat-nginx       Up        0.0.0.0:3212->3212/tcp
```

---

## 🧪 部署后测试

### 1. 清除浏览器缓存（必须！）

- **Windows/Linux:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`
- **或使用无痕模式**

### 2. 访问应用

打开浏览器访问：`http://your-server-ip:3212`

### 3. 测试功能

**测试 1: 文件上传**
- 准备一个 `.docx` 或 `.xlsx` 文件
- 点击上传按钮
- ✅ 应该显示进度条并成功上传

**测试 2: UI 优化**
- ✅ 顶部只有一个栏（不是两个）
- ✅ 右上角显示当前模型（如 "gpt-4o"）

**测试 3: 删除对话**
- 点击左上角菜单按钮
- 在对话列表中，鼠标悬停在任意对话上
- ✅ 右侧出现红色垃圾桶图标
- 点击删除，有确认提示

---

## 🔍 故障排查

### 问题 1: 文件传输失败

如果 SCP 传输失败，检查：
1. 服务器 IP 是否正确（your-server-ip）
2. 密码是否正确（your_password）
3. 本地文件是否存在

### 问题 2: 服务启动失败

在服务器上执行：
```bash
docker compose -f docker-compose.final.yml logs --tail 50
```

查看详细错误信息。

### 问题 3: 浏览器看不到更新

**原因：** 浏览器缓存

**解决：**
1. 硬刷新：`Ctrl + Shift + R`
2. 或清空浏览器缓存
3. 或使用无痕模式

### 问题 4: 文件上传仍然失败

在服务器上查看日志：
```bash
docker logs llm-chat-backend --tail 50 | grep "📁"
```

应该看到：
```
📁 上传文件: xxx.docx, MIME类型: xxx
```

如果看到"不支持的文件类型"，说明后端未更新，需要重新构建。

---

## 📞 需要帮助？

如果遇到问题，提供以下信息：

1. 服务状态：
   ```bash
   docker compose -f docker-compose.final.yml ps
   ```

2. 后端日志：
   ```bash
   docker logs llm-chat-backend --tail 50
   ```

3. 浏览器控制台错误（F12 → Console）

---

## 📝 更新内容总结

本次部署包含：

1. **文件上传修复**
   - 完全移除 MIME 类型验证
   - 只验证文件扩展名
   - 支持 .doc, .docx, .xls, .xlsx, .ppt, .pptx 等

2. **UI 优化**
   - 合并两个顶栏为一个
   - 更简洁的界面

3. **删除对话功能**
   - 鼠标悬停显示删除按钮
   - 删除前确认提示

---

**准备好了吗？** 按照上述步骤开始部署！
