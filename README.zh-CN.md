# Zachary's LLM —— 支持工具调用的大模型对话平台

[![Backend tests](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/backend-tests.yml)
[![Frontend checks](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/frontend-checks.yml/badge.svg)](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/frontend-checks.yml)

[English](README.md) · **简体中文**

一个全栈平台：支持多家大模型的流式对话、文件分析、网络搜索和工具调用，以及图片和视频生成。
它也是一个研究原型，用来研究人们如何使用"大模型 + 外部工具"的 AI 系统，尤其是工具能否帮助用户
**核实信息**（对照文档和网络来源）。

- **后端**：FastAPI · 异步 SQLAlchemy · Alembic · Python 3.12
- **前端**：React 18 · Vite 5 · Tailwind CSS 3（支持手机，可添加到主屏幕）
- **模型服务**：OpenAI、Anthropic、Google Gemini，以及任何兼容 OpenAI 的接口

---

## 目录

- [功能](#功能)
- [快速开始](#快速开始)
- [配置](#配置)
- [架构](#架构)
- [接口](#接口)
- [研究用途：信息核实实验](#研究用途信息核实实验)
- [开发](#开发)
- [部署](#部署)
- [安全与隐私](#安全与隐私)
- [常见问题](#常见问题)
- [我的工作](#我的工作)

## 功能

**对话**
- 基于 SSE 的实时流式输出；可随时停止，已生成的部分会保留
- 多轮工具调用：模型调用工具、读取结果后继续回答（最多 5 轮）
- 思考过程和工具调用实时显示，重新打开对话时也会恢复
- 对话持久保存（默认 SQLite，生产环境可用 PostgreSQL）；当前对话记录在网址里（`?c=<id>`），刷新不丢
- 附件：图片（发给支持视觉的模型）、PDF 文本提取、各类纯文本文件

**模型可用的工具**

| 工具 | 作用 | 依赖的外部服务 |
|---|---|---|
| `web_search` | 网络搜索 | DuckDuckGo（`ddgs`） |
| `analyze_website` | 读取网页，提取标题、正文、链接和图片 | 目标网站（禁止访问内网 / 本机地址） |
| `get_current_datetime` | 指定时区的当前日期和时间 | 无 |
| `geocode_address` / `reverse_geocode` | 地址与坐标互查 | OpenStreetMap Nominatim |

**生成**
- 通过已配置的 OpenAI 兼容接口生成图片（如 DALL·E 3）和视频

**界面**
- "Roots & Roads" 油画风格，浅色和深色（黄昏）两种模式
- 手机适配：键盘弹出时布局自动调整、适配刘海、44px 点击区域、侧栏左滑关闭、可添加到主屏幕

## 快速开始

### 方式一：Docker

```bash
git clone https://github.com/yuyangzheng-git/LLM-platform.git
cd LLM-platform
cp backend/.env.example backend/.env
```

生成加密密钥，填进 `backend/.env` 的 `ENCRYPTION_KEY=...`（用来加密保存的 API Key；不设置的话，
重启后已保存的 Key 将无法读取）。只需要 Python 标准库：

```bash
python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

启动：

```bash
docker compose up -d
```

- 应用：http://localhost:3212
- 后端健康检查：http://localhost:3211/health

### 方式二：本地开发

后端（Python 3.12）：

```bash
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.lock
cp .env.example .env   # 然后设置 ENCRYPTION_KEY（python generate_key.py）
uvicorn app.main:app --reload --port 3211
```

前端（Node 22）：

```bash
cd frontend
npm ci
npm run dev
```

打开 http://localhost:3212。后端启动时会自动创建并迁移数据库结构。

### 添加模型服务

目前还没有设置页面，模型服务通过接口配置，Key 会加密存进数据库：

```bash
curl -X POST http://localhost:3211/api/v1/models/configs \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "api_key": "sk-...", "default_model": "gpt-4o-mini", "enabled": true}'
```

`provider` 可选 `openai`、`anthropic`、`gemini`、`generic`。使用兼容 OpenAI 的网关时，加上
`"api_base_url": "https://your-gateway/v1"`。网页上新建的对话都使用 `openai` 这个服务商，
所以把它指向一个支持所有模型的网关，就能用模型列表里的全部模型。

## 配置

后端配置从环境变量或 `backend/.env` 读取。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `ENCRYPTION_KEY` | *（空）* | **必填。** 加密 API Key 用的 Fernet 密钥（`python backend/generate_key.py`） |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/llm_chat.db` | PostgreSQL 用 `postgresql+asyncpg://user:pass@host:5432/db` |
| `ALLOWED_ORIGINS` | `http://localhost:3212,http://127.0.0.1:3212` | 允许跨域的来源，逗号分隔 |
| `DEBUG` | `False` | 设为 `True` 时同时开放 `/docs` 接口文档 |
| `UPLOAD_DIR` | `./uploads` | 上传文件的存放目录 |
| `MAX_FILE_SIZE` | `104857600`（100 MB） | 单个文件大小上限（字节） |
| `LOG_LEVEL` | `INFO` | |

模型服务的 API Key **不会**从环境变量读取，请按上面的方法通过接口添加。`.env.example` 里仍列着
`OPENAI_API_KEY` 等变量，但后端不会使用它们。

前端：`VITE_API_BASE_URL` 在**构建时**生效。Docker 部署时留空即可（前端的 nginx 会把 `/api` 转发给后端）；
开发服务器默认连 `http://localhost:3211`。

## 架构

```
浏览器（React）                  FastAPI 后端                           外部服务
──────────────                  ────────────                           ────────
对话界面 ── POST /chat/stream ─▶ chat.py ─▶ ContextManager（历史 + 附件）
         ◀── SSE 事件 ───────── │        ─▶ LLMServiceFactory ─────────▶ OpenAI / Anthropic /
                                │            （openai、anthropic、          Gemini / 网关
                                │              gemini、generic）
                                └─ 工具循环 ─▶ ToolRegistry/Executor ───▶ DuckDuckGo、Nominatim、
                                                                         网页（防 SSRF）
                                SQLAlchemy ─▶ SQLite / PostgreSQL（Alembic 迁移）
```

```
backend/
  app/api/            对话（SSE + 工具循环）、会话、文件、模型配置、生成
  app/services/llm/   每家模型服务一个类，接口统一
  app/services/       上下文构建、文件处理
  app/tools/          工具定义、注册表、执行器
  app/utils/          URL 检查（防 SSRF）、文件校验、PDF/图片处理
  migrations/         Alembic 迁移
  tests/              pytest 测试（临时数据库、模拟大模型，不需要 Key 和网络）
frontend/
  src/components/     unified（对话）、generation（图片/视频）、common（通用）
  src/services/       接口调用（chatAPI.js 负责解析 SSE）
  public/             背景画、图标、web manifest
datasets/             信息核实数据集（已纳入版本控制）
scripts/              claim_verification.py 实验脚本
```

## 接口

所有接口都在 `/api/v1` 下。完整的字段说明：设置 `DEBUG=True` 后打开 http://localhost:3211/docs。

| 方法 | 路径 | 作用 |
|---|---|---|
| `POST` | `/chat/stream` | 发送消息，流式返回回复（SSE） |
| `POST` | `/chat/complete` | 同上，非流式 |
| `GET` `POST` | `/conversations` | 列出 / 新建对话 |
| `GET` `PUT` `DELETE` | `/conversations/{id}` | 读取 / 修改 / 删除对话 |
| `GET` | `/conversations/{id}/messages` | 历史消息，含工具调用、思考过程和附件数 |
| `POST` | `/files/upload`、`/files/upload/batch` | 上传附件 |
| `GET` `POST` | `/models/configs` | 列出 / 添加模型服务配置 |
| `GET` `PUT` `DELETE` | `/models/configs/{provider}` | 管理某个服务商 |
| `POST` | `/models/test/{provider}` | 测试服务商的 Key 是否可用 |
| `POST` | `/generation/image`、`/generation/video` | 图片 / 视频生成 |
| `GET` | `/health` | 健康检查（无前缀） |

发送消息前需要先有对话：

```json
{ "conversation_id": 1, "message": "你好", "file_ids": [], "enable_tools": true }
```

流里的每个 `data: {...}` 事件都有 `type`：`chunk`、`reasoning`、`tool_call`、`tool_result`、
`tool_blocked`、`error` 或 `done`（最后一个带有保存后的消息 id 和 token 用量）。

## 研究用途：信息核实实验

**研究问题。** 借助工具的大模型能否帮助用户核实信息、综合文档和网络上的证据？

1. 使用工具（网络搜索、网页分析、文件上下文）的回答，是否比不使用工具的回答包含更少无依据的说法？
2. 要求模型用检索到的来源支撑说法时，引用质量如何变化？
3. 使用工具会增加多少延迟和 token 成本？什么时候值得？

**实验设计。** 每条说法问两次，模型、temperature、提示词和对话设置完全相同，唯一的区别是
`enable_tools`。`enable_tools: false` 时，后端**不会**向模型发送任何工具定义，即使模型仍返回工具调用
也不会执行（由 `backend/tests/test_chat_tools.py` 测试保证）。

**运行实验。** `datasets/claim_verification_dataset.json` 里有 10 条带标签和参考链接的说法。
平台运行且已配置模型服务后：

```bash
python3 scripts/claim_verification.py --base-url http://localhost:3211 \
  --provider openai --model gpt-4o-mini --temperature 0
```

原始回答保存在 `data/claim_verification_outputs/tools_on|tools_off/`，汇总（工具调用次数、token、耗时）
保存在 `data/claim_verification_summary.csv`。只要出现 HTTP 错误、SSE `error` 事件或流里没有 `done`，
该次运行就记为失败，脚本以非零状态退出。

**评估指标。** 事实准确性（人工对照参考来源判定）、是否给出引用及来源可靠性、核查覆盖率、延迟、
token 成本、得到可用答案所需的追问次数。

**局限。** 搜索结果可能过时或不全；部分网页读不到（依赖 JavaScript 或付费墙）；有引用不等于已核实；
试点数据集很小，结论不具统计意义。

**招募参与者做实验前。** 使用合成或已去标识化的文档；每位参与者之间清空 `uploads/`；
告知参与者提示词、文件和搜索内容会发送给第三方服务。

## 开发

```bash
# 后端测试（53 个）：临时数据库、模拟大模型，不需要 API Key 和网络
cd backend && pip install -r requirements.lock pytest pytest-asyncio && python -m pytest

# 前端：lint、单元测试（Vitest）、生产构建
cd frontend && npm ci && npm run lint && npm test && npm run build
```

每个 PR 和每次推送到 `main` 都会由 GitHub Actions 自动运行以上检查（`.github/workflows/`）。

**修改数据库结构。** 改完 `backend/app/models/` 里的模型后：

```bash
cd backend && alembic revision --autogenerate -m "说明改动"
```

提交前检查 `migrations/versions/` 里生成的文件。启动时会自动执行未完成的迁移；
引入 Alembic 之前创建的旧数据库也会被自动接管。

**依赖。** `backend/requirements.txt` 列出直接依赖；`backend/requirements.lock` 锁定全部版本，
Docker 和 CI 都按它安装。修改 `requirements.txt` 后：

```bash
cd backend && uv pip compile requirements.txt --universal --python-version 3.12 -o requirements.lock
```

**新增模型服务。** 在 `backend/app/services/llm/` 里实现 `BaseLLMService`（`chat_stream`、
`chat_complete`、`test_connection`、`get_available_models`），并在 `factory.py` 里注册。

**新增工具。** 在 `backend/app/tools/` 写一个异步函数，用 `ToolDefinition` 描述参数，注册到
`tool_registry`，再在 `app/main.py` 的启动流程里调用注册函数。

## 部署

`docker-compose.yml` 运行后端（3211 端口）和前端（nginx，3212 端口，并转发 `/api`）；
数据、上传文件和日志保存在 `backend/data`、`backend/uploads`、`backend/logs`。

`docker-compose.prod.yml` 额外加了 PostgreSQL（数据在 `postgres-data` 卷里）和一个前置 nginx（3212 端口）。
使用前先修改其中的 `ALLOWED_ORIGINS`（目前是占位值），并在环境变量里设置 `DB_PASSWORD`，
否则数据库会使用文件里写的默认密码。

公网部署时：
- 加上 HTTPS（例如带证书的反向代理）；
- `ALLOWED_ORIGINS` 设成真实域名，保持 `DEBUG=False`；
- 设置一个强 `ENCRYPTION_KEY` 并备份——丢失后已保存的 API Key 都无法读取；
- **限制访问**——见下一节。

## 安全与隐私

- **目前没有用户登录。** 能访问服务器的人都可以查看对话、上传文件、消耗已配置的 API 额度。
  在加上登录之前，请只在内网、VPN 后面或带认证的反向代理后面运行。
- 模型服务的 API Key 用 Fernet 加密存储；不要提交 `.env`。
- 网页分析工具会拒绝本机、内网、链路本地等非公网地址，并检查每一次跳转，防止 SSRF。
- 返回给前端的错误信息是通用提示，详细内容只写进服务器日志。
- 上传有大小限制，分块写入磁盘，按扩展名判断类型，不接受 SVG。
- 提示词、上传的文件和搜索内容会发送给第三方服务（大模型服务商、DuckDuckGo、Nominatim 和被分析的网页）。
  对话会一直保存在数据库里，直到被删除。

## 常见问题

| 现象 | 解决办法 |
|---|---|
| 回复提示"模型服务尚未配置" | 用 `POST /api/v1/models/configs` 添加服务商（见[添加模型服务](#添加模型服务)） |
| 重启后已保存的 API Key 不能用了 | `ENCRYPTION_KEY` 为空或被改过；设置一个固定的密钥后重新添加服务商 |
| 页面能打开但接口请求失败（CORS） | 把前端的地址加进 `ALLOWED_ORIGINS` |
| `/docs` 返回 404 | 接口文档只在 `DEBUG=True` 时开放 |
| 3211 或 3212 端口被占用 | `lsof -i :3211` 找到并停掉占用的进程，或修改 `docker-compose.yml` 里的端口映射 |

## 我的工作

本项目由 Yu Yang Zheng 独立完成，设计并实现了：

- FastAPI 后端：带 Alembic 迁移的异步持久化、加密的 Key 存储、SSE 流式对话、文件处理；
- 统一接入 OpenAI、Anthropic、Gemini 和 OpenAI 兼容接口的模型服务层；
- 工具注册表、执行器和前后端共用的多轮工具循环，以及访问网页时的 SSRF 防护；
- React 前端：实时显示工具调用和思考过程的流式界面、停止生成、图片与视频生成、油画风格主题和手机适配；
- 信息核实数据集和实验脚本；
- Docker / nginx 部署和 GitHub Actions CI。

由自动化测试保证（后端 53 个、前端 12 个，每个 PR 都会在 CI 中运行），包括：`enable_tools=False`
时不发送任何工具定义、也绝不执行工具；上传 → 新建对话 → 发送消息 → 保存回答的完整流程；
SSRF 拦截（含跳转）；上传限制；新旧数据库的迁移；SSE 事件被网络拆成两段时的解析。

## 许可证

MIT（见 `backend/pyproject.toml` 中的声明）。
