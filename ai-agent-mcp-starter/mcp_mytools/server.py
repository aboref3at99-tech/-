import os
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", "/workspace")).resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

mcp = FastMCP(
    "mytools",
    stateless_http=True,
    json_response=True,
)


def _safe_path(rel_path: str) -> Path:
    p = (WORKSPACE / rel_path).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError("Path is outside workspace")
    return p


@mcp.tool()
def list_files() -> list[str]:
    """List files under the workspace directory."""
    return [str(p.relative_to(WORKSPACE)) for p in WORKSPACE.rglob("*") if p.is_file()]


@mcp.tool()
def read_file(path: str) -> str:
    """Read a UTF-8 text file from workspace."""
    p = _safe_path(path)
    return p.read_text(encoding="utf-8")


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write a UTF-8 text file to workspace (creates parents)."""
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return "ok"


@mcp.tool()
def call_my_ai_tool(endpoint: str, payload_json: str) -> str:
    """
    Proxy to your internal AI tools API.
    - endpoint: e.g. 'summarize' or 'classify'
    - payload_json: raw JSON string (keeps this generic)
    """
    base = os.environ.get("MY_AI_TOOLS_BASE_URL", "").rstrip("/")
    if not base:
        raise ValueError("MY_AI_TOOLS_BASE_URL is not set")

    token = os.environ.get("MY_AI_TOOLS_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{base}/{endpoint.lstrip('/')}"
    r = requests.post(url, data=payload_json, headers=headers, timeout=60)
    r.raise_for_status()
    return r.text


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
