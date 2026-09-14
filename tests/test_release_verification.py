"""Guard the actual CLI policy used by the manual publishing workflow."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_release", ROOT / "scripts/verify_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)
REPOSITORY = "djvirus9/awesome-devsecops-mastery-2026"
COMMIT = "a" * 40
IMAGE = "ghcr.io/" + REPOSITORY + "/sample-api@sha256:" + "b" * 64


class ReleaseVerificationTests(unittest.TestCase):
    def test_identity_options_are_not_mutually_exclusive(self):
        command = release.verification_command(REPOSITORY, COMMIT, IMAGE)
        self.assertIn("--cert-identity", command)
        for incompatible in ("--signer-workflow", "--signer-repo", "--cert-identity-regex"):
            self.assertNotIn(incompatible, command)
        self.assertIn(f"https://github.com/{REPOSITORY}/.github/workflows/release.yml@refs/heads/main", command)

    def test_source_issuer_hosted_runner_and_registry_bundle_are_required(self):
        command = release.verification_command(REPOSITORY, COMMIT, IMAGE)
        for flag, value in (("--repo", REPOSITORY), ("--source-digest", COMMIT),
                            ("--source-ref", "refs/heads/main"),
                            ("--cert-oidc-issuer", "https://token.actions.githubusercontent.com")):
            self.assertEqual(command[command.index(flag) + 1], value)
        self.assertIn("--deny-self-hosted-runners", command)
        self.assertIn("--bundle-from-oci", command)

    def test_mutable_cross_repository_and_invalid_inputs_fail_before_execution(self):
        for repo, commit, image in (
            (REPOSITORY, COMMIT, IMAGE.split("@")[0] + ":latest"),
            (REPOSITORY, COMMIT, IMAGE.replace("djvirus9", "someone-else")),
            (REPOSITORY, "main", IMAGE),
            ("--bad/repository", COMMIT, IMAGE),
            (REPOSITORY, COMMIT, IMAGE + "extra"),
        ):
            with self.subTest(repo=repo, commit=commit, image=image), self.assertRaises(ValueError):
                release.verification_command(repo, commit, image)

    def test_failed_verification_does_not_create_success_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            with mock.patch.object(release.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "gh")):
                with self.assertRaises(subprocess.CalledProcessError):
                    release.verify(REPOSITORY, COMMIT, IMAGE, output)
            self.assertFalse(output.exists())

    def test_empty_evidence_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            for payload in ("[]", "{}", "null"):
                with mock.patch.object(release.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, payload)):
                    with self.assertRaises(ValueError):
                        release.verify(REPOSITORY, COMMIT, IMAGE, Path(directory) / "report.json")

    def test_successful_verification_retains_cli_evidence(self):
        evidence = [{"verificationResult": {"verified": True}}]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            with mock.patch.object(release.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(evidence))) as run:
                release.verify(REPOSITORY, COMMIT, IMAGE, output)
            self.assertTrue(run.call_args.kwargs["check"])
            self.assertEqual(json.loads(output.read_text()), evidence)


if __name__ == "__main__":
    unittest.main()
