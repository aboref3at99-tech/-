import tempfile
import unittest
from pathlib import Path

from video_workflow import (
    VideoProjectStore,
    build_production_checklist,
    build_scene_plan,
    build_scene_prompts,
)


class VideoWorkflowTests(unittest.TestCase):
    def test_store_persists_projects_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage_file = Path(tmp) / "video-projects.json"
            store = VideoProjectStore(str(storage_file))
            created = store.create_project(
                title="Cloud Project",
                idea="Workflow for long-form AI videos",
                audience="creators",
                target_duration_minutes=12,
                language="en",
                visual_style="cinematic",
            )

            reloaded_store = VideoProjectStore(str(storage_file))
            loaded = reloaded_store.get_project(created["id"])

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["title"], "Cloud Project")

    def test_list_projects_returns_latest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage_file = Path(tmp) / "video-projects.json"
            store = VideoProjectStore(str(storage_file))
            first = store.create_project(
                title="First",
                idea="First workflow",
                audience="creators",
                target_duration_minutes=10,
                language="en",
                visual_style="cinematic",
            )
            second = store.create_project(
                title="Second",
                idea="Second workflow",
                audience="creators",
                target_duration_minutes=10,
                language="en",
                visual_style="cinematic",
            )

            listed = store.list_projects()
            self.assertEqual(listed[0]["id"], second["id"])
            self.assertEqual(listed[1]["id"], first["id"])

    def test_prompt_generation_matches_scene_count(self):
        project = {
            "id": "p1",
            "title": "Video",
            "idea": "Explain AI production pipeline",
            "audience": "creators",
            "target_duration_minutes": 10,
            "language": "en",
            "visual_style": "cinematic educational",
            "created_at": "2025-01-01T00:00:00+00:00",
        }
        scenes = build_scene_plan(project)
        prompts = build_scene_prompts(
            project=project,
            character={
                "character_name": "Omar",
                "character_description": "educator with calm expression",
                "wardrobe": "blue shirt",
                "camera_style": "35mm medium shot",
                "lighting_style": "soft key light",
            },
            scenes=scenes,
        )

        self.assertEqual(len(prompts), len(scenes))
        self.assertTrue(prompts[0]["start_frame_prompt"].startswith("START FRAME"))

    def test_checklist_is_english_and_non_empty(self):
        checklist = build_production_checklist()

        self.assertGreater(len(checklist), 0)
        self.assertIn("character consistency", checklist[0].lower())


if __name__ == "__main__":
    unittest.main()
