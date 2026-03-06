import os
from datetime import datetime, timezone
from typing import Dict, List
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


class VideoProjectCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    idea: str = Field(min_length=10)
    audience: str = Field(min_length=3, max_length=120)
    target_duration_minutes: int = Field(default=8, ge=1, le=120)
    language: str = Field(default="ar")
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


VIDEO_PROJECTS: Dict[str, Dict] = {}


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
      <body style=\"font-family: Arial, sans-serif; max-width: 920px; margin: 2rem auto;\">
        <h2>AI Agent + MCP + Browser</h2>
        <p>Quick web runner for cloud deployments.</p>
        <form method=\"post\" action=\"/run\" onsubmit=\"return false;\">
          <textarea id=\"task\" rows=\"6\" style=\"width:100%;\" placeholder=\"اكتب المهمة هنا\"></textarea><br/><br/>
          <label><input type=\"checkbox\" id=\"approved\"/> approved (for sensitive actions)</label><br/><br/>
          <button onclick=\"runTask()\">Run</button>
        </form>
        <h3>New: Video workflow planning endpoints</h3>
        <ul>
          <li><code>POST /video/projects</code></li>
          <li><code>POST /video/projects/{project_id}/plan</code></li>
          <li><code>POST /video/projects/{project_id}/prompts</code></li>
        </ul>
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


@app.post("/video/projects")
async def create_video_project(req: VideoProjectCreateRequest):
    project_id = str(uuid4())
    VIDEO_PROJECTS[project_id] = {
        "id": project_id,
        "title": req.title,
        "idea": req.idea,
        "audience": req.audience,
        "target_duration_minutes": req.target_duration_minutes,
        "language": req.language,
        "visual_style": req.visual_style,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return VIDEO_PROJECTS[project_id]


@app.get("/video/projects/{project_id}")
async def get_video_project(project_id: str):
    project = VIDEO_PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/video/projects/{project_id}/plan", response_model=ProjectPlanResponse)
async def build_project_plan(project_id: str):
    project = VIDEO_PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total_seconds = project["target_duration_minutes"] * 60
    scenes_count = 6
    scene_seconds = max(20, total_seconds // scenes_count)

    outline = [
        f"Hook قوي مرتبط بـ {project['idea']}",
        "تحديد المشكلة ولماذا تهم المشاهد الآن",
        "شرح المنهج خطوة بخطوة مع أمثلة",
        "عرض النتائج مع لقطات مقارنة قبل/بعد",
        "أخطاء شائعة وكيف تتجنبها",
        "CTA واضح للخطوة التالية",
    ]

    scenes = [
        ScenePlan(
            scene_number=idx + 1,
            goal=goal,
            duration_seconds=scene_seconds,
            camera="medium shot with slow push-in",
            key_visual=f"Visual for: {goal}",
        )
        for idx, goal in enumerate(outline)
    ]

    checklist = [
        "راجع ثبات الشخصية (face, hair, wardrobe) قبل أي توليد",
        "ولّد start/end frame لكل مشهد ثم image-to-video",
        "أنشئ voice-over بعد تثبيت توقيت المشاهد",
        "راجع transitions الصوت والصورة على timeline",
        "صدر نسخة draft ثم نسخة final بدقة أعلى",
    ]

    return ProjectPlanResponse(
        project_id=project_id,
        outline=outline,
        scenes=scenes,
        production_checklist=checklist,
    )


@app.post("/video/projects/{project_id}/prompts", response_model=PromptGenerationResponse)
async def generate_scene_prompts(project_id: str, req: PromptGenerationRequest):
    project = VIDEO_PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    plan = await build_project_plan(project_id)

    consistency_packet = {
        "character_name": req.character_name,
        "character_description": req.character_description,
        "wardrobe": req.wardrobe,
        "camera_style": req.camera_style,
        "lighting_style": req.lighting_style,
        "visual_style": project["visual_style"],
    }

    prompts = []
    for scene in plan.scenes:
        base = (
            f"{req.character_name}, {req.character_description}, wardrobe: {req.wardrobe}, "
            f"camera: {req.camera_style}, lighting: {req.lighting_style}, "
            f"style: {project['visual_style']}, scene goal: {scene.goal}"
        )
        prompts.append(
            ScenePrompt(
                scene_number=scene.scene_number,
                start_frame_prompt=f"START FRAME | {base} | composition: establishing frame",
                end_frame_prompt=f"END FRAME | {base} | composition: narrative payoff frame",
                negative_prompt="low quality, deformed face, inconsistent identity, extra limbs, blurry",
            )
        )

    return PromptGenerationResponse(
        project_id=project_id,
        consistency_packet=consistency_packet,
        scene_prompts=prompts,
    )
