"""Android binary closure integrity and portable source authority."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from cli_support import CLIHelpers

ROOT = Path(__file__).resolve().parents[1]


class AndroidComponentsTests(CLIHelpers, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_cli(['create', 'android', 'demo', '--package-name', 'com.example.demo',
                      '--output-dir', self.tmp.name, '--non-interactive'])
        self.root = Path(self.tmp.name) / 'demo'
        loader = importlib.machinery.SourceFileLoader('android_components', str(self.root / 'scripts/components'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.api = importlib.util.module_from_spec(spec)
        loader.exec_module(self.api)
        self.api.REGISTRY = self.root / '.artifacts/maven'
        self.environment = patch.dict(os.environ, {'CI': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        for name in self.api.NAMES:
            self.artifact(name)

    def artifact(self, name, version='0.1.0', dependency_version='0.1.0', parent=None):
        api = self.api
        folder = (parent or api.REGISTRY) / api.GROUP_PATH / name / version
        folder.mkdir(parents=True)
        with zipfile.ZipFile(folder / f'{name}-{version}.aar', 'w') as archive:
            archive.writestr('classes.jar', b'fixture')
            if name in ('home', 'wearhome', 'tvhome'):
                archive.writestr('res/values/strings.xml', '<resources/>')
            if name == 'sharedcore':
                for abi, machine, elf_class in [('armeabi-v7a', 40, 1), ('arm64-v8a', 183, 2), ('x86_64', 62, 2)]:
                    data = b'\x7fELF' + bytes([elf_class, 1]) + bytes(10) + b'\x03\x00' + machine.to_bytes(2, 'little')
                    archive.writestr(f'jni/{abi}/libbiucing_shared.so', data)
                    symbol = folder / 'symbols' / abi / 'libbiucing_shared.so'
                    symbol.parent.mkdir(parents=True)
                    symbol.write_bytes(data)
        deps = {dep: dependency_version for dep in api.DEPS[name]}
        pom_deps = ''.join(f'<dependency><groupId>{api.GROUP}</groupId><artifactId>{dep}</artifactId><version>{v}</version></dependency>' for dep, v in deps.items())
        (folder / f'{name}-{version}.pom').write_text(f'<project xmlns="http://maven.apache.org/POM/4.0.0"><dependencies>{pom_deps}</dependencies></project>')
        (folder / f'{name}-{version}.module').write_text('{}')
        (folder / f'{name}-{version}-sources.jar').write_bytes(b'fixture')
        api.write(folder / 'manifest.json', {'schema': 1, 'group': api.GROUP, 'name': name,
                  'version': version, 'dependencies': deps, 'minSdk': '26', 'abis': list(api.ABIS),
                  'files': api.inventory(folder)})
        return folder

    def test_lock_resolve_and_tamper_rejection(self):
        api = self.api
        api.lock()
        api.resolve()
        api.verify()
        folder = api.RESOLVED / 'maven' / api.GROUP_PATH / 'home/0.1.0'
        (folder / 'home-0.1.0.aar').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'checksum'):
            api.verify()

    def test_replacing_manifest_and_checksums_cannot_replace_locked_sdk(self):
        api = self.api
        api.lock()
        folder = api.REGISTRY / api.GROUP_PATH / 'model/0.1.0'
        (folder / 'model-0.1.0-sources.jar').write_bytes(b'changed')
        manifest = api.read(folder / 'manifest.json')
        manifest['files'] = api.inventory(folder)
        api.write(folder / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'Locked manifest'):
            api.resolve()

    def test_overrides_require_matching_dependencies_and_never_enter_ci_release(self):
        api = self.api
        api.lock()
        override = self.artifact('home', parent=self.root / 'local')
        api.write(api.OVERRIDES, {'home': str(override)})
        api.resolve()
        api.verify()
        with self.assertRaisesRegex(ValueError, 'forbids'):
            api.verify(release=True)
        with patch.dict(os.environ, {'CI': 'true'}), self.assertRaisesRegex(ValueError, 'forbids'):
            api.resolve()
        manifest = api.read(override / 'manifest.json')
        manifest['dependencies']['homestate'] = '0.2.0'
        api.write(override / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'POM'):
            api.resolve()

    def test_independent_upgrade_and_no_source_fallback(self):
        api = self.api
        api.lock()
        self.artifact('home', '0.1.1')
        declaration = api.read(api.DECLARATION)
        declaration['components']['home'] = '0.1.1'
        api.write(api.DECLARATION, declaration)
        with self.assertRaisesRegex(ValueError, 'Declaration'):
            api.resolve()
        api.lock()
        api.resolve()
        self.assertEqual(api.read(api.LOCK)['components']['model']['version'], '0.1.0')
        api.LOCK.unlink()
        with self.assertRaises(FileNotFoundError):
            api.resolve()
        settings = (self.root / 'settings.gradle.kts').read_text()
        self.assertNotIn('include(":core:', settings)
        self.assertNotIn('include(":feature:', settings)
        self.assertNotIn('implementation(project(', (self.root / 'app/build.gradle.kts').read_text())

    def test_native_ownership_and_immutable_publication(self):
        api = self.api
        with self.assertRaisesRegex(ValueError, 'already exists'):
            api.build('home', '0.1.0')
        folder = api.REGISTRY / api.GROUP_PATH / 'model/0.1.0'
        with zipfile.ZipFile(folder / 'model-0.1.0.aar', 'a') as archive:
            archive.writestr('jni/arm64-v8a/libduplicate.so', b'native')
        manifest = api.read(folder / 'manifest.json')
        manifest['files'] = api.inventory(folder)
        api.write(folder / 'manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'native ownership'):
            api.lock()

    def test_apple_android_portable_core_have_one_authority(self):
        subprocess.run(['python3', str(ROOT / 'scripts/sync-shared-core'), '--check'], check=True)
        apple = ROOT / 'src/biucingcli/template_data/apple/template/Shared/Core/Sources/CoreNative'
        android = self.root / 'shared/core/Sources/CoreNative'
        for path in apple.rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (android / path.relative_to(apple)).read_bytes())

    def test_device_shells_share_binary_state_but_keep_native_ui(self):
        import xml.etree.ElementTree as ET
        android = '{http://schemas.android.com/apk/res/android}'
        for module, feature, suffix in [('app', 'home', ''), ('wear', 'wearhome', '.wear'), ('tv', 'tvhome', '.tv')]:
            build = (self.root / module / 'build.gradle.kts').read_text()
            self.assertIn(f'applicationId = "com.example.demo{suffix}"', build)
            self.assertIn(f'components:{feature}:', build)
            self.assertIn('components:homestate:', build)
            self.assertIn('components:sharedcore:', build)
            self.assertIn('../composition/src/main/java', build)
            self.assertNotIn('implementation(project(', build)
            if module != 'app':
                self.assertNotIn('components:home:', build)
                self.assertNotIn('libs.androidx.compose.material3', build)
            manifest = ET.parse(self.root / module / 'src/main/AndroidManifest.xml').getroot()
            if module == 'wear':
                self.assertTrue(any(n.get(android + 'name') == 'android.hardware.type.watch' for n in manifest.findall('uses-feature')))
                self.assertTrue(any(n.get(android + 'name') == 'com.google.android.wearable.standalone' and n.get(android + 'value') == 'true' for n in manifest.findall('application/meta-data')))
            if module == 'tv':
                self.assertTrue(any(n.get(android + 'name') == 'android.intent.category.LEANBACK_LAUNCHER' for n in manifest.findall('application/activity/intent-filter/category')))
        self.assertEqual(self.api.DEPS['home'], ['homestate', 'designsystem'])
        self.assertIn('armeabi-v7a', self.api.ABIS)
        for platform, module in [('mobile', 'app'), ('wear', 'wear'), ('tv', 'tv')]:
            result = subprocess.run(['make', '-n', 'build', f'PLATFORM={platform}'], cwd=self.root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f':{module}:assembleDebug', result.stdout)
        result = subprocess.run(['make', '-n', 'build', 'PLATFORM=invalid'], cwd=self.root, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for script in ['artifact-info', 'verify-release-artifact']:
            result = subprocess.run(['bash', f'scripts/{script}'], cwd=self.root, env={**os.environ, 'PLATFORM': 'invalid'}, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('PLATFORM must be', result.stderr)
