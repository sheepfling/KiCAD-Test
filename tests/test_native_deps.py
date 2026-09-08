"""Cross-platform CI bootstrap must use the container's Python ABI."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.native_deps import prepare


class NativeDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.image = 'example.invalid/kicad@sha256:' + 'a' * 64

    def test_installs_linux_wheels_for_the_observed_container_abi(self) -> None:
        with patch('tools.native_deps.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout='3.13\n')
            prepare(self.root, self.image, Path('build/deps'))
        probe, install = (call.args[0] for call in run.call_args_list)
        self.assertIn('linux/amd64', probe)
        self.assertIn('python3', probe)
        self.assertNotIn('pip', probe)
        self.assertIn('manylinux2014_x86_64', install)
        self.assertIn('cp313', install)
        self.assertIn('--only-binary=:all:', install)
        self.assertEqual(install[-1], '.')

    def test_rejects_unknown_runtime_and_never_reuses_output(self) -> None:
        with patch('tools.native_deps.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout='unexpected\n')
            with self.assertRaisesRegex(ValueError, 'Unexpected container'):
                prepare(self.root, self.image, Path('build/deps'))
            self.assertEqual(run.call_count, 1)
        (self.root/'build/deps').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            prepare(self.root, self.image, Path('build/deps'))
        with self.assertRaisesRegex(ValueError, 'ignored build'):
            prepare(self.root, self.image, Path('projects/deps'))

    def test_missing_wheels_fail_the_setup_instead_of_running_an_incomplete_lane(self) -> None:
        with patch('tools.native_deps.subprocess.run') as run:
            run.side_effect = [subprocess.CompletedProcess([], 0, stdout='3.13\n'),
                               subprocess.CalledProcessError(1, ['pip'])]
            with self.assertRaises(subprocess.CalledProcessError):
                prepare(self.root, self.image, Path('build/deps'))


if __name__ == '__main__':
    unittest.main()
