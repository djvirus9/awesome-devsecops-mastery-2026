import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import yaml


SPEC = importlib.util.spec_from_file_location(
    "repository_validation", Path(__file__).resolve().parents[1] / "scripts/validate_repository.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RepositoryValidationTests(unittest.TestCase):
    def test_links_check_reference_targets_and_skip_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "read me.md").touch()
            text = """[Existing](read%20me.md#unchecked-anchor)
[Reference][guide]
[guide]: <read me.md>
[Missing](missing.md)
```markdown
[Not real](example-only.md)
```
`[Inline example](also-not-real.md)`
<!-- [Comment](not-real.md) -->
[External](https://example.invalid/a)
"""
            report = validator.Report()
            validator.check_markdown(root, Path("README.md"), text, report)
            self.assertEqual(report.counts["local_links"], 3)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("README.md:4", report.errors[0])
            self.assertIn("missing.md", report.errors[0])

    def test_on_key_survives_and_mutable_action_is_rejected(self):
        text = """name: Example
on: [push, pull_request]
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567
      - name: Validate
        run: python3 scripts/validate_repository.py
"""
        data = yaml.load(text, Loader=validator.UniqueBaseLoader)
        self.assertIn("on", data)
        report = validator.Report()
        validator.check_workflow(Path("workflow.yml"), data, report)
        self.assertEqual(report.errors, [])
        data["jobs"]["check"]["steps"][0]["uses"] = "actions/checkout@v4"
        report = validator.Report()
        validator.check_workflow(Path("workflow.yml"), data, report)
        self.assertEqual(len(report.errors), 1)
        self.assertIn("40-character", report.errors[0])

    def test_fake_scan_and_unrestricted_permissions_are_flagged(self):
        data = {
            "on": ["push"], "permissions": "write-all",
            "jobs": {"scan": {"runs-on": "ubuntu-latest", "steps": [
                {"name": "SAST scan", "run": 'echo "Scan complete"'},
                {"uses": "docker://example.invalid/check:latest"},
            ]}},
        }
        report = validator.Report()
        validator.check_workflow(Path("workflow.yml"), data, report)
        self.assertTrue(any("write-all" in error for error in report.errors))
        self.assertTrue(any("only prints" in error for error in report.errors))
        self.assertTrue(any("sha256 digest" in error for error in report.errors))

    def test_duplicate_yaml_json_and_nonfinite_json_are_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "duplicate.yaml").write_text("permissions: {}\npermissions: write-all\n")
            (root / "duplicate.json").write_text('{"value": 1, "value": 2}')
            (root / "nonfinite.json").write_text('{"value": NaN}')
            report = validator.validate(root, ["duplicate.yaml", "duplicate.json", "nonfinite.json"])
            self.assertEqual(len(report.errors), 3)
            self.assertTrue(any("duplicate key" in error for error in report.errors))
            self.assertTrue(any("duplicate JSON" in error for error in report.errors))
            self.assertTrue(any("non-standard JSON" in error for error in report.errors))

    def test_original_scanner_and_signer_defects_are_flagged(self):
        report = validator.Report()
        validator.check_config(Path("configs/trivy.yaml"), {
            "exit-code": "0", "severity": "CRITICAL,HIGH", "scan": {"security-checks": ["vuln"]},
        }, report)
        validator.check_config(Path("configs/syft.yaml"), {"output": [{"format": "cyclonedx-json"}]}, report)
        validator.check_config(Path("configs/cosign-policy.yaml"), {
            "kind": "ClusterImagePolicy", "spec": {
                "images": [{"glob": "ghcr.io/example/app:*"}],
                "authorities": [{"keyless": {"identities": [{"issuer": "https://example.invalid"}]}}],
            },
        }, report)
        self.assertEqual(len(report.errors), 5)
        self.assertTrue(any("nonzero exit-code" in error for error in report.errors))
        self.assertTrue(any("signer subject" in error for error in report.errors))

    def test_pending_paths_skip_deleted_and_ignored_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "archive").mkdir()
            (root / "archive/old.md").write_text("[Old](missing.md)")
            (root / "pending.md").write_text("[Broken](missing.md)")
            report = validator.validate(root, ["deleted.md", "archive/old.md", "pending.md"])
            self.assertEqual(report.counts["files"], 1)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("pending.md", report.errors[0])

    def test_copied_starter_without_git_metadata_is_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[Config](config.yaml)\n[Missing](not-created.md)")
            (root / "config.yaml").write_text("valid: true\n")
            (root / ".tools").mkdir()
            (root / ".tools/generated.json").write_text("not JSON")
            with mock.patch.object(validator.subprocess, "run", side_effect=AssertionError("a plain copy must not invoke Git")):
                report = validator.validate(root)
            self.assertEqual(report.counts["files"], 2)
            self.assertEqual(report.counts["yaml"], 1)
            self.assertEqual(len(report.errors), 1)
            self.assertIn("not-created.md", report.errors[0])


if __name__ == "__main__":
    unittest.main()
