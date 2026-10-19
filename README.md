# LLM Chat Platform

<div align="center">

A modern, full-stack AI chat platform supporting multiple LLM providers with real-time streaming, file attachments, and tool calling capabilities.

[Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Configuration](#configuration) • [Deployment](#deployment)

---

**Research pitch**: This project is a full-stack LLM platform for streaming chat, file analysis, web search, and tool-augmented reasoning. I built it as a research prototype for studying how users interact with AI systems that combine language models with external tools. See [research.md](research.md) for the research framing and [docs/](docs/) for reproducible demos.

</div>

## Features

### Core Capabilities
- **Multi-Provider Support** - Seamlessly switch between OpenAI, Anthropic (Claude), and Google (Gemini) models
- **Real-time Streaming** - Server-Sent Events (SSE) for smooth, responsive chat experience
- **File Attachments** - Support for images, PDFs, and Office documents with intelligent processing
- **Conversation Management** - Persistent chat history with SQLite/PostgreSQL backend
- **Dark Mode** - Beautiful, responsive UI with dark/light theme support

### AI Tools & Capabilities
- **Web Search** - Integrated DuckDuckGo search for real-time information
- **Web Scraping** - Extract and analyze content from websites
- **Date/Time Queries** - Timezone-aware date and time information
- **Location Services** - IP-based geolocation lookup

### Developer Experience
- **API Documentation** - Auto-generated OpenAPI/Swagger docs
- **Docker Support** - One-command deployment with Docker Compose
- **Environment Configs** - Separate dev/prod configurations
- **Extensible Architecture** - Easy to add new LLM providers and tools

## Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **SQLAlchemy** - Async ORM with SQLite/PostgreSQL support
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Latest Python features

### Frontend
- **React 18** - Modern UI library with hooks
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **React Markdown** - Rich text rendering with syntax highlighting

### Infrastructure
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy and static file serving
- **PostgreSQL** - Production-ready database (optional)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OR Node.js 18+ and Python 3.11+ for local development

### Option 1: Docker Deployment (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yuyangzheng-git/LLM-platform.git
cd LLM-platform
```

2. Configure environment variables:
```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3212
- API Docs: http://localhost:3212/docs
- Health Check: http://localhost:3212/health

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate encryption key
python generate_key.py

# Configure .env file
cp .env.example .env
# Edit .env with your API keys and encryption key

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 3211
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access at http://localhost:3212

## Configuration

### Environment Variables

#### Backend (.env)
```bash
# Application
APP_NAME=LLM Chat Platform
DEBUG=True
HOST=0.0.0.0
PORT=3211

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/llm_chat.db

# CORS
ALLOWED_ORIGINS=http://localhost:3212

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=image/png,image/jpeg,application/pdf,...

# Encryption (generate with: python backend/generate_key.py)
ENCRYPTION_KEY=your_generated_key_here

# LLM API Keys
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Supported Models

#### OpenAI
- GPT-4, GPT-4 Turbo
- GPT-3.5 Turbo
- GPT-4o, GPT-4o Mini

#### Anthropic
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

#### Google
- Gemini 1.5 Pro
- Gemini 1.5 Flash

## Deployment

### Production Deployment with Docker

1. Update production configuration:
```bash
# Edit .env.production
vim .env.production
```

2. Use production compose file:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. Configure Nginx (if using external reverse proxy):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3212;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

### Database Migration (SQLite to PostgreSQL)

For production, use PostgreSQL:

```bash
# Update DATABASE_URL in .env.production
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/llmchat

# The database will be auto-initialized on first run
docker-compose -f docker-compose.prod.yml up -d
```

### Schema Migrations (Alembic)

The backend applies pending [Alembic](https://alembic.sqlalchemy.org/)
migrations from `backend/migrations/` on startup. A database created by an
older version (before migrations existed) is detected and adopted
automatically, so no manual step is needed when upgrading.

After changing a model in `backend/app/models/`, generate a migration:

```bash
cd backend
alembic revision --autogenerate -m "describe the change"
```

Review the generated file before committing it.

### Dependencies

`backend/requirements.txt` lists direct dependencies with minimum versions;
`backend/requirements.lock` pins every package and is what Docker and CI
install. After editing `requirements.txt`, regenerate the lock with
[uv](https://docs.astral.sh/uv/):

```bash
cd backend
uv pip compile requirements.txt --universal --python-version 3.12 -o requirements.lock
```

## Project Structure

```
llm-chat-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   │   └── llm/      # LLM provider integrations
│   │   ├── tools/        # AI tools (search, scrape, etc.)
│   │   └── utils/        # Utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API clients
│   │   └── config/       # Model configurations
│   ├── Dockerfile
│   └── package.json
├── nginx/                # Nginx configuration
├── docker-compose.yml    # Development
└── docker-compose.prod.yml # Production
```

## API Documentation

Interactive API docs (`/docs`, `/openapi.json`) are only served by the backend
when `DEBUG=true`. Run the backend locally in debug mode and visit
http://localhost:3211/docs.

### Key Endpoints

- `POST /api/v1/chat/stream` - Send a message and get a streaming response (requires `conversation_id`; `enable_tools` toggles tool use)
- `POST /api/v1/chat/complete` - Non-streaming chat completion
- `GET /api/v1/conversations` - List all conversations
- `POST /api/v1/files/upload` - Upload file attachments
- `GET /api/v1/models/configs` - List configured LLM models
- `GET /health` - Health check endpoint

## Development

### Adding a New LLM Provider

1. Create provider service in `backend/app/services/llm/`:
```python
class NewProviderService(BaseLLMService):
    async def generate_response(self, messages, **kwargs):
        # Implementation
        pass
```

2. Register in factory (`backend/app/services/llm/factory.py`)

3. Add model config to frontend (`frontend/src/config/models.js`)

### Adding a New Tool

1. Create tool in `backend/app/tools/`:
```python
@tool_registry.register("tool_name")
class NewTool:
    def execute(self, **kwargs):
        # Implementation
        pass
```

2. Tool is automatically available to all LLM providers

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Check what's using the port
lsof -i :3212
# Kill the process or change port in docker-compose.yml
```

**Database locked (SQLite)**
```bash
# Stop all containers
docker-compose down
# Remove database file
rm backend/data/llm_chat.db
# Restart
docker-compose up -d
```

**File upload fails**
- Check `MAX_FILE_SIZE` in .env
- Verify `ALLOWED_FILE_TYPES` includes your file type
- Ensure `uploads/` directory has write permissions

## Testing

Smoke and end-to-end tests live in `backend/tests/`. They use a temporary
database and upload directory (no dependency on local config) and a fake LLM
service (no API keys or network calls required).

```bash
cd backend
pip install -r requirements.lock pytest pytest-asyncio
python -m pytest -v
```

Coverage:

- Model-provider configuration shape (`tests/test_config.py`)
- Tool registry registration and listing (`tests/test_tools.py`)
- Health, root, models, and OpenAPI endpoints (`tests/test_api.py`)
- Upload file → create conversation → chat → answer flow, with and without
  tools; asserts that `enable_tools=False` sends zero tool definitions
  (`tests/test_chat_tools.py`)

### Experiment harness (requires a running backend + API key)

```bash
python3 scripts/claim_verification.py --base-url http://localhost:3211
```

Runs the 10-claim dataset in `datasets/claim_verification_dataset.json`
(tracked in git) under both tool conditions and saves raw answers + a summary
CSV. Any failed claim-condition (HTTP error, SSE `error`, missing `done`)
exits non-zero. See [docs/demo-claim-verification.md](docs/demo-claim-verification.md).

## My Contribution

Solo project (Yu Yang Zheng). What I designed and implemented:

- The FastAPI backend with async SQLAlchemy persistence and encrypted API-key storage
- The provider abstraction layer (`backend/app/services/llm/`) for OpenAI, Anthropic, and Google
- The tool registry and executor (`backend/app/tools/`) for web search, scraping, datetime, and location
- Streaming SSE chat endpoints, conversation management, and file attachments
- The React/Vite/Tailwind frontend with dark mode and streaming rendering
- Docker Compose deployments (dev, prod) and Nginx reverse-proxy configuration

What I verified in this repository (with automated checks):

- 25 tests in `backend/tests/` pass, using an isolated temporary database and a
  fake LLM service (no API keys or network needed)
- `enable_tools` is threaded through `/api/v1/chat/stream` and `/complete`;
  a test asserts that `enable_tools=False` sends **zero** tool definitions
  **and** that the tool executor is never invoked even if the model still
  returns tool calls (guarded at the execution entry)
- Both endpoints share one tool-call loop (`app/api/tool_loop.py`): model
  requests tool → execute → results appended → second model call → answer
  persisted (tested for stream and complete)
- End-to-end test: upload file → create conversation → chat → persisted answer
- The 10-claim dataset (committed in `datasets/claim_verification_dataset.json`)
  and the `scripts/claim_verification.py` harness run both tool conditions,
  save raw answers for scoring, and exit non-zero on failed runs (tested with
  fake SSE error / missing-`done` servers)
- All documented API payloads in `docs/demo-claim-verification.md` match the
  implemented schemas (`conversation_id` required, 422 otherwise)

## Security Considerations

- API keys are encrypted at rest using Fernet encryption
- Never commit `.env` files to version control
- Use strong, unique `ENCRYPTION_KEY` in production
- Enable HTTPS in production with proper SSL certificates
- Restrict CORS origins in production

### Privacy Notes (important for research use)

- Prompts and uploaded files are sent to third-party LLM providers (OpenAI, Anthropic, Google). Do not upload personal or confidential data.
- Use synthetic or de-identified documents for studies; clear `uploads/` between participants.
- Web search and scraping queries are also sent to external services (DuckDuckGo/SearXNG and target websites).
- Conversations are stored in the local database; delete or export them per your ethics protocol.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

Built with modern tools and frameworks from the open-source community.

---

**Note**: This platform is designed for personal or internal use. Ensure you comply with the terms of service of any LLM providers you use.
