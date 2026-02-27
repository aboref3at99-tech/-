# AI Agent MCP Starter

Starter kit for running an AI agent that can:

- Use OpenAI Agents SDK as the agent runtime.
- Control a real browser via Playwright MCP server.
- Access custom tools exposed through your own MCP server.

## Structure

- `ai-agent-mcp-starter/agent_app`: FastAPI app that runs the agent loop.
- `ai-agent-mcp-starter/mcp_mytools`: Custom MCP server (`FastMCP`) with file/API tools.
- `ai-agent-mcp-starter/docker-compose.yml`: Runs `agent`, `playwright`, and `mytools` services together.

## Quick start

```bash
cd ai-agent-mcp-starter
cp .env.example .env
# edit OPENAI_API_KEY

docker compose up --build
```

Run a task:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task":"افتح ويكيبيديا وروح لصفحة OpenAI واديني ملخص فقرتين."}'
```
