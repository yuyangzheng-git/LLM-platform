# Zachary's LLM — a tool-augmented LLM chat platform

[![Backend tests](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/backend-tests.yml)
[![Frontend checks](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/frontend-checks.yml/badge.svg)](https://github.com/yuyangzheng-git/LLM-platform/actions/workflows/frontend-checks.yml)

**English** · [简体中文](README.zh-CN.md)

A full-stack platform for streaming chat with multiple LLM providers, file
analysis, web search and tool calling, plus image and video generation. I
built it as a research prototype for studying how people work with AI systems
that combine language models with external tools — in particular, whether
tool use helps users **verify claims** against documents and the web.

- **Backend**: FastAPI · async SQLAlchemy · Alembic · Python 3.12
- **Frontend**: React 18 · Vite 5 · Tailwind CSS 3 (works on phones, installable to the home screen)
- **Providers**: OpenAI, Anthropic, Google Gemini, and any OpenAI-compatible API

---

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [API](#api)
- [Research use: claim verification](#research-use-claim-verification)
- [Development](#development)
- [Deployment](#deployment)
- [Security and privacy](#security-and-privacy)
- [Troubleshooting](#troubleshooting)
- [My contribution](#my-contribution)

## Features

**Chat**
- Real-time streaming over Server-Sent Events, with a stop button that keeps the partial reply
- Multi-turn tool calling: the model can call a tool, read the result and continue (up to 5 rounds)
- Reasoning ("thinking") and tool calls are shown live and restored when a conversation is reopened
- Persistent conversations (SQLite by default, PostgreSQL in production); the open conversation is kept in the URL (`?c=<id>`)
- File attachments: images (sent to vision models), PDF text extraction, plain-text formats

**Tools available to the model**

| Tool | What it does | External service |
|---|---|---|
| `web_search` | Web search | DuckDuckGo (via `ddgs`) |
| `analyze_website` | Fetch a page and extract title, text, links and images | The target site (internal/private addresses are blocked) |
| `get_current_datetime` | Current date and time in a time zone | none |
| `geocode_address` / `reverse_geocode` | Address ↔ coordinates | OpenStreetMap Nominatim |

**Generation**
- Image generation (e.g. DALL·E 3) and video generation through the configured OpenAI-compatible endpoint

**Interface**
- Painted "Roots & Roads" theme with light and dark (dusk) modes
- Phone support: keyboard-aware layout, safe-area insets for notches, 44px touch targets, swipe-to-close history drawer, add to home screen

## Quick start

### Option 1: Docker

```bash
git clone https://github.com/yuyangzheng-git/LLM-platform.git
cd LLM-platform
cp backend/.env.example backend/.env
```

Generate an encryption key and put it in `backend/.env` as `ENCRYPTION_KEY=...`
(it encrypts the provider API keys you save; without it saved keys cannot be
read back after a restart). This needs only the Python standard library:

```bash
python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Then start the stack:

```bash
docker compose up -d
```

- App: http://localhost:3212
- Backend health check: http://localhost:3211/health

### Option 2: Local development

Backend (Python 3.12):

```bash
cd backend
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.lock
cp .env.example .env   # then set ENCRYPTION_KEY (python generate_key.py)
uvicorn app.main:app --reload --port 3211
```

Frontend (Node 22):

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:3212. The database schema is created and migrated
automatically when the backend starts.

### Add a model provider

There is no settings page yet: providers are configured through the API. The
key is stored encrypted in the database.

```bash
curl -X POST http://localhost:3211/api/v1/models/configs \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "api_key": "sk-...", "default_model": "gpt-4o-mini", "enabled": true}'
```

`provider` is one of `openai`, `anthropic`, `gemini` or `generic`. For an
OpenAI-compatible gateway, add `"api_base_url": "https://your-gateway/v1"`.
New chats from the web UI are created with the `openai` provider, so pointing
that provider at a gateway that serves every model lets you use all models in
the model picker.

## Configuration

Backend settings are read from environment variables or `backend/.env`.

| Variable | Default | Notes |
|---|---|---|
| `ENCRYPTION_KEY` | *(empty)* | **Required.** Fernet key for stored API keys (`python backend/generate_key.py`) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/llm_chat.db` | Use `postgresql+asyncpg://user:pass@host:5432/db` for PostgreSQL |
| `ALLOWED_ORIGINS` | `http://localhost:3212,http://127.0.0.1:3212` | Comma-separated CORS origins |
| `DEBUG` | `False` | `True` also serves interactive API docs at `/docs` |
| `UPLOAD_DIR` | `./uploads` | Where uploaded files are stored |
| `MAX_FILE_SIZE` | `104857600` (100 MB) | Per-file upload limit in bytes |
| `LOG_LEVEL` | `INFO` | |

Provider API keys are **not** read from the environment: add them through the
API as shown above. `.env.example` still lists `OPENAI_API_KEY` and similar,
but the backend ignores them.

Frontend: `VITE_API_BASE_URL` is read **at build time**. Leave it empty in
Docker (the frontend's nginx proxies `/api` to the backend); the dev server
defaults to `http://localhost:3211`.

## Architecture

```
Browser (React)                 FastAPI backend                         External
───────────────                 ───────────────                         ────────
Chat UI ── POST /chat/stream ─▶ chat.py ─▶ ContextManager (history + files)
          ◀── SSE events ────── │        ─▶ LLMServiceFactory ─────────▶ OpenAI / Anthropic /
                                │             (openai, anthropic,          Gemini / gateway
                                │              gemini, generic)
                                └─ tool loop ─▶ ToolRegistry/Executor ──▶ DuckDuckGo, Nominatim,
                                                                          web pages (SSRF-guarded)
                                SQLAlchemy ─▶ SQLite / PostgreSQL (Alembic migrations)
```

```
backend/
  app/api/            chat (SSE + tool loop), conversations, files, models, generation
  app/services/llm/   one class per provider behind a common interface
  app/services/       context building, file handling
  app/tools/          tool definitions, registry, executor
  app/utils/          URL guard (SSRF), file validation, PDF/image processing
  migrations/         Alembic revisions
  tests/              pytest suite (temporary DB, fake LLM — no keys or network)
frontend/
  src/components/     unified (chat), generation (image/video), common
  src/services/       API clients (SSE parsing in chatAPI.js)
  public/             background painting, icons, web manifest
datasets/             claim-verification dataset (tracked)
scripts/              claim_verification.py experiment harness
```

## API

All endpoints are under `/api/v1`. Full schemas: run with `DEBUG=True` and open
http://localhost:3211/docs.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/chat/stream` | Send a message, stream the reply (SSE) |
| `POST` | `/chat/complete` | Same, non-streaming |
| `GET` `POST` | `/conversations` | List / create conversations |
| `GET` `PUT` `DELETE` | `/conversations/{id}` | Read / update / delete one |
| `GET` | `/conversations/{id}/messages` | History, including tool calls, reasoning and attachment counts |
| `POST` | `/files/upload`, `/files/upload/batch` | Upload attachments |
| `GET` `POST` | `/models/configs` | List / add provider configurations |
| `GET` `PUT` `DELETE` | `/models/configs/{provider}` | Manage one provider |
| `POST` | `/models/test/{provider}` | Test a provider's credentials |
| `POST` | `/generation/image`, `/generation/video` | Image / video generation |
| `GET` | `/health` | Health check (no prefix) |

A chat request needs an existing conversation:

```json
{ "conversation_id": 1, "message": "Hello", "file_ids": [], "enable_tools": true }
```

The stream sends `data: {...}` events with a `type` of `chunk`, `reasoning`,
`tool_call`, `tool_result`, `tool_blocked`, `error` or `done` (the last one
carries the saved message id and token usage).

## Research use: claim verification

**Question.** Can tool-augmented LLMs help users verify information and
synthesise evidence from documents and the web?

1. Do answers with tools (web search, page analysis, file context) contain fewer unsupported claims than tool-free answers?
2. How does citation quality change when the model has to ground claims in retrieved sources?
3. What latency and token cost does tool use add, and when is it worth it?

**Design.** Each claim is asked twice with the same model, temperature, prompt
and conversation settings; the only difference is `enable_tools`. With
`enable_tools: false` the backend sends **no** tool definitions to the model
and refuses to execute any tool call it still returns (covered by
`backend/tests/test_chat_tools.py`).

**Run it.** `datasets/claim_verification_dataset.json` holds 10 labelled
claims with reference URLs. With the platform running and a provider
configured:

```bash
python3 scripts/claim_verification.py --base-url http://localhost:3211 \
  --provider openai --model gpt-4o-mini --temperature 0
```

Raw answers go to `data/claim_verification_outputs/tools_on|tools_off/` and a
summary (tool-call counts, tokens, elapsed time) to
`data/claim_verification_summary.csv`. Any HTTP error, SSE `error` event or
stream without `done` marks that run as failed and the script exits non-zero.

**Metrics.** Factuality (human-judged against the reference), citation
presence and source reliability, coverage of claims checked, latency, token
cost, and the number of follow-up prompts needed.

**Limitations.** Search results can be stale or incomplete; some pages cannot
be read (JavaScript-heavy or paywalled); a citation is not proof of
verification; the pilot dataset is small and not statistically conclusive.

**Before running a study with people.** Use synthetic or de-identified
documents, clear `uploads/` between participants, and tell participants that
prompts, files and search queries are sent to third-party services.

## Development

```bash
# Backend tests (53): temporary database, fake LLM, no API keys or network
cd backend && pip install -r requirements.lock pytest pytest-asyncio && python -m pytest

# Frontend: lint, unit tests (Vitest), production build
cd frontend && npm ci && npm run lint && npm test && npm run build
```

GitHub Actions runs both on every pull request and on pushes to `main`
(`.github/workflows/`).

**Database changes.** After editing a model in `backend/app/models/`:

```bash
cd backend && alembic revision --autogenerate -m "describe the change"
```

Review the generated file in `migrations/versions/` before committing. Pending
migrations run automatically on startup; databases created before Alembic was
introduced are adopted automatically.

**Dependencies.** `backend/requirements.txt` lists direct dependencies;
`backend/requirements.lock` pins everything and is what Docker and CI install.
After changing `requirements.txt`:

```bash
cd backend && uv pip compile requirements.txt --universal --python-version 3.12 -o requirements.lock
```

**Adding a provider.** Implement `BaseLLMService` in
`backend/app/services/llm/` (`chat_stream`, `chat_complete`,
`test_connection`, `get_available_models`) and register it in `factory.py`.

**Adding a tool.** Write an async function in `backend/app/tools/`, describe
its parameters with `ToolDefinition`, register it with `tool_registry`, and call
the register function from the app's startup in `app/main.py`.

## Deployment

`docker-compose.yml` runs the backend (port 3211) and the frontend (nginx,
port 3212, proxying `/api`); data, uploads and logs are kept in
`backend/data`, `backend/uploads` and `backend/logs`.

`docker-compose.prod.yml` adds PostgreSQL (data in the `postgres-data` volume)
and a front nginx on port 3212. Before using it, edit its `ALLOWED_ORIGINS`
(currently a placeholder) and set `DB_PASSWORD` in the environment — otherwise
the database uses the default password written in the file.

For a public deployment:
- put HTTPS in front (e.g. a reverse proxy with a certificate);
- set `ALLOWED_ORIGINS` to your real domain and keep `DEBUG=False`;
- set a strong `ENCRYPTION_KEY` and back it up — losing it makes stored API keys unreadable;
- **restrict access** — see the next section.

## Security and privacy

- **There is no user authentication yet.** Anyone who can reach the server can
  read conversations, upload files and spend the configured API credit. Run it
  on a private network, behind a VPN, or behind an authenticating proxy until
  login is added.
- Provider API keys are encrypted at rest with Fernet; never commit `.env`.
- The page-analysis tool refuses loopback, private, link-local and other
  non-public addresses, re-checking every redirect, to prevent SSRF.
- Errors returned to clients are generic; details go to the server log.
- Uploads are capped, streamed to disk, and typed by extension; SVG is not accepted.
- Prompts, uploaded files and search queries are sent to third-party services
  (the LLM providers, DuckDuckGo, Nominatim and the pages being analysed).
  Conversations are stored in the database until deleted.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Reply says the model service is not configured | Add a provider with `POST /api/v1/models/configs` (see [Quick start](#add-a-model-provider)) |
| Saved API keys stop working after a restart | `ENCRYPTION_KEY` was empty or changed; set a fixed key and re-add the providers |
| Frontend loads but API calls fail (CORS) | Add the frontend's origin to `ALLOWED_ORIGINS` |
| `/docs` returns 404 | Interactive docs are only served with `DEBUG=True` |
| Port 3211 or 3212 already in use | `lsof -i :3211`, stop that process or change the port mapping in `docker-compose.yml` |

## My contribution

Solo project by Yu Yang Zheng. I designed and built:

- the FastAPI backend: async persistence with Alembic migrations, encrypted key storage, streaming SSE chat, file handling;
- the provider layer for OpenAI, Anthropic, Gemini and OpenAI-compatible APIs;
- the tool registry, executor and shared multi-turn tool loop, with an SSRF guard for web access;
- the React frontend: streaming UI with live tool calls and reasoning, stop/resume-safe state, image and video generation, the painted theme, and phone support;
- the claim-verification dataset and experiment harness;
- Docker/nginx deployment and GitHub Actions CI.

Verified by automated tests (53 backend, 12 frontend) that run in CI on every
pull request, including: `enable_tools=False` sends zero tool definitions and
never executes tools; the full upload → conversation → chat → saved-answer
flow; SSRF blocking (including redirects); upload limits; migrations on fresh
and legacy databases; and stream parsing when events are split across
network reads.

## License

MIT (as declared in `backend/pyproject.toml`).
