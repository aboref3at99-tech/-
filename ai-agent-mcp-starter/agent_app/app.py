import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent_runner import run_task

app = FastAPI(title="AI Agent + MCP + Browser")

cors_origins = [origin.strip() for origin in os.environ.get("CORS_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    task: str = Field(min_length=1, description="User task")
    approved: bool = Field(
        default=False,
        description="Explicit approval for sensitive, non-reversible actions.",
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
      <head><title>AI Agent MCP Starter</title></head>
      <body style=\"font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto;\">
        <h2>AI Agent + MCP + Browser</h2>
        <p>Quick web runner for cloud deployments.</p>
        <form method=\"post\" action=\"/run\" onsubmit=\"return false;\">
          <textarea id=\"task\" rows=\"6\" style=\"width:100%;\" placeholder=\"اكتب المهمة هنا\"></textarea><br/><br/>
          <label><input type=\"checkbox\" id=\"approved\"/> approved (for sensitive actions)</label><br/><br/>
          <button onclick=\"runTask()\">Run</button>
        </form>
        <pre id=\"out\" style=\"background:#111;color:#ddd;padding:1rem;white-space:pre-wrap;\"></pre>
        <script>
          async function runTask() {
            const out = document.getElementById('out');
            out.textContent = 'Running...';
            const resp = await fetch('/run', {
              method: 'POST',
              headers: {'Content-Type':'application/json'},
              body: JSON.stringify({
                task: document.getElementById('task').value,
                approved: document.getElementById('approved').checked
              })
            });
            const data = await resp.json();
            out.textContent = JSON.stringify(data, null, 2);
          }
        </script>
      </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/run")
async def run(req: RunRequest):
    try:
        output = await run_task(req.task, approved=req.approved)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Agent run timed out")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Agent run failed: {exc}")

    return {"output": output}
