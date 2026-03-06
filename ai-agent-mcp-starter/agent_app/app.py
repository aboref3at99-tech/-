from fastapi import FastAPI
from pydantic import BaseModel

from agent_runner import run_task

app = FastAPI(title="AI Agent + MCP + Browser")


class RunRequest(BaseModel):
    task: str


@app.post("/run")
async def run(req: RunRequest):
    output = await run_task(req.task)
    return {"output": output}
