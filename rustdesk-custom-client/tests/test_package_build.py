import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_build', KIT / 'scripts/package-build.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def test_native_outputs_and_checksums(self):
        for platform, arch, binary in [
            ('windows', 'x86_64', 'SignOutput/rustdesk-1.5.1-x86_64.exe'),
            ('macos', 'aarch64', 'rustdesk-1.5.1-aarch64.pkg'),
            ('macos', 'x86_64', 'rustdesk-1.5.1-x86_64.pkg'),
            ('linux', 'x86_64', 'rustdesk-1.5.1-x86_64.deb'),
        ]:
            with self.subTest(platform=platform, arch=arch), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                source = root / binary
                source.parent.mkdir(exist_ok=True)
                source.write_bytes(b'test native build output')
                (root / 'LICENCE').write_text('AGPL fixture')
                out = module.package(platform, arch, 'pinned-commit', root, KIT)
                if platform == 'windows':
                    self.assertTrue((out / 'UnityAVSupport-Windows-Install.exe').is_file())
                checks = (out / 'SHA256SUMS').read_text().splitlines()
                self.assertEqual(len(checks), 5)
                for check in checks:
                    digest, name = check.split('  ', 1)
                    self.assertEqual(digest, hashlib.sha256((out / name).read_bytes()).hexdigest())

    def test_missing_or_ambiguous_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                module.package('linux', 'x86_64', 'commit', root, KIT)
            for version in ('1.5.1', '1.5.2'):
                (root / f'rustdesk-{version}-x86_64.deb').write_bytes(b'build')
            with self.assertRaises(ValueError):
                module.package('linux', 'x86_64', 'commit', root, KIT)
            self.assertFalse((root / 'unity-dist').exists())


if __name__ == '__main__':
    unittest.main()
