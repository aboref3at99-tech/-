import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List
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
        self._projects: Dict[str, Dict] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.storage_file):
            return
        with open(self.storage_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            self._projects = data

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self._projects, f, ensure_ascii=False, indent=2)

    def create_project(
        self,
        title: str,
        idea: str,
        audience: str,
        target_duration_minutes: int,
        language: str,
        visual_style: str,
    ) -> Dict:
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

        with self._lock:
            self._projects[project.id] = asdict(project)
            self._persist()
        return asdict(project)

    def get_project(self, project_id: str) -> Dict | None:
        with self._lock:
            return self._projects.get(project_id)


def build_outline(idea: str) -> List[str]:
    return [
        f"Hook قوي مرتبط بـ {idea}",
        "تحديد المشكلة ولماذا تهم المشاهد الآن",
        "شرح المنهج خطوة بخطوة مع أمثلة",
        "عرض النتائج مع لقطات مقارنة قبل/بعد",
        "أخطاء شائعة وكيف تتجنبها",
        "CTA واضح للخطوة التالية",
    ]


def build_scene_plan(project: Dict) -> List[ScenePlanItem]:
    outline = build_outline(project["idea"])
    total_seconds = project["target_duration_minutes"] * 60
    scenes_count = len(outline)
    scene_seconds = max(20, total_seconds // scenes_count)

    return [
        ScenePlanItem(
            scene_number=idx + 1,
            goal=goal,
            duration_seconds=scene_seconds,
            camera="medium shot with slow push-in",
            key_visual=f"Visual for: {goal}",
        )
        for idx, goal in enumerate(outline)
    ]


def build_production_checklist() -> List[str]:
    return [
        "راجع ثبات الشخصية (face, hair, wardrobe) قبل أي توليد",
        "ولّد start/end frame لكل مشهد ثم image-to-video",
        "أنشئ voice-over بعد تثبيت توقيت المشاهد",
        "راجع transitions الصوت والصورة على timeline",
        "صدر نسخة draft ثم نسخة final بدقة أعلى",
    ]


def build_scene_prompts(project: Dict, character: Dict, scenes: List[ScenePlanItem]) -> List[Dict[str, str | int]]:
    prompts: List[Dict[str, str | int]] = []
    for scene in scenes:
        base = (
            f"{character['character_name']}, {character['character_description']}, wardrobe: {character['wardrobe']}, "
            f"camera: {character['camera_style']}, lighting: {character['lighting_style']}, "
            f"style: {project['visual_style']}, scene goal: {scene.goal}"
        )
        prompts.append(
            {
                "scene_number": scene.scene_number,
                "start_frame_prompt": f"START FRAME | {base} | composition: establishing frame",
                "end_frame_prompt": f"END FRAME | {base} | composition: narrative payoff frame",
                "negative_prompt": "low quality, deformed face, inconsistent identity, extra limbs, blurry",
            }
        )
    return prompts
