import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sign_macos', Path(__file__).parents[1] / 'scripts/sign-macos.py')
signing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signing)


class NotarizationStateTests(unittest.TestCase):
    def fixture(self, root):
        candidate = root / 'signed.pkg'
        candidate.write_bytes(b'signed-package-fixture')
        output = root / 'release.pkg'
        state = root / 'submission.json'
        state.write_text(json.dumps({'submission_id': 'test-submission', 'notary_profile': 'test-profile',
                                     'signed_candidate': str(candidate), 'final_output': str(output),
                                     'release_ready': False}))
        return candidate, output, state

    def test_pending_preserves_candidate_without_publishing(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate, output, state = self.fixture(Path(temp))
            with patch.object(signing, 'json_command', return_value={'status': 'In Progress'}), patch.object(signing, 'run') as run:
                self.assertEqual(signing.complete(state), 2)
                run.assert_not_called()
            self.assertTrue(candidate.exists())
            self.assertFalse(output.exists())
            self.assertFalse(json.loads(state.read_text())['release_ready'])

    def test_gatekeeper_failure_prevents_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate, output, state = self.fixture(Path(temp))
            def fail_gatekeeper(*args):
                if args[0] == 'spctl':
                    raise subprocess.CalledProcessError(1, args)
            with patch.object(signing, 'json_command', return_value={'status': 'Accepted'}), patch.object(signing, 'run', side_effect=fail_gatekeeper):
                with self.assertRaises(subprocess.CalledProcessError):
                    signing.complete(state)
            self.assertTrue(candidate.exists())
            self.assertFalse(output.exists())
            self.assertFalse(json.loads(state.read_text())['release_ready'])

    def test_accepted_and_verified_package_is_published(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate, output, state = self.fixture(Path(temp))
            with patch.object(signing, 'json_command', return_value={'status': 'Accepted'}), patch.object(signing, 'run'):
                self.assertEqual(signing.complete(state), 0)
            self.assertEqual(output.read_bytes(), candidate.read_bytes())
            self.assertTrue(json.loads(state.read_text())['release_ready'])
