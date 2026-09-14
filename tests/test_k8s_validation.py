"""Offline guardrails, not a substitute for the disposable-cluster integration."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("k8s_validation", ROOT / "projects/k8s-gitops/validate_live.py")
k8s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(k8s)


class K8sValidationTests(unittest.TestCase):
    def test_kyverno_readiness_uses_live_nested_status_and_all_named_policies(self):
        document = {"items": [{"metadata": {"name": name}, "status": {
            "conditionStatus": {"ready": True, "conditions": [
                {"type": "WebhookConfigured", "status": "True"},
                {"type": "RBACPermissionsGranted", "status": "True"}]}}} for name in k8s.POLICIES]}
        self.assertTrue(k8s.kyverno_policies_ready(document))
        # This reproduces the first live run's failed report-permission state.
        document["items"][0]["status"]["conditionStatus"]["ready"] = False
        document["items"][0]["status"]["conditionStatus"]["conditions"][1]["status"] = "False"
        self.assertFalse(k8s.kyverno_policies_ready(document))
        document["items"][0]["status"] = {"conditions": [{"type": "Ready", "status": "True"}]}
        self.assertFalse(k8s.kyverno_policies_ready(document))
        self.assertFalse(k8s.kyverno_policies_ready({"items": document["items"][1:]}))
        self.assertFalse(k8s.kyverno_policies_ready({}))

    def test_reporting_permission_is_read_only_exact_resource_and_controller(self):
        role, binding = list(yaml.safe_load_all((ROOT / 'projects/k8s-gitops/kyverno-report-rbac.yaml').read_text()))
        self.assertEqual(role['rules'], [{'apiGroups': [''], 'resources': ['pods/ephemeralcontainers'],
                                         'verbs': ['get', 'list', 'watch']}])
        self.assertEqual(binding['roleRef']['name'], role['metadata']['name'])
        self.assertEqual(binding['subjects'], [{'kind': 'ServiceAccount', 'name': 'kyverno-reports-controller', 'namespace': 'kyverno'}])
        for name in k8s.POLICIES:
            policy = yaml.safe_load((ROOT / 'policies/kyverno' / (name + '.yaml')).read_text())
            matched = [resource for rule in policy['spec']['matchConstraints']['resourceRules'] for resource in rule['resources']]
            self.assertIn('pods/ephemeralcontainers', matched)
            self.assertTrue(policy['spec']['evaluation']['background']['enabled'])

    def test_only_exact_reference_repository_digest_is_accepted(self):
        valid = "ghcr.io/djvirus9/awesome-devsecops-mastery-2026/sample-api@sha256:" + "a" * 64
        self.assertEqual(k8s.validate_image_reference(valid), valid)
        self.assertEqual(k8s.validate_image_reference(""), "")
        for value in [valid.replace("sample-api", "elsewhere"), valid + "\n", valid.replace("@sha256:", ":"), "--help"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                k8s.validate_image_reference(value)

    def test_policy_negative_requires_intended_denial_not_transport_error(self):
        def result(text, code=1):
            return subprocess.CompletedProcess([], code, text)
        self.assertTrue(k8s.admission_matches(result('admission denied: disallow-privileged'), False, 'disallow-privileged'))
        for text in ['invalid Pod security context', 'failed calling webhook disallow-privileged: denied',
                     'connection refused', 'admission denied: a-different-policy']:
            self.assertFalse(k8s.admission_matches(result(text), False, 'disallow-privileged'))
        self.assertFalse(k8s.admission_matches(result('disallow-privileged', 0), False, 'disallow-privileged'))

    def test_audit_requires_success_and_named_warning(self):
        self.assertTrue(k8s.admission_matches(subprocess.CompletedProcess([], 0, 'Warning: disallow-privileged'), True, 'disallow-privileged'))
        self.assertFalse(k8s.admission_matches(subprocess.CompletedProcess([], 0, 'created (server dry run)'), True, 'disallow-privileged'))

    def test_privileged_fixtures_do_not_fail_native_api_conflict(self):
        # Kubernetes rejects privileged=true with escalation=false before the
        # intended Audit acceptance. Covers regular, init and ephemeral cases.
        for fixture in ['privileged', 'init-privileged', 'ephemeral-privileged']:
            obj = yaml.safe_load((ROOT / 'policies/fixtures' / (fixture + '.yaml')).read_text())
            containers = sum((obj['spec'].get(key, []) for key in ['containers', 'initContainers', 'ephemeralContainers']), [])
            privileged = [c for c in containers if c.get('securityContext', {}).get('privileged')]
            self.assertTrue(privileged)
            for container in privileged:
                self.assertTrue(container['securityContext']['allowPrivilegeEscalation'])

    def test_loopback_redirects_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'redirect'):
            k8s.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://example.com')

    def test_cleanup_does_not_delete_preexisting_cluster(self):
        validation = object.__new__(k8s.Validation)
        validation.created = False
        validation.creation_attempted = False
        validation.forward = None
        validation.forward_log = None
        with tempfile.TemporaryDirectory() as temporary:
            validation.temp = tempfile.TemporaryDirectory(dir=temporary)
            with patch.object(validation, 'run') as run:
                validation.cleanup()
                run.assert_not_called()

    def test_private_environment_isolated_and_credential_redacted(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(k8s, 'ROOT', Path(temporary)), \
                patch.dict(os.environ, {'KUBECONFIG': '/unrelated/config', 'REGISTRY_TOKEN': 'sensitive-example-value'}):
            validation = k8s.Validation()
            self.assertNotEqual(validation.env['KUBECONFIG'], '/unrelated/config')
            self.assertNotIn('REGISTRY_TOKEN', validation.env)
            response = subprocess.CompletedProcess([], 0, 'sensitive-example-value')
            with patch.object(k8s.subprocess, 'run', return_value=response):
                validation.run('redaction check', ['unused'])
            self.assertNotIn('sensitive-example-value', (validation.report / 'commands.log').read_text())
            validation.cleanup()

    def test_provenance_policy_requires_bundle_predicate_and_exact_identity(self):
        policy = yaml.safe_load((ROOT / 'configs/cosign-policy.yaml').read_text())
        authority = policy['spec']['authorities'][0]
        self.assertEqual(authority['signatureFormat'], 'bundle')
        self.assertEqual(authority['attestations'][0]['predicateType'], 'https://slsa.dev/provenance/v1')
        self.assertEqual(authority['keyless']['identities'], [{'issuer': 'https://token.actions.githubusercontent.com', 'subject': k8s.IDENTITY}])


if __name__ == '__main__':
    unittest.main()
