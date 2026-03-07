import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
except Exception:  # noqa: BLE001
    TestClient = None


@unittest.skipIf(TestClient is None, "fastapi test dependencies are unavailable")
class VideoApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        storage_file = Path(cls.temp_dir.name) / "video-projects.json"

        os.environ["VIDEO_PROJECTS_FILE"] = str(storage_file)
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["PLAYWRIGHT_MCP_URL"] = "http://playwright:8931/mcp"
        os.environ["MYTOOLS_MCP_URL"] = "http://mytools:8000/mcp"
        os.environ["RATE_LIMIT_MAX_REQUESTS"] = "500"

        fake_agent_runner = types.ModuleType("agent_runner")

        async def fake_run_task(task: str, approved: bool = False) -> str:
            return f"fake-output:{task}:{approved}"

        fake_agent_runner.run_task = fake_run_task
        sys.modules["agent_runner"] = fake_agent_runner

        import importlib

        if "app" in sys.modules:
            del sys.modules["app"]
        cls.app_module = importlib.import_module("app")
        cls.client = TestClient(cls.app_module.app)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_ready_endpoint(self):
        response = self.client.get("/ready")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("ready", payload)
        self.assertIn("checks", payload)
        self.assertTrue(payload["checks"]["OPENAI_API_KEY"]["ok"])

    def test_video_requires_user_header(self):
        response = self.client.get("/video/projects")
        self.assertEqual(response.status_code, 401)

    def test_video_project_lifecycle(self):
        headers = {"x-user-id": "u1"}

        create_response = self.client.post(
            "/video/projects",
            headers=headers,
            json={
                "title": "Integration Project",
                "idea": "Build a full API integration test project",
                "audience": "creators",
                "target_duration_minutes": 8,
                "language": "en",
                "visual_style": "cinematic educational",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        project = create_response.json()
        project_id = project["id"]

        list_response = self.client.get("/video/projects", headers=headers)
        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(len(list_response.json()["projects"]), 1)

        plan_response = self.client.post(f"/video/projects/{project_id}/plan", headers=headers)
        self.assertEqual(plan_response.status_code, 200)
        self.assertEqual(plan_response.json()["project_id"], project_id)

        prompts_response = self.client.post(
            f"/video/projects/{project_id}/prompts",
            headers=headers,
            json={
                "character_name": "Omar",
                "character_description": "educator with calm expression and short beard",
                "wardrobe": "blue shirt",
                "camera_style": "35mm medium shot",
                "lighting_style": "soft key light",
            },
        )
        self.assertEqual(prompts_response.status_code, 200)
        self.assertEqual(prompts_response.json()["project_id"], project_id)

        get_response = self.client.get(f"/video/projects/{project_id}", headers=headers)
        self.assertEqual(get_response.status_code, 200)
        project_payload = get_response.json()
        self.assertIn("last_plan", project_payload)
        self.assertIn("last_prompts", project_payload)
        self.assertEqual(len(project_payload["plan_versions"]), 1)
        self.assertEqual(len(project_payload["prompt_versions"]), 1)

        patch_response = self.client.patch(
            f"/video/projects/{project_id}",
            headers=headers,
            json={"title": "Updated Integration Project"},
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["title"], "Updated Integration Project")

        forbidden_read = self.client.get(f"/video/projects/{project_id}", headers={"x-user-id": "u2"})
        self.assertEqual(forbidden_read.status_code, 404)

        delete_response = self.client.delete(f"/video/projects/{project_id}", headers=headers)
        self.assertEqual(delete_response.status_code, 200)
        self.assertTrue(delete_response.json()["deleted"])


if __name__ == "__main__":
    unittest.main()
