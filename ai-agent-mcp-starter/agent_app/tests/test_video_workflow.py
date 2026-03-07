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
                owner_id="u1",
                title="Cloud Project",
                idea="Workflow for long-form AI videos",
                audience="creators",
                target_duration_minutes=12,
                language="en",
                visual_style="cinematic",
            )

            reloaded_store = VideoProjectStore(str(storage_file))
            loaded = reloaded_store.get_project(created["id"], "u1")

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["title"], "Cloud Project")
            self.assertIn("updated_at", loaded)
            self.assertEqual(loaded["owner_id"], "u1")

    def test_list_projects_returns_latest_first_and_owner_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage_file = Path(tmp) / "video-projects.json"
            store = VideoProjectStore(str(storage_file))
            first = store.create_project(
                owner_id="u1",
                title="First",
                idea="First workflow",
                audience="creators",
                target_duration_minutes=10,
                language="en",
                visual_style="cinematic",
            )
            second = store.create_project(
                owner_id="u1",
                title="Second",
                idea="Second workflow",
                audience="creators",
                target_duration_minutes=10,
                language="en",
                visual_style="cinematic",
            )
            store.create_project(
                owner_id="u2",
                title="Other Owner",
                idea="Other owner workflow",
                audience="creators",
                target_duration_minutes=10,
                language="en",
                visual_style="cinematic",
            )

            listed = store.list_projects("u1")
            self.assertEqual(len(listed), 2)
            self.assertEqual(listed[0]["id"], second["id"])
            self.assertEqual(listed[1]["id"], first["id"])

    def test_update_delete_and_save_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage_file = Path(tmp) / "video-projects.json"
            store = VideoProjectStore(str(storage_file))
            created = store.create_project(
                owner_id="u1",
                title="Original",
                idea="Original idea text",
                audience="creators",
                target_duration_minutes=9,
                language="en",
                visual_style="cinematic",
            )

            updated = store.update_project(created["id"], "u1", {"title": "Updated Title"})
            self.assertIsNotNone(updated)
            self.assertEqual(updated["title"], "Updated Title")

            save_plan_result = store.save_plan(created["id"], "u1", {"outline": ["one", "two"]})
            self.assertIsNotNone(save_plan_result)
            self.assertIn("last_plan", save_plan_result)
            self.assertEqual(len(save_plan_result["plan_versions"]), 1)

            save_prompts_result = store.save_prompts(created["id"], "u1", {"scene_prompts": [1, 2]})
            self.assertIsNotNone(save_prompts_result)
            self.assertIn("last_prompts", save_prompts_result)
            self.assertEqual(len(save_prompts_result["prompt_versions"]), 1)

            deleted = store.delete_project(created["id"], "u1")
            self.assertTrue(deleted)
            self.assertIsNone(store.get_project(created["id"], "u1"))

    def test_prompt_generation_matches_scene_count(self):
        project = {
            "id": "p1",
            "owner_id": "u1",
            "title": "Video",
            "idea": "Explain AI production pipeline",
            "audience": "creators",
            "target_duration_minutes": 10,
            "language": "en",
            "visual_style": "cinematic educational",
            "created_at": "2025-01-01T00:00:00+00:00",
            "updated_at": "2025-01-01T00:00:00+00:00",
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
