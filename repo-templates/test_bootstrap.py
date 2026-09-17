"""Template safety and completeness behavior, using disposable synthetic sources."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "bootstrap_template", Path(__file__).resolve().parents[1] / "scripts/bootstrap_template.py"
)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.source = Path(self.workspace.name) / "source"
        self.source.mkdir()
        for name in bootstrap.REQUIRED_PATHS:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic fixture\n")
        self.destination = Path(self.workspace.name) / "generated"

    def test_copy_preserves_workflow_paths_and_records_hashes(self):
        bootstrap.bootstrap(self.source, self.destination, "microservice")
        for name in bootstrap.REQUIRED_PATHS:
            self.assertEqual((self.destination / name).read_bytes(), (self.source / name).read_bytes())
        manifest = json.loads((self.destination / "template-manifest.json").read_text())
        self.assertEqual(manifest["profile"], "microservice")
        self.assertIn(".github/workflows/devsecops-golden-pipeline.yml", manifest["sha256"])
        self.assertTrue((self.destination / "TEMPLATE-SETUP.md").is_file())
        self.assertFalse((self.destination / ".git").exists())

    def test_existing_destination_is_preserved(self):
        self.destination.mkdir()
        marker = self.destination / "user-file.txt"
        marker.write_text("keep me")
        with self.assertRaisesRegex(ValueError, "must not exist"):
            bootstrap.bootstrap(self.source, self.destination, "microservice")
        self.assertEqual(marker.read_text(), "keep me")

    def test_broken_destination_symlink_is_preserved(self):
        absent = Path(self.workspace.name) / "absent-target"
        self.destination.symlink_to(absent)
        with self.assertRaisesRegex(ValueError, "must not exist"):
            bootstrap.bootstrap(self.source, self.destination, "microservice")
        self.assertTrue(self.destination.is_symlink())
        self.assertFalse(absent.exists())

    def test_missing_dependency_fails_before_creating_destination(self):
        (self.source / "tool-versions.json").unlink()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            bootstrap.bootstrap(self.source, self.destination, "microservice")
        self.assertFalse(self.destination.exists())

    def test_cache_credentials_and_symlinks_are_not_copied(self):
        for name in ("samples/.env", "samples/.env.local", "samples/key.pem", "samples/__pycache__/cache.pyc"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not for copying")
        bootstrap.bootstrap(self.source, self.destination, "k8s-app")
        self.assertFalse((self.destination / "samples/.env").exists())
        self.assertFalse((self.destination / "samples/key.pem").exists())
        self.assertFalse((self.destination / "samples/__pycache__").exists())

    def test_symlink_source_is_rejected(self):
        (self.source / "samples/linked.py").symlink_to(self.source / "samples/sample-api/app.py")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            bootstrap.bootstrap(self.source, self.destination, "microservice")

    def test_destination_inside_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            bootstrap.bootstrap(self.source, self.source / "new-template", "microservice")

    def test_dry_run_validates_without_creating(self):
        report = bootstrap.bootstrap(self.source, self.destination, "serverless", dry_run=True)
        self.assertTrue(report["dry_run"])
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
