# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE

"""
Python Build makefile unit tests
"""

# pylint: disable=line-too-long, missing-function-docstring

from contextlib import contextmanager
import os
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest


# Read the base makefile
with open('Makefile.base', 'r') as file_makefile_base:
    MAKEFILE_BASE = file_makefile_base.read()


# The default Python Build makefile
DEFAULT_MAKEFILE = '''\
include Makefile.base
'''


# Helper context manager to create a list of files in a temporary directory
@contextmanager
def create_test_files(file_defs):
    tempdir = TemporaryDirectory() # pylint: disable=consider-using-with
    try:
        for path_parts, content in file_defs:
            if isinstance(path_parts, str):
                path_parts = [path_parts]
            path = os.path.join(tempdir.name, *path_parts)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file_:
                file_.write(content)
        yield tempdir.name
    finally:
        tempdir.cleanup()


class PythonBuildTest(unittest.TestCase):
    """
    Python Build makefile unit tests
    """

    @staticmethod
    def check_output(args, cwd, env=None):
        if env is None:
            env = {'NO_DOCKER': ''}
        return subprocess.check_output(args, env=env, cwd=cwd, stderr=subprocess.STDOUT, encoding='utf-8')

    def assert_make_output(self, actual, expected):
        actual_clean = actual

        # Cleanup make message for macOS
        actual_clean = re.sub(r'^(make: Nothing to be done for )`', r"\1'", actual_clean, flags=re.MULTILINE)

        # Cleanup leading tabs for macOS
        actual_clean = re.sub(r'^\t\t', r'\t', actual_clean, flags=re.MULTILINE)

        self.assertEqual(actual_clean, expected)

    def test_help(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', '-n'], test_dir),
                '''\
echo 'usage: make [clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )
            self.assert_make_output(
                self.check_output(['make', 'help', '-n'], test_dir),
                '''\
echo 'usage: make [clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )

    def test_clean(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', 'clean', '-n'], test_dir),
                '''\
rm -rf build node_modules package-lock.json
'''
            )

    def test_superclean(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', 'superclean', '-n'], test_dir),
                '''\
rm -rf build node_modules package-lock.json
docker rmi -f node:16-slim
'''
            )
