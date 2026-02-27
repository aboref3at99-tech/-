# Desktop App (Laptop)

A simple Tkinter desktop client that talks to the agent API.

## Run

```bash
cd ai-agent-mcp-starter
python desktop_app/app.py
```

By default it calls:

- `http://127.0.0.1:8000/run`

You can override via env var:

```bash
AGENT_API_URL="https://your-agent-domain/run" python desktop_app/app.py
```

## Build executable (optional)

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed desktop_app/app.py --name ai-agent-mcp-desktop
```

The executable will be under `dist/`.
