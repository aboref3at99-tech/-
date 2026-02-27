import json
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from urllib import request, error

DEFAULT_API_URL = os.environ.get("AGENT_API_URL", "http://127.0.0.1:8000/run")


class DesktopAgentApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Agent MCP Desktop")
        self.root.geometry("920x640")

        frame = ttk.Frame(root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Agent API URL:").pack(anchor="w")
        self.api_url_var = tk.StringVar(value=DEFAULT_API_URL)
        ttk.Entry(frame, textvariable=self.api_url_var).pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Task:").pack(anchor="w")
        self.task_text = tk.Text(frame, height=10, wrap="word")
        self.task_text.pack(fill="x")

        self.approved_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="approved (required for sensitive actions)",
            variable=self.approved_var,
        ).pack(anchor="w", pady=(8, 8))

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 8))
        self.run_btn = ttk.Button(controls, text="Run Task", command=self.on_run)
        self.run_btn.pack(side="left")
        ttk.Button(controls, text="Clear", command=self.clear).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Output:").pack(anchor="w")
        self.output_text = tk.Text(frame, height=18, wrap="word")
        self.output_text.pack(fill="both", expand=True)

    def clear(self):
        self.task_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

    def on_run(self):
        task = self.task_text.get("1.0", "end").strip()
        if not task:
            messagebox.showwarning("Missing task", "Please enter a task first.")
            return

        self.run_btn.config(state="disabled")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "Running...\n")

        payload = {
            "task": task,
            "approved": self.approved_var.get(),
        }
        threading.Thread(target=self._call_api, args=(payload,), daemon=True).start()

    def _call_api(self, payload: dict):
        url = self.api_url_var.get().strip()
        try:
            req = request.Request(
                url=url,
                method="POST",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with request.urlopen(req, timeout=300) as resp:
                body = resp.read().decode("utf-8")
                parsed = json.loads(body)
                output = parsed.get("output", body)
                self._set_output(str(output))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            self._set_output(f"HTTP {exc.code}\n{body}")
        except Exception as exc:  # noqa: BLE001
            self._set_output(f"Request failed: {exc}")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))

    def _set_output(self, text: str):
        def _ui_update():
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", text)

        self.root.after(0, _ui_update)


def main():
    root = tk.Tk()
    app = DesktopAgentApp(root)
    app.task_text.insert("end", "افتح ويكيبيديا وروح لصفحة OpenAI وخدلي ملخص قصير.")
    root.mainloop()


if __name__ == "__main__":
    main()
