# AI Agent MCP Starter

Starter kit for building an AI Agent that connects to:
- Playwright MCP for browser automation.
- A custom MCP server for internal tools and workspace file operations.

## Quick start

```bash
cp .env.example .env
# edit OPENAI_API_KEY

docker compose up --build
```

## Endpoints

- `GET /health` for basic liveness.
- `POST /run` to execute a task.

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
