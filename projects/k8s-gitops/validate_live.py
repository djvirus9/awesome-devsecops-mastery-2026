#!/usr/bin/env python3
"""Destructive only to a fresh, named Kind cluster created by this process.

Linux amd64 integration harness. Never use it against an existing cluster.
All noncompliant policy fixtures are sent with --dry-run=server.
"""
import base64
import copy
import datetime as dt
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

import yaml

ROOT = Path(__file__).resolve().parents[2]
CLUSTER = "devsecops-reference"
CONTEXT = "kind-devsecops-reference"
IMAGE_RE = re.compile(r"ghcr\.io/djvirus9/awesome-devsecops-mastery-2026/sample-api@sha256:[0-9a-f]{64}")
IDENTITY = "https://github.com/djvirus9/awesome-devsecops-mastery-2026/.github/workflows/release.yml@refs/heads/main"
POLICIES = ("require-non-root", "disallow-privileged", "require-resource-limits", "restrict-workload")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Unexpected redirect from the task-local API")


def validate_image_reference(value):
    if value and not IMAGE_RE.fullmatch(value):
        raise ValueError("IMAGE_REFERENCE must be an immutable digest in the reference image repository")
    return value


def admission_matches(result, allowed, policy=None):
    """A generic API/webhook failure must not pass a negative policy test."""
    if allowed:
        return result.returncode == 0 and (policy is None or policy in result.stdout)
    return (result.returncode != 0 and policy in result.stdout
            and bool(re.search(r"denied|blocked|failed to validate|validation failure", result.stdout, re.I))
            and not re.search(r"failed calling webhook|no endpoints available|context deadline exceeded", result.stdout, re.I))


def kyverno_policies_ready(document, expected=POLICIES):
    """Kyverno ValidatingPolicy readiness is nested, not a Ready condition."""
    items = document.get("items", [document] if document.get("kind") == "ValidatingPolicy" else [])
    policies = {obj.get("metadata", {}).get("name"): obj for obj in items}
    return (set(policies) == set(expected)
            and all(obj.get("status", {}).get("conditionStatus", {}).get("ready") is True
                    for obj in policies.values()))


def exception_preserves_rendered_spec(rendered, persisted):
    """Accept API-added defaults without allowing supplied intent to change."""
    return all(persisted.get("spec", {}).get(key) == value for key, value in rendered["spec"].items())


def exception_snapshot_unchanged(before, after):
    """Compare canonical API state, not a manifest missing server defaults."""
    initial, retained = before.get("metadata", {}), after.get("metadata", {})
    return (bool(initial.get("uid")) and not retained.get("deletionTimestamp")
            and all(key in initial and initial[key] == retained.get(key)
                    for key in ("uid", "generation", "name", "namespace"))
            and before.get("spec") == after.get("spec"))


class Validation:
    def __init__(self):
        self.reference = validate_image_reference(os.getenv("IMAGE_REFERENCE", ""))
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.report = ROOT / "reports" / "k8s" / f"{stamp}-{os.getpid()}"
        self.report.mkdir(parents=True)
        self.temp = tempfile.TemporaryDirectory(prefix="devsecops-k8s-")
        self.scratch = Path(self.temp.name)
        self.env = os.environ.copy()
        for name in ("DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH", "KUBECONFIG", "HELM_KUBECONTEXT",
                     "REGISTRY_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
            self.env.pop(name, None)
        self.env.update({
            "PATH": str(ROOT / ".tools/bin") + os.pathsep + os.environ.get("PATH", ""),
            "KUBECONFIG": str(self.scratch / "kubeconfig"),
            "HELM_CONFIG_HOME": str(self.scratch / "helm/config"),
            "HELM_CACHE_HOME": str(self.scratch / "helm/cache"),
            "HELM_DATA_HOME": str(self.scratch / "helm/data"),
            "DOCKER_CONTEXT": os.environ.get("DOCKER_CONTEXT", "default"),
            "KIND_EXPERIMENTAL_PROVIDER": "docker",
        })
        self.created = False
        self.creation_attempted = False
        self.forward = None
        self.forward_log = None
        self.steps = []
        self.redact = [value for value in (os.getenv("REGISTRY_TOKEN"),) if value]

    def record(self, name, detail="passed"):
        self.steps.append({"check": name, "result": detail})
        print(f"{name}: {detail}", flush=True)

    def run(self, name, args, *, check=True, timeout=180, input=None):
        result = subprocess.run(args, cwd=ROOT, env=self.env, input=input, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        output = result.stdout
        for secret in self.redact:
            output = output.replace(secret, "[REDACTED]")
        with (self.report / "commands.log").open("a", encoding="utf-8") as log:
            log.write(f"\n## {name} (exit {result.returncode})\n{output}\n")
        if check and result.returncode:
            raise RuntimeError(f"{name} failed (exit {result.returncode}); see commands.log")
        return result

    def kube(self, name, *args, **kwargs):
        return self.run(name, ["kubectl", "--context", CONTEXT, "--request-timeout=90s", *args], **kwargs)

    def apply_object(self, name, obj):
        return self.kube(name, "apply", "-f", "-", input=json.dumps(obj))

    def admission(self, name, manifest, allowed=True, policy=None, retry=20):
        for attempt in range(retry):
            result = self.kube(name, "apply", "--dry-run=server", "-f", str(manifest), check=False)
            if admission_matches(result, allowed, policy):
                self.record(name)
                return
            if attempt + 1 < retry:
                time.sleep(1)
        raise RuntimeError(f"{name}: intended admission outcome was not observed")

    def fixture(self, name):
        return ROOT / "policies/fixtures" / f"{name}.yaml"

    def wait_policies_ready(self, expected=POLICIES):
        deadline = time.monotonic() + 120
        while True:
            result = self.kube("Policy readiness", "get", "validatingpolicies", *expected, "-o", "json")
            if kyverno_policies_ready(json.loads(result.stdout), expected):
                return
            if time.monotonic() >= deadline:
                raise RuntimeError("Kyverno policy readiness timed out; inspect conditionStatus in commands.log")
            time.sleep(2)

    def preflight(self):
        if (platform.system(), platform.machine()) != ("Linux", "x86_64"):
            raise RuntimeError("This CI harness requires Linux amd64; use the manual guide on macOS")
        pins = json.loads((ROOT / "tool-versions.json").read_text())["tools"]
        for name, args in (("kind", ["version"]), ("helm", ["version", "--short"]),
                           ("kubectl", ["version", "--client=true", "-o", "json"])):
            result = self.run(name + " version", [name, *args])
            if pins[name]["version"] not in result.stdout:
                raise RuntimeError(f"{name} does not match tool-versions.json")
        endpoint = self.run("Docker endpoint", ["docker", "context", "inspect", self.env["DOCKER_CONTEXT"],
                            "--format", "{{.Endpoints.docker.Host}}"])
        if not endpoint.stdout.strip().startswith("unix://"):
            raise RuntimeError("Only a local Unix-socket Docker endpoint is accepted")
        self.run("Docker readiness", ["docker", "info", "--format", "{{.ServerVersion}} {{.MemTotal}}"])
        clusters = self.run("Existing Kind names", ["kind", "get", "clusters"])
        if CLUSTER in clusters.stdout.splitlines():
            raise RuntimeError(f"Refusing existing Kind cluster {CLUSTER}; no cleanup will touch it")
        # Also reject orphaned containers before Kind attempts any creation.
        nodes = self.run("Existing Kind containers", ["docker", "ps", "-aq", "--filter",
                         f"label=io.x-k8s.kind.cluster={CLUSTER}"])
        if nodes.stdout.strip():
            raise RuntimeError("Refusing existing or orphaned containers with the reserved cluster label")
        self.record("isolated-preflight")

    def start(self):
        self.run("Build local API", ["docker", "build", "--pull", "-t", "devsecops-reference:local", "samples/sample-api"], timeout=600)
        self.run("Container smoke", [str(ROOT / ".venv/bin/python"), "scripts/container_smoke.py"], timeout=120)
        # Kind removes partial nodes on creation failure by default. Set ownership
        # only after successful creation; never delete a pre-existing cluster.
        self.creation_attempted = True
        self.run("Create isolated Kind", ["kind", "create", "cluster", "--config", "projects/k8s-gitops/kind.yaml",
                 "--kubeconfig", self.env["KUBECONFIG"]], timeout=300)
        self.created = True
        self.run("Add Cilium chart", ["helm", "repo", "add", "cilium", "https://helm.cilium.io/"])
        self.run("Install Cilium", ["helm", "upgrade", "--install", "cilium", "cilium/cilium", "--version", "1.20.1",
                 "--namespace", "kube-system", "--kube-context", CONTEXT, "--set", "ipam.mode=kubernetes",
                 "--set", "kubeProxyReplacement=false", "--set", "operator.replicas=1", "--wait", "--timeout", "5m"], timeout=360)
        self.kube("Ready node", "wait", "--for=condition=Ready", "nodes", "--all", "--timeout=120s")
        self.run("Load local API", ["kind", "load", "docker-image", "devsecops-reference:local", "--name", CLUSTER])
        self.kube("Reference namespace", "apply", "-f", "projects/k8s-gitops/base/namespace.yaml")
        self.kube("Exception namespace", "create", "namespace", "policy-exceptions")
        self.run("Add Kyverno chart", ["helm", "repo", "add", "kyverno", "https://kyverno.github.io/kyverno/"])
        self.run("Install Kyverno", ["helm", "upgrade", "--install", "kyverno", "kyverno/kyverno", "--version", "3.9.1",
                 "--namespace", "kyverno", "--create-namespace", "--kube-context", CONTEXT,
                 "--set", "features.policyExceptions.enabled=true", "--set", "features.policyExceptions.namespace=policy-exceptions",
                 "--wait", "--timeout", "5m"], timeout=360)
        self.kube("Ephemeral-container reporting permission", "apply", "-f", "projects/k8s-gitops/kyverno-report-rbac.yaml")
        for policy in POLICIES:
            self.kube("Apply " + policy, "apply", "-f", f"policies/kyverno/{policy}.yaml")
        self.wait_policies_ready()
        self.record("cluster-cni-and-admission-ready")

    def audit_deploy(self):
        self.admission("audit-compliant", self.fixture("good"))
        self.admission("audit-privileged-warning", self.fixture("privileged"), policy="disallow-privileged")
        # This is a public, synthetic credential for this disposable lesson only.
        self.apply_object("Synthetic API credential", {"apiVersion": "v1", "kind": "Secret",
            "metadata": {"name": "sample-api-tokens", "namespace": CLUSTER},
            "stringData": {"API_TOKENS_JSON": '{"demo-alice-token":"alice","demo-bob-token":"bob"}'}})
        self.kube("Deploy API", "apply", "-k", "projects/k8s-gitops/base")
        self.kube("API rollout", "-n", CLUSTER, "rollout", "status", "deployment/sample-api", "--timeout=120s")
        self.start_forward()
        self.http_checks("initial-api")
        code = """import errno, os
assert os.getuid() == 10001 and os.getgid() == 10001
assert not os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token')
status = open('/proc/self/status').read().splitlines()
assert int(next(x.split()[1] for x in status if x.startswith('CapEff:')), 16) == 0
assert next(x.split()[1] for x in status if x.startswith('NoNewPrivs:')) == '1'
try:
    open('/app/reference-write-check', 'w').close()
except OSError as error:
    assert error.errno == errno.EROFS, error
else:
    raise AssertionError('root filesystem is writable')
with open('/tmp/reference-write-check', 'w') as output:
    output.write('disposable check')
os.unlink('/tmp/reference-write-check')
print('PASS: uid, capabilities, no-new-privileges, read-only root, writable tmp, no API token')
"""
        self.kube("Runtime hardening", "-n", CLUSTER, "exec", "deployment/sample-api", "--", "python", "-c", code)
        result = self.kube("ServiceAccount has no secret access", "auth", "can-i", "get", "secrets", "-n", CLUSTER,
                           "--as", f"system:serviceaccount:{CLUSTER}:sample-api", check=False)
        if result.returncode != 1 or result.stdout.strip() != "no":
            raise RuntimeError("Unexpected ServiceAccount authorization result")
        self.record("runtime-hardening-and-rbac")

    def start_forward(self):
        self.stop_forward()
        path = self.report / "port-forward.log"
        self.forward_log = path.open("w", encoding="utf-8")
        self.forward = subprocess.Popen(["kubectl", "--context", CONTEXT, "-n", CLUSTER, "port-forward",
            "--address", "127.0.0.1", "service/sample-api", ":8080"], cwd=ROOT, env=self.env,
            stdout=self.forward_log, stderr=subprocess.STDOUT)
        for _ in range(60):
            match = re.search(r"Forwarding from 127\.0\.0\.1:(\d+)", path.read_text())
            if match:
                self.url = "http://127.0.0.1:" + match[1]
                return
            if self.forward.poll() is not None:
                break
            time.sleep(0.5)
        raise RuntimeError("Local port-forward did not become ready")

    def stop_forward(self):
        if self.forward is not None:
            if self.forward.poll() is None:
                self.forward.terminate()
                try:
                    self.forward.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.forward.kill()
                    self.forward.wait(timeout=5)
            self.forward = None
        if self.forward_log is not None:
            self.forward_log.close()
            self.forward_log = None

    def http_checks(self, name):
        opener = build_opener(ProxyHandler({}), NoRedirect())
        cases = [("/health", None, 200, "ok"), ("/v1/items", None, 401, None),
                 ("/v1/items", "demo-alice-token", 200, "item-1"),
                 ("/v1/items", "demo-bob-token", 200, "item-2"),
                 ("/v1/items/item-2", "demo-alice-token", 404, None)]
        for path, token, expected, item in cases:
            headers = {"Authorization": "Bearer " + token} if token else {}
            try:
                response = opener.open(Request(self.url + path, headers=headers), timeout=5)
            except HTTPError as error:
                response = error
            with response:
                payload = json.load(response)
                if response.status != expected:
                    raise RuntimeError(f"{name} {path}: expected HTTP{expected}, got {response.status}")
            if item == "ok" and payload != {"status": "ok"}:
                raise RuntimeError("Health payload differs")
            if item and item != "ok" and [entry["id"] for entry in payload["items"]] != [item]:
                raise RuntimeError("Ownership check failed")
        self.record(name)

    def enforce_exception(self):
        self.run("Promote policies to Deny", ["bash", "policies/set-mode.sh", "enforce"])
        self.admission("deny-compliant", self.fixture("good"))
        for fixture, policy in (("privileged", "disallow-privileged"), ("override-root", "require-non-root"),
                                ("missing-limits", "require-resource-limits")):
            self.admission("deny-" + fixture, self.fixture(fixture), allowed=False, policy=policy)
        result = self.run("Render bounded exception", [str(ROOT / ".venv/bin/python"), "policies/render-exception.py",
            "--minutes", "1", "--ticket", "CI-LAB-04", "--approver", "disposable-ci-operator",
            "--reason", "Synthetic server-dry-run expiry validation"])
        exception = json.loads(result.stdout)
        exception_path = self.report / "exception.json"
        exception_path.write_text(json.dumps(exception, indent=2) + "\n")
        guard = json.loads(self.run("Render derived deadline guard", [str(ROOT / ".venv/bin/python"),
            "policies/render-exception.py", "--guard-for", str(exception_path)]).stdout)
        guard_name = guard["metadata"]["name"]
        (self.report / "deadline-guard.json").write_text(json.dumps(guard, indent=2) + "\n")
        self.apply_object("Install deadline guard before granting exception", guard)
        self.wait_policies_ready((guard_name,))
        self.record("exception-deadline-guard-ready")
        self.apply_object("Apply bounded exception", exception)
        initial = json.loads(self.kube("Snapshot admitted exception", "-n", "policy-exceptions", "get",
            "policyexception.policies.kyverno.io", "reference-limits-exercise", "-o", "json").stdout)
        if not exception_preserves_rendered_spec(exception, initial):
            raise RuntimeError("Admitted exception changed explicitly rendered policy scope or expiry")
        self.admission("exception-exact-object", self.fixture("missing-limits"))
        self.admission("exception-does-not-cover-other-object", self.fixture("init-missing-limits"),
                       allowed=False, policy="require-resource-limits")
        expiry = dt.datetime.fromisoformat(exception["spec"]["expiresAt"].replace("Z", "+00:00"))
        while dt.datetime.now(dt.timezone.utc) <= expiry + dt.timedelta(seconds=2):
            time.sleep(1)
        self.admission("exception-expired-guard-denial", self.fixture("missing-limits"), allowed=False, policy=guard_name)
        retained = json.loads(self.kube("Exception retained after deadline", "-n", "policy-exceptions", "get",
            "policyexception.policies.kyverno.io", "reference-limits-exercise", "-o", "json").stdout)
        if not exception_snapshot_unchanged(initial, retained):
            raise RuntimeError("Exception changed or was deleted before the deadline assertion")
        self.record("expired-exception-retained-without-refresh")
        corrected = yaml.safe_load(self.fixture("good").read_text())
        corrected["metadata"]["name"] = "missing-limits"
        corrected_path = self.scratch / "corrected-missing-limits.json"
        corrected_path.write_text(json.dumps(corrected))
        self.admission("expired-exception-corrected-object-accepted", corrected_path)
        self.kube("Remove expired exception", "-n", "policy-exceptions", "delete",
                  "policyexception.policies.kyverno.io", "reference-limits-exercise")
        self.admission("original-limits-restored-after-revocation", self.fixture("missing-limits"),
                       allowed=False, policy="require-resource-limits")
        self.kube("Remove deadline guard after original enforcement restored", "delete", "validatingpolicy", guard_name)

    def network_rollback(self):
        result = self.run("Network boundary Jobs", ["bash", "projects/k8s-gitops/check-network.sh"])
        if "PASS: labelled client reached" not in result.stdout or "PASS: unlabelled client timed out" not in result.stdout:
            raise RuntimeError("Both network assertions must produce their expected PASS message")
        self.record("network-ingress-allowed-and-denied")
        self.kube("Initial rollout history", "-n", CLUSTER, "rollout", "history", "deployment/sample-api")
        self.kube("Introduce missing local image", "-n", CLUSTER, "set", "image", "deployment/sample-api",
                  "sample-api=devsecops-reference:missing-local-tag")
        result = self.kube("Expected failed rollout", "-n", CLUSTER, "rollout", "status", "deployment/sample-api", "--timeout=45s", check=False)
        pods = json.loads(self.kube("Failed rollout Pods", "-n", CLUSTER, "get", "pods", "-l", "app=sample-api", "-o", "json").stdout)
        reasons = [c.get("state", {}).get("waiting", {}).get("reason") for p in pods["items"]
                   for c in p.get("status", {}).get("containerStatuses", [])]
        if result.returncode == 0 or "ErrImageNeverPull" not in reasons:
            raise RuntimeError("The missing local image did not produce the intended rollout failure")
        diff = self.kube("Detect drift", "diff", "-k", "projects/k8s-gitops/base", check=False)
        if diff.returncode != 1 or "missing-local-tag" not in diff.stdout:
            raise RuntimeError("Drift was not detected as expected")
        self.http_checks("old-revision-remains-healthy")
        self.kube("Rollback", "-n", CLUSTER, "rollout", "undo", "deployment/sample-api")
        self.kube("Recovered rollout", "-n", CLUSTER, "rollout", "status", "deployment/sample-api", "--timeout=120s")
        self.kube("No remaining drift", "diff", "-k", "projects/k8s-gitops/base")
        self.start_forward()
        self.http_checks("recovered-api")
        self.record("drift-and-rollback")

    def signed_release(self):
        """Read-only GHCR access; no publishing or signing by this harness."""
        docker_config = self.scratch / "registry-auth"
        docker_config.mkdir(mode=0o700)
        self.env["DOCKER_CONFIG"] = str(docker_config)
        token, user = os.getenv("REGISTRY_TOKEN", ""), os.getenv("REGISTRY_USER", "")
        pull_secrets = []
        if token:
            if not user or ":" in user:
                raise RuntimeError("REGISTRY_USER is required with REGISTRY_TOKEN")
            authorization = base64.b64encode(f"{user}:{token}".encode()).decode()
            config = json.dumps({"auths": {"ghcr.io": {"auth": authorization}}})
            encoded = base64.b64encode(config.encode()).decode()
            self.redact.extend([authorization, config, encoded])
            config_path = docker_config / "config.json"
            config_path.write_text(config)
            config_path.chmod(0o600)
            self.apply_object("Ephemeral registry pull credential", {"apiVersion": "v1", "kind": "Secret",
                "metadata": {"name": "reference-registry", "namespace": CLUSTER},
                "type": "kubernetes.io/dockerconfigjson", "data": {".dockerconfigjson": encoded}})
            pull_secrets = [{"name": "reference-registry"}]
        self.run("Verify exact release signature", ["cosign", "verify", "--certificate-identity", IDENTITY,
                 "--certificate-oidc-issuer", "https://token.actions.githubusercontent.com", self.reference])
        self.run("Pull immutable release", ["docker", "pull", "--platform", "linux/amd64", self.reference], timeout=300)
        architecture = self.run("Release architecture", ["docker", "image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", self.reference])
        if architecture.stdout.strip() != "linux/amd64":
            raise RuntimeError("Release does not contain the required Linux amd64 image")
        self.run("Add Sigstore chart", ["helm", "repo", "add", "sigstore", "https://sigstore.github.io/helm-charts"])
        # The chart currently lags the controller release. Explicitly override
        # its image with the v0.15.1 multi-platform digest from GHCR; record both.
        self.run("Install provenance admission controller", ["helm", "upgrade", "--install", "policy-controller",
            "sigstore/policy-controller", "--version", "0.10.8", "--namespace", "cosign-system", "--create-namespace",
            "--kube-context", CONTEXT, "--set-string",
            "webhook.image.version=sha256:0492bb264fb1d9bdc8e3f343ef542cc85b7dd7c7fd8d9524b453c2bd31a1d128",
            "--set-string", "webhook.configData.enable-oci11=true",
            "--set-string", "webhook.configData.no-match-policy=deny", "--wait", "--timeout", "5m"], timeout=360)
        self.kube("Release provenance policy", "apply", "-f", "configs/cosign-policy.yaml")
        self.kube("Provenance policy ready", "wait", "--for=condition=Ready", "clusterimagepolicy/require-reference-release-provenance", "--timeout=120s")
        self.kube("Opt in only reference namespace", "label", "namespace", CLUSTER, "policy.sigstore.dev/include=true")
        deployment = yaml.safe_load((ROOT / "projects/k8s-gitops/base/deployment.yaml").read_text())
        deployment["metadata"]["namespace"] = CLUSTER
        spec = deployment["spec"]["template"]["spec"]
        spec["containers"][0].update({"image": self.reference, "imagePullPolicy": "IfNotPresent"})
        if pull_secrets:
            spec["imagePullSecrets"] = pull_secrets
        signed = self.scratch / "signed-deployment.json"
        signed.write_text(json.dumps(deployment))
        self.admission("signed-provenance-accepted", signed)
        wrong = yaml.safe_load((ROOT / "configs/cosign-policy.yaml").read_text())
        wrong["metadata"]["name"] = "reference-wrong-identity-test"
        wrong["spec"]["authorities"][0]["keyless"]["identities"][0]["subject"] = IDENTITY.replace("release.yml", "not-the-release.yml")
        self.apply_object("Additional deliberately wrong identity policy", wrong)
        self.kube("Wrong identity policy ready", "wait", "--for=condition=Ready", "clusterimagepolicy/reference-wrong-identity-test", "--timeout=120s")
        self.admission("wrong-identity-rejected", signed, allowed=False, policy="reference-wrong-identity-test")
        self.kube("Remove additional identity test policy", "delete", "clusterimagepolicy", "reference-wrong-identity-test")
        self.admission("trusted-identity-restored", signed)
        unmatched = copy.deepcopy(deployment)
        # An unrelated, digest-pinned public base image tests the unmatched-image
        # boundary only. Do not mislabel it as missing-signature verification.
        base_image = (ROOT / "samples/sample-api/Dockerfile").read_text().splitlines()[0].split()[1]
        unmatched["spec"]["template"]["spec"]["containers"][0]["image"] = base_image
        unmatched_path = self.scratch / "unmatched-deployment.json"
        unmatched_path.write_text(json.dumps(unmatched))
        self.admission("unmatched-image-rejected", unmatched_path, allowed=False, policy="no matching policies")
        self.kube("Deploy verified release", "apply", "-f", str(signed))
        self.kube("Verified release rollout", "-n", CLUSTER, "rollout", "status", "deployment/sample-api", "--timeout=180s", timeout=210)
        self.start_forward()
        self.http_checks("released-api")
        self.record("signed-release-provenance-and-identity")

    def cleanup(self):
        self.stop_forward()
        if self.creation_attempted and not self.created:
            # A hard timeout can interrupt Kind before its own partial-create
            # cleanup. Report leftovers explicitly; don't claim ownership of a
            # cluster whose create operation never completed successfully.
            result = self.run("Check partial Kind creation", ["docker", "ps", "-a", "--filter",
                f"label=io.x-k8s.kind.cluster={CLUSTER}", "--format", "{{.ID}} {{.Names}}"], check=False)
            if result.returncode or result.stdout.strip():
                self.record("partial-creation-cleanup", "unconfirmed; inspect commands.log and dispose of the dedicated CI runner")
        if self.created:
            for name, args in (("Cluster Pods", ["get", "pods", "-A", "-o", "wide"]),
                               ("Cluster events", ["get", "events", "-A", "--sort-by=.lastTimestamp"]),
                               ("Policy status", ["get", "validatingpolicies", "-o", "yaml"]),
                               ("Policy reports", ["get", "policyreports", "-A", "-o", "yaml"])):
                try:
                    self.kube(name, *args, check=False, timeout=100)
                except (OSError, subprocess.SubprocessError):
                    pass
            for namespace, deployment in (("kyverno", "kyverno-admission-controller"),
                                          ("kyverno", "kyverno-reports-controller"),
                                          (CLUSTER, "sample-api"),
                                          ("cosign-system", "policy-controller-webhook")):
                try:
                    self.kube(deployment + " diagnostic logs", "-n", namespace, "logs", "deployment/" + deployment,
                              "--all-containers", "--tail=100", check=False, timeout=30)
                except (OSError, subprocess.SubprocessError):
                    pass
            result = self.run("Delete owned Kind cluster", ["kind", "delete", "cluster", "--name", CLUSTER,
                "--kubeconfig", self.env["KUBECONFIG"]], check=False, timeout=180)
            if result.returncode:
                raise RuntimeError("Owned Kind cleanup failed; inspect runner and commands.log")
            self.created = False
            self.record("owned-cluster-cleaned-up")
        self.temp.cleanup()

    def execute(self):
        failure = None
        try:
            self.preflight()
            self.start()
            self.audit_deploy()
            self.enforce_exception()
            self.network_rollback()
            if self.reference:
                self.signed_release()
            else:
                self.record("signed-release", "not requested; no admission claim")
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, URLError) as error:
            failure = str(error)
        finally:
            try:
                self.cleanup()
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                failure = (failure + "; " if failure else "") + str(error)
            summary = {"status": "failed" if failure else "passed", "failure": failure,
                       "image_reference": self.reference or None, "checks": self.steps,
                       "limitations": ["No ArgoCD/Flux reconciliation or organizational approval routing.",
                                       "Network Jobs verify ingress; egress configuration is not dynamically tested.",
                                       "Signed path tests trusted provenance, wrong identity and unmatched images; no unsigned same-repository artifact is published."]}
            (self.report / "result.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(f"Evidence: {self.report}", flush=True)
            if failure:
                print(f"FAILED: {failure}", flush=True)
        return 1 if failure else 0


def main():
    # SIGTERM from CI cancellation still runs the finally cleanup. SIGKILL or a
    # destroyed runner cannot be trapped; the dedicated hosted VM is ephemeral.
    def interrupted(_signum, _frame):
        raise RuntimeError("Validation interrupted")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    return Validation().execute()


if __name__ == "__main__":
    raise SystemExit(main())
