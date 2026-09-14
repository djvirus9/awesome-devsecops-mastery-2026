#!/usr/bin/env python3
"""Offline repository checks: syntax, local Markdown paths, and selected structures.

This is not a Kubernetes API validator, shell interpreter, GitHub workflow runner,
or complete CommonMark parser. It does not check anchors or external URLs.
"""

import argparse
from collections import Counter
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import yaml


IGNORED_PARTS = {".git", ".venv", ".tools", "reports", "archive", "__pycache__"}
FULL_ACTION_PIN = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")
DOCKER_ACTION_PIN = re.compile(r"^docker://[^\s@]+@sha256:[0-9a-fA-F]{64}$")
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*"
    r"(?P<target><[^>\n]+>|(?:\\.|[^()\s]|\([^()\n]*\))+)"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\)))?\s*\)"
)
REFERENCE_DEFINITION = re.compile(
    r"^ {0,3}\[(?P<label>[^\]\n]+)\]:\s*(?P<target><[^>\n]+>|\S+)", re.MULTILINE
)
REFERENCE_USE = re.compile(r"!?\[(?P<label>[^\]\n]+)\]\[(?P<ref>[^\]\n]*)\]")


class UniqueBaseLoader(yaml.BaseLoader):
    """Keep YAML scalar keys as strings (including GitHub's `on`) and reject duplicates."""

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in mapping:
                    raise yaml.constructor.ConstructorError(
                        "while constructing a mapping", node.start_mark,
                        f"duplicate key {key!r}", key_node.start_mark,
                    )
                mapping[key] = self.construct_object(value_node, deep=deep)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "mapping key must be a scalar", key_node.start_mark,
                ) from error
        return mapping


def unique_json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_json_constant(value):
    raise ValueError(f"non-standard JSON constant {value}")


def blank_preserving_lines(value):
    return "".join("\n" if char == "\n" else " " for char in value)


def markdown_prose(text):
    """Remove fenced/inline code and comments while preserving diagnostic line numbers."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if opening and opening[1][0] == fence[0] and len(opening[1]) >= fence[1] and not opening[2].strip():
                fence = None
            lines.append(blank_preserving_lines(line))
        elif opening:
            fence = (opening[1][0], len(opening[1]))
            lines.append(blank_preserving_lines(line))
        else:
            lines.append(line)
    prose = "".join(lines)
    prose = re.sub(r"<!--[\s\S]*?-->", lambda match: blank_preserving_lines(match[0]), prose)
    return re.sub(r"(`+)([^`\n]|(?!\1)`)*?\1", lambda match: blank_preserving_lines(match[0]), prose)


class Report:
    def __init__(self):
        self.counts = Counter()
        self.errors = []

    def error(self, path, message, line=None):
        location = str(path) + (f":{line}" if line else "")
        self.errors.append(f"{location}: {message}")


def check_local_target(root, source, target, report, line):
    target = html.unescape(target.removeprefix("<").removesuffix(">"))
    target = re.sub(r"\\([\\`*{}\[\]()#+\-.!_ >])", r"\1", target)
    if not target or target.startswith(("#", "//")) or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return
    try:
        path = unquote(urlsplit(target).path)
        if not path:
            return
        candidate = (root / path.lstrip("/") if path.startswith("/") else root / source.parent / path).resolve()
        report.counts["local_links"] += 1
        if not candidate.is_relative_to(root.resolve()):
            report.error(source, f"local link leaves this repository: {target}", line)
        elif not candidate.exists():
            report.error(source, f"missing local link target: {target}", line)
    except (ValueError, OSError, RuntimeError) as error:
        report.error(source, f"invalid local link {target!r}: {error}", line)


def check_markdown(root, source, text, report):
    prose = markdown_prose(text)
    definitions = set()
    for match in REFERENCE_DEFINITION.finditer(prose):
        definitions.add(" ".join(match["label"].split()).casefold())
        check_local_target(root, source, match["target"], report, prose.count("\n", 0, match.start()) + 1)
    for match in INLINE_LINK.finditer(prose):
        check_local_target(root, source, match["target"], report, prose.count("\n", 0, match.start()) + 1)
    for match in REFERENCE_USE.finditer(prose):
        label = " ".join((match["ref"] or match["label"]).split()).casefold()
        if label not in definitions:
            report.error(source, f"undefined Markdown link reference: {label}", prose.count("\n", 0, match.start()) + 1)


def check_action(source, location, value, report):
    if not isinstance(value, str):
        report.error(source, f"{location}: uses must be a string")
    elif value.startswith("./"):
        return  # Local actions and reusable workflows are maintained in the same revision.
    elif value.startswith("docker://"):
        if not DOCKER_ACTION_PIN.fullmatch(value):
            report.error(source, f"{location}: Docker action needs an immutable sha256 digest: {value}")
    elif not FULL_ACTION_PIN.fullmatch(value):
        report.error(source, f"{location}: external action/workflow needs a full 40-character commit SHA: {value}")


def check_permissions(source, location, value, report):
    if value == "read-all":
        return
    if not isinstance(value, dict) or not all(isinstance(level, str) and level in {"read", "write", "none"} for level in value.values()):
        report.error(source, f"{location}: use explicit permission scopes or read-all; write-all is not allowed")


def check_workflow(source, workflow, report):
    report.counts["workflows"] += 1
    if not isinstance(workflow, dict):
        report.error(source, "GitHub workflow must be a mapping")
        return
    if "on" not in workflow:
        report.error(source, "GitHub workflow must declare on events")
    if "permissions" not in workflow:
        report.error(source, "GitHub workflow must declare default permissions explicitly")
    else:
        check_permissions(source, "permissions", workflow["permissions"], report)
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        report.error(source, "GitHub workflow must have a non-empty jobs mapping")
        return
    for job_name, job in jobs.items():
        location = f"jobs.{job_name}"
        if not isinstance(job, dict):
            report.error(source, f"{location}: job must be a mapping")
            continue
        if "permissions" in job:
            check_permissions(source, f"{location}.permissions", job["permissions"], report)
        if "uses" in job:
            check_action(source, location, job["uses"], report)
            continue
        steps = job.get("steps")
        if not isinstance(steps, list) or not steps:
            report.error(source, f"{location}: executable job must have non-empty steps")
            continue
        if "runs-on" not in job:
            report.error(source, f"{location}: executable job needs runs-on")
        for index, step in enumerate(steps, 1):
            step_location = f"{location}.steps[{index}]"
            if not isinstance(step, dict):
                report.error(source, f"{step_location}: step must be a mapping")
                continue
            if ("run" in step) == ("uses" in step):
                report.error(source, f"{step_location}: step needs exactly one of run or uses")
            if "uses" in step:
                check_action(source, step_location, step["uses"], report)
            name = str(step.get("name", ""))
            body = str(step.get("run", ""))
            if re.search(r"\bplaceholder\b", name + "\n" + body, re.IGNORECASE):
                report.error(source, f"{step_location}: placeholder steps cannot serve as working checks")
            commands = [line.strip() for line in body.splitlines() if line.strip() and not line.lstrip().startswith("#")]
            print_only = commands and all(re.match(r"^(echo|printf)\s+", command) or command in {"true", ":"} for command in commands)
            has_shell_control = any(token in body for token in ("&&", "||", ";", "|"))
            if print_only and not has_shell_control and re.search(r"\b(check|checks|scan|sast|sca|sbom|policy|test|validate|verify|security|gate)\b", name, re.IGNORECASE):
                report.error(source, f"{step_location}: named check only prints a message or returns success")


def check_config(source, data, report):
    if source.parent != Path("configs"):
        return
    if not isinstance(data, dict):
        report.error(source, "tool configuration must be a mapping")
        return
    report.counts["configs"] += 1
    if source.name == "trivy.yaml":
        try:
            blocking_exit = int(data.get("exit-code", "0"))
        except (ValueError, TypeError):
            blocking_exit = 0
        if not 1 <= blocking_exit <= 255:
            report.error(source, "Trivy requires a nonzero exit-code so findings fail the gate")
        severity = data.get("severity")
        if not isinstance(severity, list) or not severity or not all(isinstance(item, str) and item in {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"} for item in severity):
            report.error(source, "Trivy severity must be a non-empty YAML list of valid severities")
        scan = data.get("scan", {})
        if not isinstance(scan, dict) or "security-checks" in scan:
            report.error(source, "Trivy scan must be a mapping using scanners, not legacy security-checks")
        elif "scanners" in scan and (not isinstance(scan["scanners"], list) or not scan["scanners"]):
            report.error(source, "Trivy scan.scanners must be a non-empty list")
    elif source.name == "syft.yaml":
        output = data.get("output")
        if output is not None and (not isinstance(output, list) or not output or not all(isinstance(item, str) and item for item in output)):
            report.error(source, "Syft output must be a list of format strings, not format mappings")
    elif source.name == "semgrep.yml":
        rules = data.get("rules")
        if not isinstance(rules, list) or not rules:
            report.error(source, "Semgrep needs a non-empty rules list")
            return
        ids = set()
        for index, rule in enumerate(rules, 1):
            if not isinstance(rule, dict):
                report.error(source, f"Semgrep rule {index} must be a mapping")
                continue
            rule_id = rule.get("id")
            if not isinstance(rule_id, str) or not rule_id or rule_id in ids:
                report.error(source, f"Semgrep rule {index} needs a unique, non-empty id")
            if isinstance(rule_id, str):
                ids.add(rule_id)
            if not rule.get("message") or not isinstance(rule.get("languages"), list) or not rule.get("languages") or not isinstance(rule.get("severity"), str) or rule["severity"] not in {"ERROR", "WARNING", "INFO"}:
                report.error(source, f"Semgrep rule {index} needs message, languages, and ERROR/WARNING/INFO severity")
            if rule.get("mode") != "taint" and not any(key in rule for key in ("pattern", "patterns", "pattern-either", "pattern-regex")):
                report.error(source, f"Semgrep rule {index} needs a matching pattern")
    elif source.name == "cosign-policy.yaml":
        if data.get("kind") != "ClusterImagePolicy" or not isinstance(data.get("spec"), dict):
            report.error(source, "Sigstore config needs a ClusterImagePolicy spec")
            return
        spec = data["spec"]
        images = spec.get("images")
        if not isinstance(images, list) or not images or not all(isinstance(image, dict) and isinstance(image.get("glob"), str) and image["glob"] for image in images):
            report.error(source, "Sigstore policy needs non-empty image glob selectors")
        authorities = spec.get("authorities")
        if not isinstance(authorities, list) or not authorities:
            report.error(source, "Sigstore policy needs authorities")
            return
        for authority in authorities:
            if not isinstance(authority, dict):
                report.error(source, "Sigstore authority must be a mapping")
                continue
            if "keyless" not in authority:
                continue
            keyless = authority["keyless"]
            identities = keyless.get("identities") if isinstance(keyless, dict) else None
            if not isinstance(identities, list) or not identities or not all(isinstance(identity, dict) and (identity.get("issuer") or identity.get("issuerRegExp")) and (identity.get("subject") or identity.get("subjectRegExp")) for identity in identities):
                report.error(source, "Sigstore keyless identities need both issuer and signer subject constraints")


def tracked_and_pending_paths(root):
    """Use Git when present; a copied starter without .git uses a pruned tree walk.

    A plain directory has no Git index or ignore engine. The explicit generated
    directory exclusions apply there; no dependency tree or external symlink is
    followed. This also works when the copy lives inside another repository.
    """
    if not (root / ".git").exists():
        paths = []
        for directory, folders, files in os.walk(root, followlinks=False):
            folders[:] = sorted(name for name in folders if name not in IGNORED_PARTS and not (Path(directory) / name).is_symlink())
            paths.extend((Path(directory) / name).relative_to(root) for name in files)
        return sorted(paths)
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, check=True, stdout=subprocess.PIPE,
    )
    return sorted({Path(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item})


def validate(root, paths=None):
    root = Path(root).resolve()
    report = Report()
    for source in tracked_and_pending_paths(root) if paths is None else paths:
        source = Path(source)
        if IGNORED_PARTS.intersection(source.parts) or not (root / source).is_file():
            continue
        if not (root / source).resolve().is_relative_to(root):
            report.error(source, "file resolves outside the repository")
            continue
        report.counts["files"] += 1
        suffix = source.suffix.lower()
        if suffix not in {".md", ".json", ".yaml", ".yml"}:
            continue
        try:
            text = (root / source).read_text(encoding="utf-8")
            if suffix == ".md":
                report.counts["markdown"] += 1
                check_markdown(root, source, text, report)
            elif suffix == ".json":
                report.counts["json"] += 1
                json.loads(text, object_pairs_hook=unique_json_object, parse_constant=reject_json_constant)
            else:
                report.counts["yaml"] += 1
                documents = list(yaml.load_all(text, Loader=UniqueBaseLoader))
                for data in documents:
                    if source.parent == Path(".github/workflows") or isinstance(data, dict) and "on" in data and "jobs" in data:
                        check_workflow(source, data, report)
                    check_config(source, data, report)
        except (UnicodeError, OSError, ValueError, yaml.YAMLError) as error:
            report.error(source, f"invalid {suffix.lstrip('.')} content: {error}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        report = validate(args.root)
    except (subprocess.CalledProcessError, OSError) as error:
        print(f"Cannot list repository files: {error}", file=sys.stderr)
        return 2
    print("Validated " + ", ".join(f"{count} {name}" for name, count in sorted(report.counts.items())))
    print("Scope: local Markdown paths (no anchors/external URLs), JSON/YAML syntax, and selected workflow/config structures.")
    for error in report.errors:
        print(f"ERROR {error}", file=sys.stderr)
    print(f"Repository validation: {len(report.errors)} error(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
