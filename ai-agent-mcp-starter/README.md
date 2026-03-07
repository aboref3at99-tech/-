# AI Agent MCP Starter

Starter kit for building an AI Agent that connects to:
- Playwright MCP for browser automation.
- A custom MCP server for internal tools and workspace file operations.
- A lightweight video-workflow planning API (project, scenes, prompt packet) with file-backed persistence.

## Mobile-first usage (no Docker required)

If you will use the app from a **phone browser only**, run the backend directly and open it via your public domain.

### 1) Install dependencies

```bash
cd ai-agent-mcp-starter/agent_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Set environment variables

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-5.2"
export RUN_TIMEOUT_SECONDS="180"
export CORS_ORIGINS="*"
export PLAYWRIGHT_MCP_URL="http://playwright:8931/mcp"
export MYTOOLS_MCP_URL="http://mytools:8000/mcp"
export VIDEO_PROJECTS_FILE="/tmp/ai-agent-mcp/video-projects.json"
export RATE_LIMIT_WINDOW_SECONDS="60"
export RATE_LIMIT_MAX_REQUESTS="120"
```

### 3) Start backend

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then open from your phone browser:

```text
https://your-domain/
```

---

## Endpoints

- `GET /` interactive web UI for agent tasks + video workflow (mobile-ready).
- `GET /health` liveness.
- `GET /ready` readiness checks for required env vars, writable project storage, and rate-limit config.
- `POST /run` execute a task.


Readiness check:

```bash
curl http://localhost:8000/ready
```

Example run:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"Open Wikipedia, navigate to OpenAI page, and summarize two paragraphs."}'
```

If your task includes sensitive actions (delete/payment/transfer/send/final confirm), pass `approved: true` explicitly:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"Delete file secrets.txt", "approved": true}'
```

## Video planning endpoints

> All `/video/*` endpoints require `x-user-id` header (simple owner isolation).

- `POST /video/projects` create a project workspace.
- `GET /video/projects` list saved projects (latest first).
- `GET /video/projects/{project_id}` fetch saved project metadata (includes latest saved plan/prompts).
- `PATCH /video/projects/{project_id}` update project fields (title, idea, duration, style, etc.).
- `DELETE /video/projects/{project_id}` delete a project.
- `POST /video/projects/{project_id}/plan` generate outline + scene plan + production checklist (also saved in project metadata).
- `POST /video/projects/{project_id}/prompts` generate start/end prompt pairs for each scene with a character consistency packet (also saved in project metadata).

Create a project:

```bash
curl -X POST http://localhost:8000/video/projects \
  -H "Content-Type: application/json" \
  -H "x-user-id: mobile-user-1" \
  -d '{
    "title":"AI Documentary about Mars",
    "idea":"Explain the full long-form video production workflow from concept to export",
    "audience":"content creators",
    "target_duration_minutes":12,
    "language":"en",
    "visual_style":"cinematic educational"
  }'
```

List projects:

```bash
curl -H "x-user-id: mobile-user-1" http://localhost:8000/video/projects
```

Generate plan:

```bash
curl -X POST http://localhost:8000/video/projects/<project_id>/plan \
  -H "x-user-id: mobile-user-1"
```

Generate prompts:

```bash
curl -X POST http://localhost:8000/video/projects/<project_id>/prompts \
  -H "Content-Type: application/json" \
  -H "x-user-id: mobile-user-1" \
  -d '{
    "character_name":"Omar",
    "character_description":"middle eastern male educator, short beard, calm expression",
    "wardrobe":"dark blue shirt",
    "camera_style":"35mm medium shot",
    "lighting_style":"soft key light"
  }'
```

Update project:

```bash
curl -X PATCH http://localhost:8000/video/projects/<project_id> \
  -H "Content-Type: application/json" \
  -H "x-user-id: mobile-user-1" \
  -d '{"title":"Updated mobile workflow project"}'
```

Delete project:

```bash
curl -X DELETE http://localhost:8000/video/projects/<project_id> \
  -H "x-user-id: mobile-user-1"
```

---

## Docker (optional)

Docker is optional. Use it only if you want all services locally in one command:

```bash
cp .env.example .env
docker compose up --build
```

---

## Cloud deployment notes

- Expose only `agent` publicly; keep tool services private.
- Set `CORS_ORIGINS` to your exact domain in production.
- `VIDEO_PROJECTS_FILE` is file-based MVP storage.
- `RATE_LIMIT_WINDOW_SECONDS` and `RATE_LIMIT_MAX_REQUESTS` control basic in-memory rate limiting.
- For multi-instance deployments, move to shared DB storage (PostgreSQL/Redis).
