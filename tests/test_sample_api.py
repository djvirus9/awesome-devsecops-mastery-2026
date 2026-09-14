"""Authorization regression tests use Flask's in-process client only."""

import importlib.util
import json
from pathlib import Path
import unittest

API_PATH = Path(__file__).resolve().parents[1] / "samples/sample-api/app.py"
SPEC = importlib.util.spec_from_file_location("sample_api", API_PATH)
api = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(api)


class SampleApiTests(unittest.TestCase):
    def setUp(self):
        self.app = api.create_app({"TESTING": True, "API_TOKENS_JSON": json.dumps({
            "demo-alice-token": "alice", "demo-bob-token": "bob",
        })})
        self.client = self.app.test_client()

    def get(self, path, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token is not None else {}
        return self.client.get(path, headers=headers)

    def test_health_is_public(self):
        self.assertEqual(self.get("/health").json, {"status": "ok"})

    def test_credentials_required_for_both_protected_routes(self):
        for path in ("/v1/items", "/v1/items/item-1"):
            for token in (None, "invalid", "", "x" * 257, "non-ascii-\u00e9"):
                with self.subTest(path=path, token=token):
                    self.assertEqual(self.get(path, token).status_code, 401)

    def test_list_filters_by_owner(self):
        self.assertEqual([x["id"] for x in self.get("/v1/items", "demo-alice-token").json["items"]], ["item-1"])
        self.assertEqual([x["id"] for x in self.get("/v1/items", "demo-bob-token").json["items"]], ["item-2"])

    def test_item_access_requires_ownership(self):
        self.assertEqual(self.get("/v1/items/item-1", "demo-alice-token").status_code, 200)
        wrong_owner = self.get("/v1/items/item-1", "demo-bob-token")
        absent = self.get("/v1/items/absent", "demo-bob-token")
        self.assertEqual(wrong_owner.status_code, 404)
        self.assertEqual(wrong_owner.json, absent.json)

    def test_no_default_access_without_configured_tokens(self):
        client = api.create_app({"TESTING": True, "API_TOKENS_JSON": "{}"}).test_client()
        self.assertEqual(client.get("/v1/items", headers={"Authorization": "Bearer demo-alice-token"}).status_code, 401)

    def test_invalid_configuration_does_not_echo_secrets(self):
        for raw in ('{"private-value":', '[]', '{"": "alice"}', '{"private-value": 3}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError) as failure:
                api.load_tokens(raw)
            self.assertNotIn("private-value", str(failure.exception))

    def test_logs_and_responses_do_not_echo_credentials(self):
        with self.assertLogs(self.app.logger, level="WARNING") as captured:
            response = self.get("/v1/items", "unrecognized-private-token")
        self.assertNotIn("unrecognized-private-token", " ".join(captured.output))
        self.assertNotIn("unrecognized-private-token", response.get_data(as_text=True))
        self.assertIn('"event": "request_denied"', " ".join(captured.output))

    def test_cache_and_content_headers_apply_to_failures_too(self):
        for path in ("/health", "/v1/items", "/missing"):
            response = self.get(path)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")


if __name__ == "__main__":
    unittest.main()
