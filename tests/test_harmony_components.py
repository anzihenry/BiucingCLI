"""HarmonyOS binary closure, DI rejection and shared source authority."""
import importlib.machinery
import importlib.util
import io
import json
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli_support import CLIHelpers


class HarmonyComponentsTests(CLIHelpers, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_cli(['create', 'harmonyos', 'demo', '--bundle-name', 'com.example.demo',
                      '--output-dir', self.tmp.name, '--non-interactive'])
        self.root = Path(self.tmp.name) / 'demo'
        self.api = self.load('components')
        self.api.REGISTRY = self.root / '.artifacts/components'
        self.environment = patch.dict(os.environ, {'CI': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for name in self.api.NAMES:
            self.artifact(name)

    def load(self, name):
        loader = importlib.machinery.SourceFileLoader('harmony_' + name, str(self.root / 'scripts' / name))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def artifact(self, name, version='0.1.0', parent=None, **options):
        api = self.api
        folder = (parent or api.REGISTRY) / name / version
        folder.mkdir(parents=True)
        deps = {n: '0.1.0' for n in api.DEPS[name]}
        metadata = {'name': '@biucing/' + name, 'version': version, 'metadata': {'byteCodeHar': True},
                    'dependencies': {'@biucing/' + n: v for n, v in deps.items()}}
        with tarfile.open(folder / (name + '.har'), 'w:gz') as archive:
            def add(path, data):
                member = tarfile.TarInfo('package/' + path)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            add('oh-package.json5', json.dumps(metadata).encode())
            add('ets/modules.abc', b'fixture bytecode')
            if options.get('source'):
                add('Index.ets', b'source implementation')
            if name == 'homefeature':
                add('resources/base/element/string.json', b'{}')
            if name == 'sharedcore':
                for abi, (machine, elf_class) in api.ABIS.items():
                    data = b'\x7fELF' + bytes([elf_class, 1]) + bytes(10) + b'\x03\x00' + machine.to_bytes(2, 'little')
                    add('libs/' + abi + '/libbiucing_shared.so', data)
                    symbol = folder / 'symbols' / abi / 'libbiucing_shared.so'
                    symbol.parent.mkdir(parents=True)
                    symbol.write_bytes(data)
            elif options.get('native'):
                add('libs/arm64-v8a/libcopy.so', b'copy')
        api.write(folder / 'manifest.json', {'schema': 1, 'name': name, 'version': version,
                  'dependencies': deps, 'toolchain': api.read(self.root / 'dependencies/toolchain.json'),
                  'sources': {}, 'files': api.inventory(folder)})
        return folder

    def test_resolve_rejects_artifact_and_locked_manifest_tamper(self):
        api = self.api
        api.lock()
        api.resolve()
        (api.RESOLVED / 'homefeature.har').write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            api.verify()
        folder = api.REGISTRY / 'contracts/0.1.0'
        manifest = api.read(folder / 'manifest.json')
        manifest['sources'] = {'changed': 'revision'}
        api.write(folder / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'Locked manifest'):
            api.resolve()

    def test_binary_missing_never_falls_back_to_source(self):
        api = self.api
        api.lock()
        (api.REGISTRY / 'sharedcore/0.1.0/sharedcore.har').unlink()
        with self.assertRaisesRegex(ValueError, 'checksum'):
            api.resolve()

    def test_independent_upgrade_and_immutable_publish(self):
        api = self.api
        self.artifact('homefeature', '0.1.1')
        declaration = api.read(api.DECLARATION)
        declaration['components']['homefeature'] = '0.1.1'
        api.write(api.DECLARATION, declaration)
        api.lock()
        api.resolve()
        self.assertEqual(api.read(api.LOCK)['components']['contracts']['version'], '0.1.0')
        with self.assertRaisesRegex(ValueError, 'Immutable'):
            api.publish('homefeature', '0.1.1')

    def test_overrides_rejected_by_ci_release_and_dependency_conflicts(self):
        api = self.api
        api.lock()
        folder = self.artifact('homefeature', parent=self.root / 'local')
        api.write(api.OVERRIDES, {'homefeature': str(folder)})
        api.resolve()
        with self.assertRaisesRegex(ValueError, 'forbids'):
            api.verify(release=True)
        with patch.dict(os.environ, {'CI': 'true'}), self.assertRaisesRegex(ValueError, 'forbids'):
            api.resolve()
        metadata = api.read(folder / 'manifest.json')
        metadata['dependencies']['contracts'] = '0.2.0'
        api.write(folder / 'manifest.json', metadata)
        with self.assertRaisesRegex(ValueError, 'dependency version'):
            api.resolve()

    def test_source_and_duplicate_native_are_rejected(self):
        api = self.api
        for option in ['source', 'native']:
            folder = self.artifact('homefeature', parent=self.root / option, **{option: True})
            with self.assertRaisesRegex(ValueError, 'source|owns native'):
                api.validate(folder, 'homefeature', '0.1.0')

    def test_toolchain_mismatch_is_rejected(self):
        api = self.api
        folder = api.REGISTRY / 'contracts/0.1.0'
        data = api.read(folder / 'manifest.json')
        data['toolchain']['sdk'] = 'different'
        api.write(folder / 'manifest.json', data)
        with self.assertRaisesRegex(ValueError, 'toolchain'):
            api.lock()

    def test_di_checks_hidden_graphs_separately_and_rejects_bad_bindings(self):
        api = self.load('di')
        for relative in api.GRAPHS:
            graph = json.loads((self.root / relative).read_text())
            self.assertIn('new ', api.generate(graph))
            graph['nodes'][0]['args'] = ['absent']
            with self.assertRaisesRegex(ValueError, 'Missing dependency'):
                api.generate(graph)
            graph['nodes'][0]['args'] = [graph['nodes'][0]['id']]
            with self.assertRaisesRegex(ValueError, 'cycle'):
                api.generate(graph)
        hvigor = (self.root / 'hvigorfile.ts').read_text()
        self.assertIn("'--scope', 'shell'", hvigor)
        self.assertNotIn('components/homefeature', hvigor)
        self.assertIn("getExtParam('buildMode')", hvigor)

    def test_installed_sdk_tamper_and_source_substitution_are_rejected(self):
        api = self.api
        api.lock()
        api.resolve()
        for name in api.NAMES:
            installed = self.root / 'entry/oh_modules/@biucing' / name
            store = self.root / 'store' / name / '@biucing' / name
            store.mkdir(parents=True)
            installed.parent.mkdir(parents=True, exist_ok=True)
            installed.symlink_to(store, target_is_directory=True)
            for dep in api.DEPS[name]:
                (store.parent / dep).symlink_to(self.root / 'entry/oh_modules/@biucing' / dep,
                                              target_is_directory=True)
            with tarfile.open(api.RESOLVED / (name + '.har')) as archive:
                for member in archive.getmembers():
                    if member.isfile():
                        output = installed / Path(*Path(member.name).parts[1:])
                        output.parent.mkdir(parents=True, exist_ok=True)
                        output.write_bytes(archive.extractfile(member).read())
        api.verify_installed()
        target = self.root / 'entry/oh_modules/@biucing/homefeature/ets/modules.abc'
        target.write_bytes(b'changed after installation')
        with self.assertRaisesRegex(ValueError, 'Installed SDK differs'):
            api.verify_installed()
        manifest = api.read(self.root / 'entry/oh-package.json5')
        manifest['dependencies']['@biucing/homefeature'] = 'file:../components/homefeature'
        api.write(self.root / 'entry/oh-package.json5', manifest)
        with self.assertRaisesRegex(ValueError, 'locked HARs only'):
            api.verify_installed()

    def test_declared_devices_do_not_claim_unavailable_native_architectures(self):
        profile = json.loads((self.root / 'entry/src/main/module.json5').read_text())
        self.assertEqual(set(profile['module']['deviceTypes']),
                         {'phone', 'tablet', '2in1', 'wearable', 'tv'})
        native = json.loads((self.root / 'components/sharedcore/build-profile.json5').read_text())
        self.assertEqual(set(native['buildOption']['externalNativeOptions']['abiFilters']),
                         set(self.api.ABIS))

    def test_portable_core_has_one_authority(self):
        source = Path(__file__).resolve().parents[1] / 'shared/core'
        for item in source.rglob('*'):
            if item.is_file() and (item.relative_to(source).parts[0] in ('Sources', 'Tests') or item.name == 'CMakeLists.txt'):
                self.assertEqual(item.read_bytes(), (self.root / 'shared/core' / item.relative_to(source)).read_bytes())
