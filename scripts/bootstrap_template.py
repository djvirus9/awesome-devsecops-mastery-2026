"""Copy the complete portable reference into a new local directory, without Git or network writes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


SOURCE_ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    "microservice": "projects/microservice-api/README.md",
    "k8s-app": "projects/k8s-gitops/README.md",
    "serverless": "projects/serverless-pipeline/README.md",
}
ROOT_FILES = (
    "README.md", "LICENSE", "CONTRIBUTING.md", "CONTRIBUTIONS.md", "CODEOWNERS",
    "CODE_OF_CONDUCT.md", "SECURITY.md", ".gitignore", ".python-version",
    ".pre-commit-config.yaml", "Makefile", "requirements-dev.in", "requirements-dev.txt",
    "tool-versions.json",
)
SOURCE_DIRECTORIES = (
    ".github", "scripts", "configs", "samples", "tests", "policies", "labs", "projects",
    "docs", "repo-templates", "templates", "dashboards", "metrics-templates", "scorecards",
    "evidence-packs", "checklists", "sdlc-checklists", "playbooks", "integrations", "recipes",
    "pipelines", "skill-maps", "archive",
)
REQUIRED_PATHS = (
    ".github/workflows/devsecops-golden-pipeline.yml", ".github/workflows/release.yml",
    ".pre-commit-config.yaml", "Makefile", "requirements-dev.txt", "tool-versions.json",
    "scripts/validate_repository.py", "scripts/install_tool.py", "scripts/container_smoke.py",
    "samples/sample-api/app.py", "policies/verify.sh", "tests/test_sample_api.py",
    "labs/lab-05-runtime-detection/test_detect.py",
)
EXCLUDED_PARTS = {".git", ".venv", ".tools", "__pycache__", ".pytest_cache", "reports", "node_modules"}


def excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts) or any(
        part == ".env" or part.startswith(".env.") or part == ".DS_Store"
        for part in path.parts
    ) or path.suffix in {".pyc", ".pyo", ".pem", ".key"}


def selected_files(source: Path) -> list[Path]:
    missing = [path for path in REQUIRED_PATHS if not (source / path).is_file()]
    if missing:
        raise ValueError("reference is incomplete; missing: " + ", ".join(missing))
    result = []
    candidates = [source / name for name in ROOT_FILES if (source / name).exists()]
    for name in SOURCE_DIRECTORIES:
        directory = source / name
        if directory.is_symlink():
            raise ValueError(f"source directory must not be a symlink: {name}")
        if directory.exists():
            candidates.extend(directory.rglob("*"))
    for path in candidates:
        relative = path.relative_to(source)
        if excluded(relative):
            continue
        if path.is_symlink():
            raise ValueError(f"source files must not be symlinks: {relative}")
        if path.is_file():
            result.append(relative)
    return sorted(set(result))


def revision(source: Path) -> dict:
    """Git metadata is informational; hashes identify the copied working-tree bytes."""
    if not (source / ".git").exists():
        return {"base_commit": None, "working_tree_dirty": None}
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=source, check=True,
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=source, check=True,
            capture_output=True, text=True, timeout=10,
        ).stdout)
        return {"base_commit": head, "working_tree_dirty": dirty}
    except (OSError, subprocess.SubprocessError):
        return {"base_commit": None, "working_tree_dirty": None}


def bootstrap(source: Path, destination: Path, profile: str, dry_run: bool = False) -> dict:
    source = source.resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError("destination must not exist; existing paths are never overwritten")
    destination = destination.resolve()
    if profile not in PROFILES:
        raise ValueError("unknown template profile")
    if destination == source or destination.is_relative_to(source):
        raise ValueError("destination must be outside the source repository")
    if destination.exists():
        raise ValueError("destination must not exist; existing directories are never overwritten")
    if not destination.parent.is_dir():
        raise ValueError("destination parent must already exist")
    files = selected_files(source)
    summary = {"profile": profile, "destination": str(destination), "files": len(files), "dry_run": dry_run}
    if dry_run:
        return summary

    # mkdir is exclusive, so a destination created after validation is not overwritten.
    destination.mkdir()
    inventory = {}
    for relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
        inventory[relative.as_posix()] = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {"profile": profile, "source": revision(source), "sha256": inventory}
    (destination / "template-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (destination / "TEMPLATE-SETUP.md").write_text(
        "# Generated reference setup\n\n"
        f"Profile: `{profile}`. This is the complete local reference, with an extension guide at "
        f"[{PROFILES[profile]}]({PROFILES[profile]}).\n\n"
        "Start with `make setup`, `make test`, and `make validate`. See "
        "[tool installation and optional checks](docs/validation.md). The workflow at "
        "`.github/workflows/devsecops-golden-pipeline.yml` is a local copy of the canonical workflow; "
        "all shared source, locks, configurations, fixtures, and scripts are included.\n\n"
        "No Git repository was initialized, remote contacted, dependency installed, or release triggered. "
        "The manual release workflow is included but remains an optional operation requiring deliberate "
        "identity, registry, and permission review. Cluster/serverless deployment is not provisioned.\n\n"
        "Before publishing, review CODEOWNERS, security reporting/contact routes, upstream README links, "
        "workflow repository/ref trust assumptions, optional publishing permissions, and project scope. "
        "Configure required checks in your own repository after observing a successful run.\n\n"
        "`template-manifest.json` records copied-file hashes and the source base commit/dirty state. "
        "It is a local copy inventory, not a signed provenance attestation. Local caches, .env files, "
        "private-key files, generated reports, and Git history were excluded.\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="microservice")
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(bootstrap(SOURCE_ROOT, args.destination, args.profile, args.dry_run), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"Template setup failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
