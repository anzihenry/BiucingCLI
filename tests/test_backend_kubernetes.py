"""P5 release control-flow tests. Fake API calls are not cluster/HA evidence."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from biucingcli.cli import main


class KubernetesReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        with redirect_stdout(io.StringIO()):
            main(['create', 'web-service', 'release-probe', '--module-name', 'example.org/release/probe',
                  '--output-dir', str(self.base), '--non-interactive'])
        self.root = self.base / 'release-probe'
        self.bundle = self.base / 'bundle'
        self.bundle.mkdir()
        self.image = 'registry.example.com/probe@sha256:' + '1' * 64
        (self.bundle / 'image.txt').write_text(self.image + '\n')
        (self.bundle / 'namespace.txt').write_text('backend-prod\n')
        for file in ('app.yaml', 'migration.yaml'):
            (self.bundle / file).write_text('image: ' + self.image + '\n')
        (self.bundle / 'platform.yaml').write_text('kind: ServiceAccount\n')
        (self.bundle / 'capacity.env').write_bytes((self.root / 'deploy/kubernetes/capacity.env').read_bytes())
        self.seal()
        tools = self.base / 'tools'
        tools.mkdir()
        self.log = self.base / 'calls.jsonl'
        fake = tools / 'kubectl'
        fake.write_text('#!' + sys.executable + '\n' + '''import json, os, sys
args = sys.argv[1:]
with open(os.environ['CALL_LOG'], 'a') as out:
    out.write(json.dumps(args) + '\\n')
fault = os.environ.get('FAULT')
if 'create' in args:
    print('job/schema-migrate-fixture')
if 'get' in args and 'jsonpath={.status.availableReplicas}' in args:
    print('1' if fault == 'replicas' else '3')
if (fault == 'migration' and 'wait' in args) or (fault == 'rollout' and 'rollout' in args) or (fault == 'admission' and '--dry-run=server' in args):
    sys.exit(7)
''')
        fake.chmod(0o755)
        pause = tools / 'sleep'
        pause.write_text('#!/bin/sh\nexit 0\n')
        pause.chmod(0o755)
        (self.root / 'scripts/security').write_text('#!/bin/sh\nprintf "{}\\n"\n')
        self.env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'], CALL_LOG=str(self.log),
                        SIGNER_IDENTITY='exact-test-workflow', SIGNER_ISSUER='https://issuer.example.com')
        self.env.pop('SIGNER_KEY', None)

    def seal(self):
        files = sorted(p for p in self.bundle.iterdir() if p.name != 'SHA256SUMS')
        (self.bundle / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in files))

    def release(self, action='deploy', fault='', context='isolated-test'):
        result = subprocess.run(['./scripts/kube-release', action, context, str(self.bundle)], cwd=self.root,
                                env=dict(self.env, FAULT=fault), capture_output=True, text=True)
        calls = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        return result, calls

    @staticmethod
    def mutating_apply(call):
        return 'apply' in call and '--dry-run=server' not in call

    def test_migration_failure_never_updates_deployment(self):
        result, calls = self.release(fault='migration')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('create' in call for call in calls))
        self.assertFalse(any(self.mutating_apply(call) for call in calls))
        self.assertFalse((self.bundle / 'deployed-context.txt').exists())
        self.assertFalse(any('delete' in call for call in calls))

    def test_failed_admission_stops_before_migration(self):
        result, calls = self.release(fault='admission')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any('create' in call or self.mutating_apply(call) for call in calls))

    def test_rollout_failure_is_not_success_and_has_no_implicit_rollback(self):
        result, calls = self.release(fault='rollout')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sum(self.mutating_apply(call) for call in calls), 1)
        self.assertFalse((self.bundle / 'deployed-context.txt').exists())
        self.assertFalse(any('undo' in call or 'delete' in call for call in calls))

    def test_successful_order_and_rollback_skip_ddl(self):
        result, calls = self.release()
        self.assertEqual(result.returncode, 0, result.stderr)
        create = next(i for i, call in enumerate(calls) if 'create' in call)
        wait = next(i for i, call in enumerate(calls) if 'wait' in call)
        apply = next(i for i, call in enumerate(calls) if self.mutating_apply(call))
        self.assertLess(create, wait)
        self.assertLess(wait, apply)
        self.assertEqual((self.bundle / 'deployed-context.txt').read_text().strip(), 'isolated-test')
        self.log.unlink()
        result, calls = self.release(action='rollback')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any('create' in call or 'wait' in call for call in calls))
        self.assertEqual(sum(self.mutating_apply(call) for call in calls), 1)
        self.log.unlink()
        result, calls = self.release(action='rollback', context='different-cluster')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_tampered_snapshot_is_rejected_before_api_calls(self):
        (self.bundle / 'app.yaml').write_text('image: unverified:latest\n')
        result, calls = self.release(action='preflight')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_budget_counts_terminating_replicas_and_rejects_shell_input(self):
        path = self.bundle / 'capacity.env'
        result = subprocess.run(['./scripts/kube-capacity', str(path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('demand=125 available=170 margin=45', result.stdout)
        path.write_text(path.read_text().replace('DB_MAX_CONNECTIONS=200', 'DB_MAX_CONNECTIONS=140'))
        self.assertNotEqual(subprocess.run(['./scripts/kube-capacity', str(path)], cwd=self.root, capture_output=True).returncode, 0)
        marker = self.base / 'executed'
        path.write_text('MAX_REPLICAS=$(touch ' + str(marker) + ')\n')
        self.assertNotEqual(subprocess.run(['./scripts/kube-capacity', str(path)], cwd=self.root, capture_output=True).returncode, 0)
        self.assertFalse(marker.exists())

    def test_stateless_micro_deploy_has_no_migration_dependency(self):
        with redirect_stdout(io.StringIO()):
            main(['create', 'micro-service', 'stateless-probe', '--module-name', 'example.org/stateless/probe',
                  '--proto-package', 'platform.stateless.v1', '--output-dir', str(self.base), '--non-interactive'])
        self.root = self.base / 'stateless-probe'
        (self.root / 'scripts/security').write_text('#!/bin/sh\nprintf "{}\\n"\n')
        (self.bundle / 'migration.yaml').unlink()
        self.seal()
        result, calls = self.release()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any('create' in call or 'wait' in call for call in calls))
        self.assertEqual(sum(self.mutating_apply(call) for call in calls), 1)

    def test_custom_ports_are_integers_and_drills_start_unverified(self):
        import yaml
        with redirect_stdout(io.StringIO()):
            main(['create', 'micro-service', 'port-probe', '--module-name', 'example.org/ports/probe',
                  '--proto-package', 'platform.ports.v2', '--http-port', '8181', '--grpc-port', '9191',
                  '--service-name', 'custom-rpc', '--output-dir', str(self.base), '--non-interactive'])
        root = self.base / 'port-probe/deploy/kubernetes'
        deployment = yaml.safe_load((root / 'base/deployment.yaml').read_text())
        service = yaml.safe_load((root / 'base/service.yaml').read_text())
        self.assertEqual(deployment['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort'], 9191)
        self.assertEqual(service['spec']['ports'][0]['port'], 9191)
        self.assertEqual(service['metadata']['name'], 'custom-rpc')
        report = json.loads((root / 'drill-report.json').read_text())
        self.assertEqual(report['status'], 'not-run')
        self.assertTrue(all(x['status'] == 'not-run' for x in report['scenarios']))

    def test_hpa_initial_single_replica_does_not_complete_release(self):
        result, calls = self.release(fault='replicas')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('rollout' in call for call in calls))
        self.assertFalse((self.bundle / 'deployed-context.txt').exists())
