#!/usr/bin/env python3
"""Verify the fictional dashboard with isolated Linux/amd64 Docker services.

No service ports are published. Grafana, the exporter, Prometheus and renderer
remain inside one task-owned network namespace. No
host socket, credentials, sensor, existing Grafana or production data is mounted.
"""

import base64
import hashlib
import json
import math
import os
import platform
import re
import secrets
import shutil
import signal
import struct
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports/dashboard"
# Official release tags and Docker Registry index digests checked 2026-09-15.
# These are test infrastructure pins, not a claim that their images are CVE-free.
IMAGES = {
    "exporter": "python:3.12.14-alpine3.24@sha256:b64631e04e4920160c50fbe8d8df828f7f35f06f425cb44aa09bca53e708a35a",
    "prometheus": "prom/prometheus:v3.14.0@sha256:5ce7540c3c00ef4ab0c9d2c995c6a5b9c421f44b4a115d97a2c7af3b1c21cbb0",
    "grafana": "grafana/grafana:13.2.1@sha256:f772d434e8fab0049deb2b1b30abd43342bcfca1537614aa8d36080232cf4283",
    "renderer": "grafana/grafana-image-renderer:v5.12.3@sha256:cf36a94431662540a72d2058a43e0cbf72638334475d8216a25a77526a627be7",
}
EXPECTED = {1: 64800.0, 2: 1200.0, 3: 2.0}
DATASOURCE_UID = "devsecops-demo-prometheus"
MAX_RESPONSE = 20 * 1024 * 1024
DOCKER_ENV = os.environ.copy()
for variable in ("DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
    DOCKER_ENV.pop(variable, None)


def docker(*args, timeout=180):
    result = subprocess.run(["docker", *args], capture_output=True, text=True,
                            env=DOCKER_ENV, timeout=timeout, check=False)
    if result.returncode:
        # Avoid printing command arguments containing ephemeral service tokens.
        raise RuntimeError(f"docker {args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Unexpected redirect from the task-local Grafana")


def fetch(base, path, authorization, data=None, timeout=15):
    if not re.fullmatch(r"http://127\.0\.0\.1:[0-9]+", base) or not path.startswith("/"):
        raise ValueError("Only the task-local loopback Grafana may be queried")
    headers = {"Authorization": authorization}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    request = urllib.request.Request(base + path, headers=headers, data=data)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        payload = response.read(MAX_RESPONSE + 1)
        if len(payload) > MAX_RESPONSE:
            raise RuntimeError("Dashboard response exceeded the evidence size limit")
        return payload


def fetch_json(base, path, authorization, data=None):
    return json.loads(fetch(base, path, authorization, data))


class GrafanaClient:
    """Use the existing namespace without weakening the internal-only network.

    Docker does not establish a host port mapping for an internal-only bridge.
    Execute the same bounded, proxy-free HTTP helper beside the exporter instead.
    The ephemeral authorization value travels through stdin, not command arguments.
    """
    def __init__(self, exporter, authorization):
        if not re.fullmatch(r"[a-f0-9]{64}", exporter):
            raise ValueError("Expected the exact task-owned exporter container ID")
        self.exporter, self.authorization = exporter, authorization

    def fetch(self, path, data=None, timeout=15):
        code = ("import json,runpy,sys; "
                "helper=runpy.run_path('/fixture/scripts/validate_dashboard.py'); "
                "request=json.load(sys.stdin); "
                "sys.stdout.buffer.write(helper['fetch']('http://127.0.0.1:3000',"
                "request['path'],request['authorization'],request['data'],request['timeout']))")
        request = {"path": path, "authorization": self.authorization, "data": data,
                   "timeout": timeout}
        result = subprocess.run(
            ["docker", "exec", "--interactive", self.exporter, "python", "-c", code],
            input=json.dumps(request).encode(), capture_output=True, env=DOCKER_ENV,
            timeout=timeout + 15, check=False)
        if result.returncode:
            raise RuntimeError("Task-local Grafana request failed: " +
                               result.stderr.decode("utf-8", errors="replace").strip())
        if len(result.stdout) > MAX_RESPONSE:
            raise RuntimeError("Dashboard response exceeded the evidence size limit")
        return result.stdout

    def json(self, path, data=None):
        return json.loads(self.fetch(path, data))


def wait_for(check, description, timeout=120):
    deadline = time.monotonic() + timeout
    while True:
        try:
            result = check()
            if result:
                return result
        except (OSError, ValueError, RuntimeError):
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError(f"Timed out waiting for {description}")
        time.sleep(1)


def prometheus_value(response, expected):
    if response.get("status") != "success":
        raise ValueError("Prometheus query did not succeed")
    data = response.get("data", {})
    rows = data.get("result", [])
    if data.get("resultType") != "vector" or len(rows) != 1:
        raise ValueError("Expected exactly one instant-vector sample")
    value = float(rows[0]["value"][1])
    if not math.isfinite(value) or not math.isclose(value, expected):
        raise ValueError(f"Expected {expected}, received {value}")
    return value


def grafana_values(response):
    values = {}
    for panel_id, expected in EXPECTED.items():
        result = response.get("results", {}).get(str(panel_id), {})
        if result.get("error") or result.get("status", 200) != 200:
            raise ValueError(f"Grafana query failed for panel {panel_id}")
        samples = []
        for frame in result.get("frames", []):
            for index, field in enumerate(frame.get("schema", {}).get("fields", [])):
                if field.get("type") == "number":
                    samples.extend(frame["data"]["values"][index])
        if len(samples) != 1 or isinstance(samples[0], bool):
            raise ValueError(f"Expected one numeric Grafana sample for panel {panel_id}")
        value = float(samples[0])
        if not math.isfinite(value) or not math.isclose(value, expected):
            raise ValueError(f"Unexpected Grafana value for panel {panel_id}: {value}")
        values[str(panel_id)] = value
    return values


def png_dimensions(payload):
    """Check PNG structure/checksums; a person must still inspect panel contents."""
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Renderer did not return a PNG")
    offset, dimensions, has_pixels = 8, None, False
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(payload):
            raise ValueError("Truncated PNG chunk")
        kind = payload[offset + 4:offset + 8]
        data = payload[offset + 8:end - 4]
        checksum = struct.unpack(">I", payload[end - 4:end])[0]
        if zlib.crc32(kind + data) & 0xffffffff != checksum:
            raise ValueError("PNG checksum mismatch")
        if offset == 8:
            if kind != b"IHDR" or length != 13:
                raise ValueError("PNG is missing its image header")
            dimensions = struct.unpack(">II", data[:8])
            if not all(150 <= value <= 3000 for value in dimensions):
                raise ValueError("Unexpected rendered image dimensions")
        has_pixels |= kind == b"IDAT" and length > 0
        if kind == b"IEND":
            if length or end != len(payload) or not has_pixels:
                raise ValueError("Incomplete PNG image")
            return dimensions
        offset = end
    raise ValueError("PNG has no end marker")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def prepare_fixture(directory):
    # Copy only the synthetic inputs and their reader, never the full checkout.
    for relative in ("scripts/metrics.py", "scripts/validate_dashboard.py",
                     "metrics-templates/incident-metrics.json",
                     "metrics-templates/incident-metrics.csv", "dashboards/prometheus.yml",
                     "dashboards/grafana-devsecops.json"):
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    datasource_dir = directory / "provisioning/datasources"
    dashboard_dir = directory / "provisioning/dashboards"
    datasource_dir.mkdir(parents=True)
    dashboard_dir.mkdir(parents=True)
    (datasource_dir / "demo.yaml").write_text(
        "apiVersion: 1\ndatasources:\n  - name: Demo Prometheus\n"
        f"    uid: {DATASOURCE_UID}\n    type: prometheus\n    access: proxy\n"
        "    url: http://127.0.0.1:9090\n    isDefault: true\n    editable: false\n",
        encoding="utf-8")
    (dashboard_dir / "demo.yaml").write_text(
        "apiVersion: 1\nproviders:\n  - name: devsecops-demo\n    type: file\n"
        "    allowUiUpdates: false\n    updateIntervalSeconds: 30\n"
        "    options:\n      path: /fixture/dashboards\n", encoding="utf-8")
    # TemporaryDirectory is 0700; the read-only bind must be traversable by the
    # non-root container users. It contains no credentials or private dataset.
    for path in (directory, *directory.rglob("*")):
        path.chmod(0o755 if path.is_dir() else 0o644)
    return json.loads((directory / "dashboards/grafana-devsecops.json").read_text())


class Services:
    def __init__(self, directory, reports):
        self.directory, self.reports = directory, reports
        self.name = "devsecops-dashboard-" + uuid.uuid4().hex[:12]
        self.network = None
        self.containers = []
        self.redactions = []

    def create(self, role, options=(), command=()):
        container = docker("create", "--name", self.name + "-" + role,
                           "--label", "devsecops.validation=" + self.name,
                           "--platform", "linux/amd64", "--read-only",
                           "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                           "--pids-limit", "512", "--tmpfs", "/tmp:rw,nosuid,nodev,size=1g",
                           *options, IMAGES[role], *command)
        if not re.fullmatch(r"[a-f0-9]{64}", container):
            raise RuntimeError("Docker did not return an exact container ID")
        self.containers.append((role, container))  # Track before attempting start.
        docker("start", container)
        return container

    def mount(self, source, destination):
        return ["--mount", f"type=bind,src={self.directory / source},dst={destination},readonly"]

    def internal_json(self, exporter, path):
        # Fixed Prometheus destination in the shared namespace, not a user URL.
        if not path.startswith("/api/v1/"):
            raise ValueError("Only Prometheus API paths are supported")
        code = ("import urllib.request,sys; "
                "o=urllib.request.build_opener(urllib.request.ProxyHandler({})); "
                "r=o.open('http://127.0.0.1:9090'+sys.argv[1],timeout=5); "
                "print(r.read(1048576).decode())")
        return json.loads(docker("exec", exporter, "python", "-c", code, path))

    def cleanup(self):
        errors = []
        for role, container in reversed(self.containers):
            try:
                # Docker logs writes some process output to stderr.
                result = subprocess.run(["docker", "logs", "--tail", "200", container],
                                        text=True, capture_output=True, env=DOCKER_ENV,
                                        timeout=20, check=False)
                logs = result.stdout + result.stderr
                for secret in self.redactions:
                    logs = logs.replace(secret, "[ephemeral-token-redacted]")
                (self.reports / (role + ".log")).write_text(logs, encoding="utf-8")
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                errors.append(f"{role} logs: {error}")
            try:
                docker("rm", "--force", container)
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                errors.append(f"{role} cleanup: {error}")
        if self.network:
            try:
                docker("network", "rm", self.network)
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                errors.append(f"network cleanup: {error}")
        return errors


def validate(directory, reports, services):
    dashboard = prepare_fixture(directory)
    if set(panel["id"] for panel in dashboard["panels"]) != set(EXPECTED):
        raise ValueError("Update acceptance values when changing dashboard panels")
    images = {}
    for role, image in IMAGES.items():
        print(f"Pulling pinned {role} image", flush=True)
        docker("pull", "--platform", "linux/amd64", image, timeout=600)
        images[role] = json.loads(docker("image", "inspect", "--format",
                                        '{{json .RepoDigests}}', image))
    write_json(reports / "images.json", {"configured": IMAGES, "resolved": images})
    services.network = docker("network", "create", "--internal", "--label",
                              "devsecops.validation=" + services.name, services.name)
    exporter = services.create("exporter", ["--network", services.network,
        "--user", "10001:10001",
        "--env", "PYTHONDONTWRITEBYTECODE=1", *services.mount(".", "/fixture")],
        ["python", "/fixture/scripts/metrics.py", "--serve"])
    shared = ["--network", "container:" + exporter]
    services.create("prometheus", [*shared,
        "--tmpfs", "/prometheus:rw,nosuid,nodev,size=128m,uid=65534,gid=65534",
        *services.mount("dashboards/prometheus.yml", "/etc/prometheus/prometheus.yml")],
        ["--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.path=/prometheus",
         "--storage.tsdb.retention.time=1h", "--web.listen-address=127.0.0.1:9090"])
    renderer_token = secrets.token_urlsafe(32)
    password = secrets.token_urlsafe(32)
    services.redactions.extend([renderer_token, password])
    renderer = services.create("renderer", [*shared, "--memory", "8g", "--cpus", "2",
        "--shm-size", "256m", "--tmpfs", "/home/nonroot:rw,nosuid,nodev,size=128m,uid=65532",
        "--env", "AUTH_TOKEN=" + renderer_token, "--env", "GOMEMLIMIT=512MiB"],
        ["server", "--server.addr=127.0.0.1:8081", "--rate-limit.max-limit=1",
         "--rate-limit.min-limit=1"])
    grafana_env = {
        "GF_SERVER_HTTP_ADDR": "127.0.0.1",
        "GF_SECURITY_ADMIN_PASSWORD": password,
        "GF_AUTH_ANONYMOUS_ENABLED": "false",
        "GF_ANALYTICS_REPORTING_ENABLED": "false",
        "GF_ANALYTICS_CHECK_FOR_UPDATES": "false",
        "GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES": "false",
        "GF_PLUGINS_PREINSTALL_DISABLED": "true",
        "GF_LOG_MODE": "console",
        "GF_RENDERING_SERVER_URL": "http://127.0.0.1:8081/render",
        "GF_RENDERING_CALLBACK_URL": "http://127.0.0.1:3000/",
        "GF_RENDERING_RENDERER_TOKEN": renderer_token,
    }
    environment = [argument for key, value in grafana_env.items()
                   for argument in ("--env", key + "=" + value)]
    services.create("grafana", [*shared, *environment,
        "--tmpfs", "/var/lib/grafana:rw,nosuid,nodev,size=256m,uid=472,gid=0",
        "--tmpfs", "/var/log/grafana:rw,nosuid,nodev,size=32m,uid=472,gid=0",
        *services.mount("provisioning", "/etc/grafana/provisioning"),
        *services.mount("dashboards", "/fixture/dashboards")])
    authorization = "Basic " + base64.b64encode(("admin:" + password).encode()).decode()
    services.redactions.append(authorization)
    client = GrafanaClient(exporter, authorization)
    health = wait_for(lambda: client.json("/api/health"), "Grafana health")
    if health.get("database") != "ok":
        raise ValueError("Grafana database did not become healthy")
    write_json(reports / "grafana-health.json", health)
    wait_for(lambda: docker("inspect", "--format", '{{.State.Health.Status}}', renderer)
             == "healthy", "renderer health")
    up_path = "/api/v1/query?" + urllib.parse.urlencode({"query": 'up{job="devsecops-demo"}'})
    def scrape_ready():
        response = services.internal_json(exporter, up_path)
        prometheus_value(response, 1)
        return response
    up = wait_for(scrape_ready, "successful fixture scrape")
    write_json(reports / "prometheus-up.json", up)
    write_json(reports / "prometheus-version.json", services.internal_json(exporter, "/api/v1/status/buildinfo"))
    provisioned = client.json("/api/dashboards/uid/devsecops-demo")
    if len(provisioned.get("dashboard", {}).get("panels", [])) != 3:
        raise ValueError("Grafana did not provision all three panels")
    expected_queries = {panel["id"]: panel["targets"][0]["expr"] for panel in dashboard["panels"]}
    actual_queries = {panel["id"]: panel["targets"][0]["expr"]
                      for panel in provisioned["dashboard"]["panels"]}
    if actual_queries != expected_queries:
        raise ValueError("Provisioned dashboard queries differ from the committed model")
    write_json(reports / "grafana-dashboard.json", provisioned)
    datasource = client.json(f"/api/datasources/uid/{DATASOURCE_UID}/health")
    if datasource.get("status") != "OK":
        raise ValueError("Grafana datasource health check failed")
    write_json(reports / "grafana-datasource-health.json", datasource)
    queries, direct = [], {}
    for panel in dashboard["panels"]:
        expression = panel["targets"][0]["expr"]
        path = "/api/v1/query?" + urllib.parse.urlencode({"query": expression})
        response = services.internal_json(exporter, path)
        prometheus_value(response, EXPECTED[panel["id"]])
        direct[str(panel["id"])] = {"expression": expression, "response": response}
        queries.append({"refId": str(panel["id"]), "expr": expression,
                        "datasource": {"type": "prometheus", "uid": DATASOURCE_UID},
                        "instant": True, "range": False, "format": "time_series",
                        "intervalMs": 15000, "maxDataPoints": 100})
    write_json(reports / "prometheus-queries.json", direct)
    now = int(time.time() * 1000)
    queried = client.json("/api/ds/query",
                          {"from": str(now - 300000), "to": str(now), "queries": queries})
    write_json(reports / "grafana-queries.json", queried)
    values = grafana_values(queried)
    renders = []
    for panel_id in EXPECTED:
        params = urllib.parse.urlencode({"orgId": 1, "panelId": panel_id,
            "width": 1000, "height": 500, "tz": "UTC", "timeout": 90,
            "from": "now-5m", "to": "now", "var-DS_PROMETHEUS": DATASOURCE_UID})
        path = "/render/d-solo/devsecops-demo/demo?" + params
        payload = client.fetch(path, timeout=120)
        dimensions = png_dimensions(payload)
        filename = f"panel-{panel_id}.png"
        (reports / filename).write_bytes(payload)
        renders.append({"file": filename, "dimensions": dimensions,
                        "sha256": hashlib.sha256(payload).hexdigest()})
    source_hashes = {relative: hashlib.sha256((directory / relative).read_bytes()).hexdigest()
                     for relative in ("dashboards/grafana-devsecops.json",
                                      "metrics-templates/incident-metrics.json",
                                      "metrics-templates/incident-metrics.csv", "scripts/metrics.py",
                                      "scripts/validate_dashboard.py")}
    return {"values": values, "renders": renders, "source_sha256": source_hashes,
            "visual_review": "PNG structure validated; inspect panel images before claiming visual acceptance"}


def main():
    def interrupted(_signum, _frame):
        raise RuntimeError("Dashboard validation interrupted")
    # SIGKILL cannot be trapped; use a disposable CI runner for that final limit.
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    # A fresh evidence directory prevents a failed rerun from presenting old PNGs
    # as current results. Never remove or overwrite a previous run's evidence.
    reports = REPORTS / uuid.uuid4().hex[:12]
    reports.mkdir(parents=True, exist_ok=False)
    summary = {"started_at": datetime.now(timezone.utc).isoformat(),
               "status": "failed", "scope": "fictional fixture, isolated Linux/amd64 containers",
               "evidence_directory": str(reports.relative_to(ROOT))}
    result = 1
    with tempfile.TemporaryDirectory(prefix="devsecops-dashboard-") as temporary:
        services = Services(Path(temporary), reports)
        try:
            if (platform.system(), platform.machine()) != ("Linux", "x86_64"):
                raise RuntimeError("This acceptance harness requires a Linux AMD64 host")
            context = docker("context", "show")
            endpoint = docker("context", "inspect", context, "--format", "{{.Endpoints.docker.Host}}")
            if not endpoint.startswith("unix://"):
                raise RuntimeError("Only a local Unix-socket Docker endpoint is accepted")
            # Freeze the checked context for every subsequent command/cleanup.
            DOCKER_ENV["DOCKER_CONTEXT"] = context
            summary["docker_context"] = context
            if docker("info", "--format", "{{.OSType}}") != "linux":
                raise RuntimeError("A Linux-container Docker daemon is required")
            summary.update(validate(Path(temporary), reports, services))
            summary["status"] = "passed"
            result = 0
        except (OSError, ValueError, TypeError, KeyError, IndexError, RuntimeError,
                subprocess.SubprocessError) as error:
            message = str(error)
            for secret in services.redactions:
                message = message.replace(secret, "[ephemeral-token-redacted]")
            summary["error"] = message
        finally:
            summary["cleanup_errors"] = services.cleanup()
            if summary["cleanup_errors"]:
                summary["status"], result = "failed", 1
            summary["finished_at"] = datetime.now(timezone.utc).isoformat()
            write_json(reports / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
