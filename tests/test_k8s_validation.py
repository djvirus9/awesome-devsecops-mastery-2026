"""Offline guardrails, not a substitute for the disposable-cluster integration."""
import importlib.util
import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("k8s_validation", ROOT / "projects/k8s-gitops/validate_live.py")
k8s = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(k8s)
RENDER_SPEC = importlib.util.spec_from_file_location("exception_renderer", ROOT / "policies/render-exception.py")
renderer = importlib.util.module_from_spec(RENDER_SPEC)
RENDER_SPEC.loader.exec_module(renderer)


class K8sValidationTests(unittest.TestCase):
    def test_rendered_exception_uses_native_expiry_and_supported_scope_only(self):
        before = dt.datetime.now(dt.timezone.utc)
        command = [sys.executable, str(ROOT / 'policies/render-exception.py'), '--minutes', '1',
                   '--ticket', 'TEST', '--approver', 'local-test', '--reason', 'native expiry regression']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        spec = json.loads(result.stdout)['spec']
        expiry = dt.datetime.fromisoformat(spec['expiresAt'].replace('Z', '+00:00'))
        self.assertGreater(expiry, before + dt.timedelta(seconds=58))
        self.assertLess(expiry, dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=61))
        self.assertEqual(spec['policyRefs'], [{'name': 'require-resource-limits', 'kind': 'ValidatingPolicy'}])
        self.assertEqual(len(spec['matchConditions']), 1)
        expression = spec['matchConditions'][0]['expression']
        self.assertNotIn('time.', expression)
        self.assertIn("object.metadata.name == 'missing-limits'", expression)
        self.assertIn("object.metadata.namespace == 'devsecops-reference'", expression)
        for minutes in ['0', '121']:
            invalid = command.copy()
            invalid[invalid.index('--minutes') + 1] = minutes
            self.assertNotEqual(subprocess.run(invalid, capture_output=True).returncode, 0)

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
        single = {"kind": "ValidatingPolicy", "metadata": {"name": renderer.GUARD_NAME},
                  "status": {"conditionStatus": {"ready": True}}}
        self.assertTrue(k8s.kyverno_policies_ready(single, (renderer.GUARD_NAME,)))
        self.assertFalse(k8s.kyverno_policies_ready(single))

    def test_deadline_guard_derives_original_validation_and_covers_all_pod_paths(self):
        exception = yaml.safe_load((ROOT / 'policies/kyverno/tests/exception-active/exception.yaml').read_text())
        original = yaml.safe_load((ROOT / 'policies/kyverno/require-resource-limits.yaml').read_text())
        guard = renderer.deadline_guard(exception)
        self.assertEqual(guard['metadata']['name'], renderer.GUARD_NAME)
        self.assertNotIn(renderer.GUARD_NAME, [ref['name'] for ref in exception['spec']['policyRefs']])
        self.assertEqual(guard['spec']['validationActions'], ['Deny'])
        self.assertEqual(guard['spec']['failurePolicy'], 'Fail')
        self.assertFalse(guard['spec']['evaluation']['background']['enabled'])
        self.assertEqual(guard['spec']['variables'], original['spec']['variables'])
        self.assertEqual(guard['spec']['matchConstraints']['resourceRules'], [original['spec']['matchConstraints']['resourceRules'][0]])
        self.assertEqual(guard['spec']['matchConditions'][-1]['expression'], renderer.EXACT_OBJECT)
        for source, validation in zip(original['spec']['validations'], guard['spec']['validations'], strict=True):
            self.assertEqual(validation['expression'], 'time.now() < timestamp("2099-01-01T00:00:00Z") || (' + source['expression'] + ')')
        for field, bad in [('policyRefs', []), ('matchConditions', []), ('expiresAt', '2099-01-01')]:
            altered = copy.deepcopy(exception)
            altered['spec'][field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError):
                renderer.deadline_guard(altered)

    def test_deadline_workflow_grants_only_after_guard_and_revokes_before_cleanup(self):
        validation = object.__new__(k8s.Validation)
        exception = yaml.safe_load((ROOT / 'policies/kyverno/tests/exception-expired/exception.yaml').read_text())
        guard = renderer.deadline_guard(exception)
        persisted = copy.deepcopy(exception)
        # The live API defaults this field. Comparing to the submitted manifest
        # previously failed despite successful, unchanged deadline enforcement.
        persisted['spec']['reportResult'] = 'skip'
        persisted['metadata'].update({'uid': 'local-test-uid', 'generation': 1})
        events = []

        def run(name, *args, **kwargs):
            events.append(name)
            obj = guard if name == 'Render derived deadline guard' else exception
            return subprocess.CompletedProcess([], 0, json.dumps(obj))

        def kube(name, *args, **kwargs):
            events.append(name)
            return subprocess.CompletedProcess([], 0, json.dumps(persisted))

        def admission(name, manifest, **kwargs):
            events.append(name)
            if name == 'exception-expired-guard-denial':
                self.assertFalse(kwargs['allowed'])
                self.assertEqual(kwargs['policy'], renderer.GUARD_NAME)
            if name == 'original-limits-restored-after-revocation':
                self.assertEqual(kwargs['policy'], 'require-resource-limits')
            if name == 'expired-exception-corrected-object-accepted':
                corrected = json.loads(manifest.read_text())
                self.assertEqual(corrected['metadata']['name'], 'missing-limits')
                self.assertIn('limits', corrected['spec']['containers'][0]['resources'])

        with tempfile.TemporaryDirectory() as temporary:
            validation.report = validation.scratch = Path(temporary)
            with patch.object(validation, 'run', side_effect=run), patch.object(validation, 'kube', side_effect=kube), \
                    patch.object(validation, 'apply_object', side_effect=lambda name, obj: events.append(name)), \
                    patch.object(validation, 'wait_policies_ready', side_effect=lambda names: events.append('guard-ready')), \
                    patch.object(validation, 'admission', side_effect=admission), patch.object(validation, 'record'):
                validation.enforce_exception()
        ordered = ['Install deadline guard before granting exception', 'guard-ready', 'Apply bounded exception',
                   'Snapshot admitted exception', 'exception-exact-object', 'exception-expired-guard-denial', 'Exception retained after deadline',
                   'expired-exception-corrected-object-accepted', 'Remove expired exception',
                   'original-limits-restored-after-revocation', 'Remove deadline guard after original enforcement restored']
        positions = [events.index(name) for name in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_exception_snapshot_accepts_defaulting_but_detects_scope_change_or_replacement(self):
        rendered = yaml.safe_load((ROOT / 'policies/kyverno/tests/exception-active/exception.yaml').read_text())
        persisted = copy.deepcopy(rendered)
        persisted['spec']['reportResult'] = 'skip'
        persisted['metadata'].update({'uid': 'live-shaped-uid', 'generation': 1, 'resourceVersion': '1167'})
        self.assertTrue(k8s.exception_preserves_rendered_spec(rendered, persisted))
        self.assertTrue(k8s.exception_snapshot_unchanged(persisted, copy.deepcopy(persisted)))
        changed_version = copy.deepcopy(persisted)
        changed_version['metadata']['resourceVersion'] = '1168'
        self.assertTrue(k8s.exception_snapshot_unchanged(persisted, changed_version))
        for key, value in [('expiresAt', '2099-02-01T00:00:00Z'), ('policyRefs', []), ('matchConditions', [])]:
            modified = copy.deepcopy(persisted)
            modified['spec'][key] = value
            with self.subTest(spec=key):
                self.assertFalse(k8s.exception_preserves_rendered_spec(rendered, modified))
                self.assertFalse(k8s.exception_snapshot_unchanged(persisted, modified))
        for key, value in [('uid', 'replacement-uid'), ('generation', 2), ('deletionTimestamp', '2099-01-01T00:00:00Z'),
                           ('name', 'other-exception'), ('namespace', 'other-namespace')]:
            modified = copy.deepcopy(persisted)
            modified['metadata'][key] = value
            with self.subTest(metadata=key):
                self.assertFalse(k8s.exception_snapshot_unchanged(persisted, modified))
        missing_uid = copy.deepcopy(persisted)
        del missing_uid['metadata']['uid']
        self.assertFalse(k8s.exception_snapshot_unchanged(missing_uid, persisted))

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

    def test_networkpolicy_deny_egress_uses_api_canonical_no_rule_form(self):
        policy = yaml.safe_load((ROOT / 'projects/k8s-gitops/base/network-policy.yaml').read_text())
        spec = policy['spec']
        self.assertEqual(spec['podSelector'], {'matchLabels': {'app': 'sample-api'}})
        self.assertEqual(set(spec['policyTypes']), {'Ingress', 'Egress'})
        # In v1.35.8, egress:[] is omitted on API read but reflect.DeepEqual
        # distinguishes it from nil on update, producing generation-only drift.
        # No egress key plus explicit Egress isolation still grants no outbound
        # allowance. [{}] would instead allow everything and must not be added.
        self.assertNotIn('egress', spec)
        self.assertEqual(spec['ingress'], [{'from': [{'podSelector': {'matchLabels': {'access': 'sample-api'}}}],
                                           'ports': [{'protocol': 'TCP', 'port': 8080}]}])

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
