# AI Agent MCP Starter

Starter kit for building an AI Agent that connects to:
- Playwright MCP for browser automation.
- A custom MCP server for internal tools and workspace file operations.
- A lightweight video-workflow planning API (project, scenes, prompt packet) with file-backed persistence for cloud runs.

## Quick start (local)

```bash
cp .env.example .env
# edit OPENAI_API_KEY

docker compose up --build
```

## Endpoints

- `GET /` lightweight web UI (useful for cloud test).
- `GET /health` liveness.
- `POST /run` execute a task.

Example run:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"افتح ويكيبيديا، روح لصفحة OpenAI وخدلي ملخص فقرتين."}'
```

If your task includes sensitive actions (delete/payment/transfer/send/final confirm), pass `approved: true` explicitly:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"احذف الملف secrets.txt", "approved": true}'
```

## Video planning endpoints (new)

The starter now includes a first MVP for long-form AI video workflows:

- `POST /video/projects` create a project workspace.
- `GET /video/projects/{project_id}` fetch saved project metadata.
- `POST /video/projects/{project_id}/plan` generate outline + scene plan + production checklist.
- `POST /video/projects/{project_id}/prompts` generate start/end prompt pairs for each scene while keeping a character consistency packet.

Create a project:

```bash
curl -X POST http://localhost:8000/video/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title":"AI Documentary about Mars",
    "idea":"شرح رحلة بناء وثائقي طويل من الفكرة إلى التصدير",
    "audience":"content creators",
    "target_duration_minutes":12,
    "language":"ar",
    "visual_style":"cinematic educational"
  }'
```

Generate plan:

```bash
curl -X POST http://localhost:8000/video/projects/<project_id>/plan
```

Generate prompts:

```bash
curl -X POST http://localhost:8000/video/projects/<project_id>/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "character_name":"Omar",
    "character_description":"middle eastern male educator, short beard, calm expression",
    "wardrobe":"dark blue shirt",
    "camera_style":"35mm medium shot",
    "lighting_style":"soft key light"
  }'
```

---

## Desktop app for laptop

If you want a laptop desktop app (instead of browser-only), use the included Tkinter client:

```bash
cd ai-agent-mcp-starter
python desktop_app/app.py
```

- Default backend URL: `http://127.0.0.1:8000/run`
- You can point it to your cloud endpoint with:

```bash
AGENT_API_URL="https://your-agent-domain/run" python desktop_app/app.py
```

Optional executable build (Windows/macOS/Linux):

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed desktop_app/app.py --name ai-agent-mcp-desktop
```

---

## Cloud deployment (3 services)

To run this "on the cloud web", deploy **three separate services** in the same private network:

1. `playwright` service from image `mcr.microsoft.com/playwright/mcp`
2. `mytools` service from `./mcp_mytools`
3. `agent` service from `./agent_app` (public HTTP)

### Required env on `agent`

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional)
- `RUN_TIMEOUT_SECONDS`
- `CORS_ORIGINS` (set your frontend domain in production)
- `PLAYWRIGHT_MCP_URL` (private URL to playwright, e.g. `http://playwright:8931/mcp`)
- `MYTOOLS_MCP_URL` (private URL to mytools, e.g. `http://mytools:8000/mcp`)
- `VIDEO_PROJECTS_FILE` (optional): path for persisted video project metadata (default `/tmp/ai-agent-mcp/video-projects.json`).

### Required env on `mytools`

- `WORKSPACE_DIR=/workspace`
- `MY_AI_TOOLS_BASE_URL` (optional internal API)
- `MY_AI_TOOLS_TOKEN` (optional)

### Deployment notes

- Keep `playwright` and `mytools` **private/internal only**.
- Expose only `agent` publicly.
- Set `CORS_ORIGINS` to your exact frontend domain(s), not `*`, in production.
- Mount a persistent volume for `/workspace` on `mytools` if you need saved files.
- For multi-instance deployment, move project storage to a shared DB (PostgreSQL/Redis) instead of local file persistence.
