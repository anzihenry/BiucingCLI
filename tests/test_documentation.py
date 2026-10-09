"""Exercise documentation-gate failures without editing repository documents."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationChecksTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        namespace = runpy.run_path(str(ROOT / 'scripts/check-docs'))
        self.main = namespace['main']
        self.main.__globals__['ROOT'] = self.root
        self.write('README.md', 'Project', '[English](README.en.md)\n[Docs](docs/README.md)')
        self.write('README.en.md', 'Project EN', '[中文](README.md)\n[Docs](docs/README.en.md)')
        self.write('CHANGELOG.md', 'Changes', '[English](CHANGELOG.en.md)\n[Docs](docs/README.md)')
        self.write('CHANGELOG.en.md', 'Changes EN', '[中文](CHANGELOG.md)\n[Docs](docs/README.en.md)')
        self.write('docs/README.md', 'Docs', '[English](README.en.md)\n[Project](../README.md)')
        self.write('docs/README.en.md', 'Docs EN', '[中文](README.md)\n[Project](../README.en.md)')
        self.inventory = self.root / 'docs/initiatives/process/documentation-standard/evidence/migration-inventory.json'
        self.inventory.parent.mkdir(parents=True)
        self.inventory.write_text(json.dumps({'files': []}))

    def write(self, path, title, body, status='current'):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f'---\ntitle: {json.dumps(title)}\nstatus: {status}\n'
                     f'owner: project-maintainers\nupdated: 2026-10-09\n---\n\n'
                     f'# {title}\n\n{body}\n')

    def check(self):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            code = self.main()
        return code, output.getvalue()

    def append(self, path, content):
        p = self.root / path
        p.write_text(p.read_text() + content)

    def test_valid_fixture_and_heading_references(self):
        self.append('README.md', '\n## Hello `World`\n\n[Heading](#hello-world)\n')
        self.append('docs/README.md', '\n[Root heading](../README.md#hello-world)\n'
                    '\n```md\n[Ignored example](does-not-exist.md)\n```\n')
        self.append('docs/README.en.md', '\n```md\n[Ignored example](does-not-exist.md)\n```\n')
        self.assertEqual(self.check()[0], 0, self.check()[1])

    def test_rejects_missing_file_and_heading_and_absolute_links(self):
        cases = [('missing.md', 'missing link target'),
                 ('#missing', 'missing heading anchor'),
                 ('/README.md', 'absolute repository link')]
        p = self.root / 'README.md'
        original = p.read_text()
        for href, expected in cases:
            with self.subTest(href=href):
                p.write_text(original + f'\n[Broken]({href})\n')
                code, output = self.check()
                self.assertEqual(code, 1)
                self.assertIn(expected, output)
        p.write_text(original)

    def test_rejects_invalid_metadata_and_language_mismatch(self):
        p = self.root / 'README.md'
        original = p.read_text()
        for before, after, expected in [('owner: project-maintainers', 'owner: unknown', 'unconfigured owner'),
                                        ('status: current', 'status: released', 'illegal status'),
                                        ('updated: 2026-10-09', 'updated: 2026-99-99', 'month must be'),
                                        ('status: current', 'status: draft', 'bilingual status mismatch')]:
            with self.subTest(after=after):
                p.write_text(original.replace(before, after))
                code, output = self.check()
                self.assertEqual(code, 1)
                self.assertIn(expected, output)
        p.write_text(original)

    def test_rejects_missing_translation_and_index_drift(self):
        self.append('docs/README.md', '\n| [Wrong title](../README.md) | draft |\n')
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('index title/status mismatch', output)
        (self.root / 'README.en.md').unlink()
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('missing bilingual', output)

    def test_rejects_old_paths_and_missing_migration_targets(self):
        self.inventory.write_text(json.dumps({'files': [
            {'source': 'docs/old.md', 'target': 'docs/new.md'}]}))
        self.append('README.md', '\nOld path: docs/old.md\n')
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('missing migration target', output)
        self.assertIn('stale repository path', output)

    def test_rejects_missing_prose_translation(self):
        self.write('docs/guide.md', 'Guide', '[Docs](README.md)')
        self.append('docs/README.md', '\n[Guide](guide.md)\n')
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('guide.md: missing bilingual counterpart', output)

    def test_rejects_translated_code_drift_and_updated_mismatch(self):
        self.append('README.md', '\n```bash\nmake verify\n```\n')
        self.append('README.en.md', '\n```bash\nmake release\n```\n')
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('bilingual code-block mismatch', output)
        p = self.root / 'README.en.md'
        p.write_text(p.read_text().replace('make release', 'make verify').replace(
            'updated: 2026-10-09', 'updated: 2026-10-08'))
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('bilingual updated mismatch', output)

    def test_rejects_an_isolated_navigation_cluster(self):
        self.write('docs/isolated/README.md', 'Isolated', '[English](README.en.md)')
        self.write('docs/isolated/README.en.md', 'Isolated EN', '[中文](README.md)')
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn('not reachable by a maintained-document link', output)
