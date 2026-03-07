import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class VideoProject:
    id: str
    title: str
    idea: str
    audience: str
    target_duration_minutes: int
    language: str
    visual_style: str
    created_at: str


@dataclass
class ScenePlanItem:
    scene_number: int
    goal: str
    duration_seconds: int
    camera: str
    key_visual: str


class VideoProjectStore:
    def __init__(self, storage_file: str):
        self.storage_file = storage_file
        self._lock = Lock()
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.storage_file):
            return

        with open(self.storage_file, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)

        if isinstance(data, dict):
            self._projects = data

    def _persist(self) -> None:
        directory = os.path.dirname(self.storage_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.storage_file, "w", encoding="utf-8") as file_handle:
            json.dump(self._projects, file_handle, ensure_ascii=False, indent=2)

    def create_project(
        self,
        title: str,
        idea: str,
        audience: str,
        target_duration_minutes: int,
        language: str,
        visual_style: str,
    ) -> Dict[str, Any]:
        project = VideoProject(
            id=str(uuid4()),
            title=title,
            idea=idea,
            audience=audience,
            target_duration_minutes=target_duration_minutes,
            language=language,
            visual_style=visual_style,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        project_payload = asdict(project)
        with self._lock:
            self._projects[project.id] = project_payload
            self._persist()

        return project_payload

    def get_project(self, project_id: str) -> Dict[str, Any] | None:
        with self._lock:
            return self._projects.get(project_id)

    def list_projects(self) -> List[Dict[str, Any]]:
        with self._lock:
            projects = list(self._projects.values())

        return sorted(projects, key=lambda item: item.get("created_at", ""), reverse=True)


def build_outline(idea: str) -> List[str]:
    return [
        f"Open with a strong hook tied to: {idea}",
        "Frame the core problem and explain why it matters right now",
        "Break down the method step by step with practical examples",
        "Show before/after outcomes to highlight the transformation",
        "Cover common mistakes and how to avoid them",
        "Close with a clear call-to-action for the viewer",
    ]


def build_scene_plan(project: Dict[str, Any]) -> List[ScenePlanItem]:
    outline = build_outline(project["idea"])
    total_seconds = int(project["target_duration_minutes"]) * 60
    scene_seconds = max(20, total_seconds // len(outline))

    return [
        ScenePlanItem(
            scene_number=index + 1,
            goal=goal,
            duration_seconds=scene_seconds,
            camera="medium shot with slow push-in",
            key_visual=f"Visual direction: {goal}",
        )
        for index, goal in enumerate(outline)
    ]


def build_production_checklist() -> List[str]:
    return [
        "Validate character consistency (face, hair, wardrobe) before generation",
        "Generate start and end frames for each scene before image-to-video",
        "Create voice-over after scene timing is locked",
        "Review visual and audio transitions on the timeline",
        "Export draft first, then render final output at higher quality",
    ]


def build_scene_prompts(
    project: Dict[str, Any],
    character: Dict[str, str],
    scenes: List[ScenePlanItem],
) -> List[Dict[str, str | int]]:
    prompts: List[Dict[str, str | int]] = []
    for scene in scenes:
        base_prompt = (
            f"{character['character_name']}, {character['character_description']}, wardrobe: {character['wardrobe']}, "
            f"camera: {character['camera_style']}, lighting: {character['lighting_style']}, "
            f"style: {project['visual_style']}, scene objective: {scene.goal}"
        )
        prompts.append(
            {
                "scene_number": scene.scene_number,
                "start_frame_prompt": f"START FRAME | {base_prompt} | composition: establishing shot",
                "end_frame_prompt": f"END FRAME | {base_prompt} | composition: payoff shot",
                "negative_prompt": "low quality, deformed face, inconsistent identity, extra limbs, blurry",
            }
        )

    return prompts
