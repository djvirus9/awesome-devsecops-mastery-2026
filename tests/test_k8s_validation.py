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


BOOTSTRAP_PREFIX = ('Error from server (InternalError): error when creating "policies/kyverno/require-non-root.yaml": '
                    'Internal error occurred: failed calling webhook "validate-policy.kyverno.svc": ')
BOOTSTRAP_REFUSED = (BOOTSTRAP_PREFIX + 'failed to call webhook: Post '
                    '"https://kyverno-svc.kyverno.svc:443/policyvalidate?timeout=10s": '
                    'dial tcp 192.0.2.10:443: connect: connection refused')
BOOTSTRAP_NO_ENDPOINTS = BOOTSTRAP_PREFIX + 'no endpoints available for service "kyverno-svc"'


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class K8sValidationTests(unittest.TestCase):
    def test_bootstrap_classifies_only_exact_webhook_startup_errors(self):
        permitted = [BOOTSTRAP_REFUSED, BOOTSTRAP_NO_ENDPOINTS,
                     BOOTSTRAP_PREFIX + 'failed to call webhook: no endpoints available for service "kyverno-svc"',
                     BOOTSTRAP_REFUSED.replace('192.0.2.10', '[2001:db8::10]')]
        for text in permitted:
            with self.subTest(text=text):
                self.assertTrue(k8s.kyverno_bootstrap_unavailable(subprocess.CompletedProcess([], 1, text + '\n')))
                self.assertFalse(k8s.kyverno_bootstrap_unavailable(subprocess.CompletedProcess([], 0, text)))
        rejected = [
            BOOTSTRAP_REFUSED.replace('validate-policy.kyverno.svc', 'validate-policy.kyverno.svc.other'),
            BOOTSTRAP_REFUSED.replace('kyverno-svc.kyverno.svc:443', 'other-service.kyverno.svc:443'),
            BOOTSTRAP_REFUSED.replace('/policyvalidate?', '/other-path?'),
            BOOTSTRAP_NO_ENDPOINTS.replace('service "kyverno-svc"', 'service "kyverno-svc-other"'),
            BOOTSTRAP_REFUSED.replace('connect: connection refused', 'context deadline exceeded'),
            BOOTSTRAP_REFUSED.replace('connect: connection refused', 'x509: certificate signed by unknown authority'),
            BOOTSTRAP_PREFIX + 'admission denied: invalid policy',
            BOOTSTRAP_PREFIX + 'remote error: tls: internal error',
            'Error from server (Forbidden): insufficient RBAC permissions',
            'Error from server (Invalid): unknown field in policy',
            'dial tcp 192.0.2.10:443: connect: connection refused',
            BOOTSTRAP_REFUSED + '\nError from server (Forbidden): another failure',
        ]
        for text in rejected:
            with self.subTest(text=text):
                self.assertFalse(k8s.kyverno_bootstrap_unavailable(subprocess.CompletedProcess([], 1, text)))

    def test_bootstrap_retries_availability_errors_and_logs_every_attempt(self):
        for text in (BOOTSTRAP_REFUSED, BOOTSTRAP_NO_ENDPOINTS):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as temporary:
                validation = object.__new__(k8s.Validation)
                validation.report, validation.env, validation.redact = Path(temporary), {}, []
                responses = [subprocess.CompletedProcess([], 1, text)] + [
                    subprocess.CompletedProcess([], 0, 'created') for _ in k8s.POLICIES]
                with patch.object(k8s.subprocess, 'run', side_effect=responses) as run, \
                        patch.object(k8s.time, 'monotonic', return_value=0), patch.object(k8s.time, 'sleep') as sleep:
                    validation.apply_initial_policies()
                self.assertEqual(run.call_count, 5)
                sleep.assert_called_once_with(2)
                paths = [call.args[0][-1] for call in run.call_args_list]
                self.assertEqual(paths, [f'policies/kyverno/{name}.yaml' for name in (k8s.POLICIES[0], *k8s.POLICIES)])
                for call in run.call_args_list:
                    self.assertIn('--request-timeout=10000ms', call.args[0])
                    self.assertEqual(call.args[0][1:3], ['--context', k8s.CONTEXT])
                    self.assertEqual(call.kwargs['timeout'], 15)
                log = (validation.report / 'commands.log').read_text()
                self.assertEqual(log.count('## Apply '), 5)
                self.assertIn('bootstrap attempt 1) (exit 1)', log)
                self.assertIn('bootstrap attempt 2) (exit 0)', log)

    def test_bootstrap_permanent_error_fails_without_retry(self):
        validation = object.__new__(k8s.Validation)
        result = subprocess.CompletedProcess([], 1, BOOTSTRAP_PREFIX + 'admission denied: invalid policy')
        with patch.object(validation, 'kube', return_value=result) as kube, \
                patch.object(k8s.time, 'monotonic', return_value=0), patch.object(k8s.time, 'sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError, 'without a retryable startup error'):
                validation.apply_initial_policies()
        kube.assert_called_once()
        sleep.assert_not_called()

    def test_bootstrap_transient_then_permanent_error_stops(self):
        validation = object.__new__(k8s.Validation)
        responses = [subprocess.CompletedProcess([], 1, BOOTSTRAP_REFUSED),
                     subprocess.CompletedProcess([], 1, 'Error from server (Forbidden): access denied')]
        with patch.object(validation, 'kube', side_effect=responses) as kube, \
                patch.object(k8s.time, 'monotonic', return_value=0), patch.object(k8s.time, 'sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError, 'without a retryable startup error'):
                validation.apply_initial_policies()
        self.assertEqual(kube.call_count, 2)
        sleep.assert_called_once_with(2)

    def test_bootstrap_deadline_is_shared_and_bounds_calls_and_sleep(self):
        validation = object.__new__(k8s.Validation)
        clock = FakeClock()

        def apply(name, *args, **kwargs):
            if args[-1].endswith('require-non-root.yaml'):
                self.assertEqual(kwargs['timeout'], 15)
                self.assertEqual(kwargs['request_timeout'], '10000ms')
                clock.now = 119.25
                return subprocess.CompletedProcess([], 0, 'created')
            self.assertEqual(kwargs['timeout'], 0.75)
            self.assertEqual(kwargs['request_timeout'], '750ms')
            clock.now = 119.5
            return subprocess.CompletedProcess([], 1, BOOTSTRAP_REFUSED)

        with patch.object(validation, 'kube', side_effect=apply) as kube, \
                patch.object(k8s.time, 'monotonic', side_effect=clock.monotonic), \
                patch.object(k8s.time, 'sleep', side_effect=clock.sleep):
            with self.assertRaisesRegex(RuntimeError, 'initial policy admission timed out'):
                validation.apply_initial_policies()
        self.assertEqual(kube.call_count, 2)
        self.assertEqual(clock.sleeps, [0.5])
        self.assertEqual(clock.now, 120)

    def test_bootstrap_never_issues_zero_timeout_near_deadline(self):
        validation = object.__new__(k8s.Validation)
        with patch.object(validation, 'kube') as kube, \
                patch.object(k8s.time, 'monotonic', side_effect=[0, 119.9995]):
            with self.assertRaisesRegex(RuntimeError, 'initial policy admission timed out'):
                validation.apply_initial_policies()
        kube.assert_not_called()

    def test_bootstrap_late_success_does_not_extend_deadline(self):
        validation = object.__new__(k8s.Validation)
        with patch.object(validation, 'kube', return_value=subprocess.CompletedProcess([], 0, 'created')) as kube, \
                patch.object(k8s.time, 'monotonic', side_effect=[0, 0, 120]):
            with self.assertRaisesRegex(RuntimeError, 'initial policy admission timed out'):
                validation.apply_initial_policies()
        kube.assert_called_once()

    def test_bootstrap_subprocess_timeout_logs_redacted_partial_output_and_stops(self):
        with tempfile.TemporaryDirectory() as temporary:
            validation = object.__new__(k8s.Validation)
            validation.report, validation.env, validation.redact = Path(temporary), {}, ['synthetic-private-value']
            failure = subprocess.TimeoutExpired(['kubectl'], 15, output=b'synthetic-private-value\xff')
            with patch.object(k8s.subprocess, 'run', side_effect=failure) as run, \
                    patch.object(k8s.time, 'monotonic', return_value=0), patch.object(k8s.time, 'sleep') as sleep:
                with self.assertRaises(subprocess.TimeoutExpired):
                    validation.apply_initial_policies()
            run.assert_called_once()
            sleep.assert_not_called()
            log = (validation.report / 'commands.log').read_text()
            self.assertIn('(timed out)', log)
            self.assertIn('[REDACTED]', log)
            self.assertNotIn('synthetic-private-value', log)

    def test_kube_retains_default_request_timeout_and_accepts_bounded_override(self):
        validation = object.__new__(k8s.Validation)
        with patch.object(validation, 'run') as run:
            validation.kube('default', 'get', 'pods')
            self.assertIn('--request-timeout=90s', run.call_args.args[1])
            validation.kube('bounded', 'get', 'pods', request_timeout='750ms', timeout=0.75)
            self.assertIn('--request-timeout=750ms', run.call_args.args[1])
            self.assertEqual(run.call_args.kwargs['timeout'], 0.75)

    def test_start_still_applies_all_policies_before_readiness_and_success(self):
        validation = object.__new__(k8s.Validation)
        validation.env = {'KUBECONFIG': '/unused-test-config'}
        events = []

        def command(name, *args, **kwargs):
            events.append(name)
            return subprocess.CompletedProcess([], 0, 'created')

        with patch.object(validation, 'run', side_effect=command), patch.object(validation, 'kube', side_effect=command), \
                patch.object(validation, 'wait_policies_ready', side_effect=lambda: events.append('policies-ready')), \
                patch.object(validation, 'record', side_effect=events.append), \
                patch.object(k8s.time, 'monotonic', return_value=0):
            validation.start()
        ordered = ['Install Kyverno', 'Ephemeral-container reporting permission'] + [
            f'Apply {policy} (bootstrap attempt 1)' for policy in k8s.POLICIES] + [
            'policies-ready', 'cluster-cni-and-admission-ready']
        positions = [events.index(name) for name in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(sum(name.startswith('Apply ') for name in events), len(k8s.POLICIES))

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
