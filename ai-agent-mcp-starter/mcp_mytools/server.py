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
    path = (WORKSPACE / rel_path).resolve()
    if WORKSPACE not in path.parents and path != WORKSPACE:
        raise ValueError("Path is outside workspace")
    return path


@mcp.tool()
def list_files() -> list[str]:
    """List all files under workspace recursively."""
    return [
        str(path.relative_to(WORKSPACE))
        for path in WORKSPACE.rglob("*")
        if path.is_file()
    ]


@mcp.tool()
def read_file(path: str) -> str:
    """Read a UTF-8 text file from workspace."""
    safe = _safe_path(path)
    return safe.read_text(encoding="utf-8")


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write a UTF-8 text file to workspace and create missing directories."""
    safe = _safe_path(path)
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_text(content, encoding="utf-8")
    return "ok"


@mcp.tool()
def call_my_ai_tool(endpoint: str, payload_json: str) -> str:
    """
    Proxy request to your internal AI tools API.

    Args:
        endpoint: Path after base URL (e.g. "summarize").
        payload_json: Raw JSON string body.
    """
    base = os.environ.get("MY_AI_TOOLS_BASE_URL", "").rstrip("/")
    if not base:
        raise ValueError("MY_AI_TOOLS_BASE_URL is not set")

    token = os.environ.get("MY_AI_TOOLS_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{base}/{endpoint.lstrip('/')}"
    response = requests.post(url, data=payload_json, headers=headers, timeout=60)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
