import os
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent_runner import run_task
from video_workflow import (
    VideoProjectStore,
    build_outline,
    build_production_checklist,
    build_scene_plan,
    build_scene_prompts,
)

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


class VideoProjectCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    idea: str = Field(min_length=10)
    audience: str = Field(min_length=3, max_length=120)
    target_duration_minutes: int = Field(default=8, ge=1, le=120)
    language: str = Field(default="en")
    visual_style: str = Field(default="cinematic educational")


class ScenePlan(BaseModel):
    scene_number: int
    goal: str
    duration_seconds: int
    camera: str
    key_visual: str


class ProjectPlanResponse(BaseModel):
    project_id: str
    outline: List[str]
    scenes: List[ScenePlan]
    production_checklist: List[str]


class PromptGenerationRequest(BaseModel):
    character_name: str = Field(min_length=2, max_length=120)
    character_description: str = Field(min_length=10)
    wardrobe: str = Field(default="smart casual")
    camera_style: str = Field(default="35mm medium shot")
    lighting_style: str = Field(default="soft key light")


class ScenePrompt(BaseModel):
    scene_number: int
    start_frame_prompt: str
    end_frame_prompt: str
    negative_prompt: str


class PromptGenerationResponse(BaseModel):
    project_id: str
    consistency_packet: Dict[str, str]
    scene_prompts: List[ScenePrompt]


video_store = VideoProjectStore(
    os.environ.get("VIDEO_PROJECTS_FILE", "/tmp/ai-agent-mcp/video-projects.json")
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
      <head>
        <title>AI Agent MCP Starter</title>
        <style>
          body {font-family: Arial, sans-serif; max-width: 1100px; margin: 1.5rem auto; color: #1e1e1e;}
          .grid {display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;}
          .card {border: 1px solid #ddd; border-radius: 10px; padding: 1rem; background: #fafafa;}
          input, textarea, select, button {width: 100%; box-sizing: border-box; margin-top: .5rem; padding: .6rem; border-radius: 8px; border: 1px solid #ccc;}
          button {background: #111827; color: #fff; border: none; cursor: pointer;}
          button:hover {background: #0b1220;}
          .inline {display:flex; gap:.75rem;}
          .inline > * {flex:1;}
          pre {background:#0f172a; color:#e2e8f0; padding:1rem; border-radius:10px; white-space: pre-wrap; min-height: 180px;}
          h2, h3 {margin: .4rem 0;}
        </style>
      </head>
      <body>
        <h2>AI Agent + Video Workflow Studio (Cloud Ready)</h2>
        <p>Use this page to run tasks and manage your long-form video planning workflow.</p>

        <div class="grid">
          <div class="card">
            <h3>1) Run Generic Agent Task</h3>
            <textarea id="task" rows="5" placeholder="Type your task here"></textarea>
            <label><input type="checkbox" id="approved" style="width:auto; margin-right:.4rem;"/>approved for sensitive actions</label>
            <button onclick="runTask()">Run Task</button>
          </div>

          <div class="card">
            <h3>2) Create Video Project</h3>
            <input id="title" placeholder="Project title" value="Long-form AI Tutorial"/>
            <textarea id="idea" rows="3" placeholder="Project idea">Build a long AI tutorial from concept to final export.</textarea>
            <div class="inline">
              <input id="audience" placeholder="Audience" value="content creators"/>
              <input id="duration" type="number" min="1" max="120" value="12"/>
            </div>
            <div class="inline">
              <input id="language" placeholder="Language" value="en"/>
              <input id="visualStyle" placeholder="Visual style" value="cinematic educational"/>
            </div>
            <button onclick="createProject()">Create Project</button>
          </div>

          <div class="card">
            <h3>3) Load / Plan</h3>
            <input id="projectId" placeholder="Project ID"/>
            <div class="inline">
              <button onclick="listProjects()">List Projects</button>
              <button onclick="loadProject()">Load Project</button>
            </div>
            <button onclick="generatePlan()">Generate Scene Plan</button>
          </div>

          <div class="card">
            <h3>4) Generate Scene Prompts</h3>
            <input id="characterName" placeholder="Character name" value="Omar"/>
            <textarea id="characterDescription" rows="2" placeholder="Character description">Middle eastern male educator with short beard and calm expression.</textarea>
            <div class="inline">
              <input id="wardrobe" placeholder="Wardrobe" value="dark blue shirt"/>
              <input id="cameraStyle" placeholder="Camera style" value="35mm medium shot"/>
            </div>
            <input id="lightingStyle" placeholder="Lighting style" value="soft key light"/>
            <button onclick="generatePrompts()">Generate Prompts</button>
          </div>
        </div>

        <h3>Output</h3>
        <pre id="out"></pre>

        <script>
          const out = document.getElementById('out');
          const show = (data) => out.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);

          async function api(path, options = {}) {
            const response = await fetch(path, {
              headers: {'Content-Type': 'application/json'},
              ...options,
            });
            const payload = await response.json();
            if (!response.ok) throw new Error(JSON.stringify(payload));
            return payload;
          }

          async function runTask() {
            try {
              show('Running task...');
              const payload = await api('/run', {
                method: 'POST',
                body: JSON.stringify({
                  task: document.getElementById('task').value,
                  approved: document.getElementById('approved').checked,
                }),
              });
              show(payload);
            } catch (error) {
              show(error.message);
            }
          }

          async function createProject() {
            try {
              show('Creating project...');
              const payload = await api('/video/projects', {
                method: 'POST',
                body: JSON.stringify({
                  title: document.getElementById('title').value,
                  idea: document.getElementById('idea').value,
                  audience: document.getElementById('audience').value,
                  target_duration_minutes: Number(document.getElementById('duration').value),
                  language: document.getElementById('language').value,
                  visual_style: document.getElementById('visualStyle').value,
                }),
              });
              document.getElementById('projectId').value = payload.id;
              show(payload);
            } catch (error) {
              show(error.message);
            }
          }

          async function listProjects() {
            try {
              show('Loading projects...');
              const payload = await api('/video/projects');
              show(payload);
            } catch (error) {
              show(error.message);
            }
          }

          async function loadProject() {
            try {
              const projectId = document.getElementById('projectId').value.trim();
              if (!projectId) return show('Please provide a project ID.');
              show('Loading project...');
              const payload = await api(`/video/projects/${projectId}`);
              show(payload);
            } catch (error) {
              show(error.message);
            }
          }

          async function generatePlan() {
            try {
              const projectId = document.getElementById('projectId').value.trim();
              if (!projectId) return show('Please provide a project ID.');
              show('Generating plan...');
              const payload = await api(`/video/projects/${projectId}/plan`, {method: 'POST'});
              show(payload);
            } catch (error) {
              show(error.message);
            }
          }

          async function generatePrompts() {
            try {
              const projectId = document.getElementById('projectId').value.trim();
              if (!projectId) return show('Please provide a project ID.');
              show('Generating prompts...');
              const payload = await api(`/video/projects/${projectId}/prompts`, {
                method: 'POST',
                body: JSON.stringify({
                  character_name: document.getElementById('characterName').value,
                  character_description: document.getElementById('characterDescription').value,
                  wardrobe: document.getElementById('wardrobe').value,
                  camera_style: document.getElementById('cameraStyle').value,
                  lighting_style: document.getElementById('lightingStyle').value,
                }),
              });
              show(payload);
            } catch (error) {
              show(error.message);
            }
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


@app.post("/video/projects")
async def create_video_project(req: VideoProjectCreateRequest):
    return video_store.create_project(
        title=req.title,
        idea=req.idea,
        audience=req.audience,
        target_duration_minutes=req.target_duration_minutes,
        language=req.language,
        visual_style=req.visual_style,
    )


@app.get("/video/projects")
async def list_video_projects():
    return {"projects": video_store.list_projects()}


@app.get("/video/projects/{project_id}")
async def get_video_project(project_id: str):
    project = video_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/video/projects/{project_id}/plan", response_model=ProjectPlanResponse)
async def build_project_plan(project_id: str):
    project = video_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    outline = build_outline(project["idea"])
    scenes = [ScenePlan(**scene.__dict__) for scene in build_scene_plan(project)]
    checklist = build_production_checklist()

    return ProjectPlanResponse(
        project_id=project_id,
        outline=outline,
        scenes=scenes,
        production_checklist=checklist,
    )


@app.post("/video/projects/{project_id}/prompts", response_model=PromptGenerationResponse)
async def generate_scene_prompts(project_id: str, req: PromptGenerationRequest):
    project = video_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenes = build_scene_plan(project)
    consistency_packet = {
        "character_name": req.character_name,
        "character_description": req.character_description,
        "wardrobe": req.wardrobe,
        "camera_style": req.camera_style,
        "lighting_style": req.lighting_style,
        "visual_style": project["visual_style"],
    }
    prompts = [
        ScenePrompt(**prompt)
        for prompt in build_scene_prompts(
            project=project,
            character={
                "character_name": req.character_name,
                "character_description": req.character_description,
                "wardrobe": req.wardrobe,
                "camera_style": req.camera_style,
                "lighting_style": req.lighting_style,
            },
            scenes=scenes,
        )
    ]

    return PromptGenerationResponse(
        project_id=project_id,
        consistency_packet=consistency_packet,
        scene_prompts=prompts,
    )
