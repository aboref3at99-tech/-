from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent_runner import run_task

app = FastAPI(title="AI Agent + MCP + Browser")


class RunRequest(BaseModel):
    task: str = Field(min_length=1, description="User task")
    approved: bool = Field(
        default=False,
        description="Explicit approval for sensitive, non-reversible actions.",
    )


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
