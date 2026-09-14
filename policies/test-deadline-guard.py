#!/usr/bin/env python3
"""Evaluate generated deadline guards using the pinned offline Kyverno CLI."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("exception_renderer", ROOT / "render-exception.py")
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


def main():
    # Fixed distant dates make both temporal branches deterministic. The live
    # harness separately proves the transition without replacing either object.
    exception = yaml.safe_load((ROOT / "kyverno/tests/exception-active/exception.yaml").read_text())
    cases = [
        ("active-missing", "missing-limits", "2099", "pass", None),
        ("active-compliant", "good", "2099", "pass", None),
        ("expired-missing", "missing-limits", "2000", "fail", None),
        ("expired-corrected-same-name", "good", "2000", "pass", None),
        ("active-init-missing", "init-missing-limits", "2099", "pass", None),
        ("expired-init-missing", "init-missing-limits", "2000", "fail", None),
        ("expired-other-name", "missing-limits", "2000", "skip", {"name": "other-pod"}),
        ("expired-other-namespace", "missing-limits", "2000", "skip", {"namespace": "other-namespace"}),
        ("expired-zero-limits", "zero-limits", "2000", "fail", None),
    ]
    with tempfile.TemporaryDirectory(prefix="devsecops-deadline-fixtures-") as temporary:
        for name, fixture, year, expected, metadata in cases:
            directory = Path(temporary) / name
            directory.mkdir()
            case_exception = copy.deepcopy(exception)
            case_exception["spec"]["expiresAt"] = year + "-01-01T00:00:00Z"
            guard = renderer.deadline_guard(case_exception)
            path = ROOT / "fixtures" / (fixture + ".yaml")
            obj = yaml.safe_load(path.read_text())
            obj["metadata"].update({"name": "missing-limits", "namespace": "devsecops-reference", **(metadata or {})})
            (directory / "guard.yaml").write_text(yaml.safe_dump(guard))
            (directory / "resource.yaml").write_text(yaml.safe_dump(obj))
            test = {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Test", "metadata": {"name": name},
                    "policies": ["guard.yaml"], "resources": ["resource.yaml"], "results": [{
                        "isValidatingPolicy": True, "policy": renderer.GUARD_NAME, "kind": obj["kind"],
                        "resources": [obj["metadata"]["name"]], "result": expected}]}
            (directory / "kyverno-test.yaml").write_text(yaml.safe_dump(test))
        return subprocess.run([sys.argv[1], "test", temporary, "--fail-only"], timeout=120).returncode


if __name__ == "__main__":
    raise SystemExit(main())
