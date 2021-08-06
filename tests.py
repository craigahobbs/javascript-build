# Licensed under the MIT License
# https://github.com/craigahobbs/javascript-build/blob/main/LICENSE

"""
JavaScript Build makefile unit tests
"""

# pylint: disable=line-too-long, missing-function-docstring

from contextlib import contextmanager
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest

# Read the base makefile
with open('Makefile.base', 'r') as file_makefile_base:
    MAKEFILE_BASE = file_makefile_base.read()


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


class JavaScriptBuildTest(unittest.TestCase):
    """
    JavaScript Build makefile unit tests
    """

    def assert_make_output(self, actual, expected):
        actual_clean = actual

        # Cleanup npm versions
        actual_clean = re.sub(r"@'[~|^]?\d+.*?'", "@'X.X.X'", actual_clean, flags=re.MULTILINE)

        # Cleanup make message for macOS
        actual_clean = re.sub(r'^(make: Nothing to be done for )`', r"\1'", actual_clean, flags=re.MULTILINE)

        # Cleanup leading tabs for macOS
        actual_clean = re.sub(r'^\t\t', r'\t', actual_clean, flags=re.MULTILINE)

        self.assertEqual(actual_clean, expected)

    def test_help(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
echo 'usage: make [changelog|clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )
            self.assert_make_output(
                subprocess.check_output(['make', 'help', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
echo 'usage: make [changelog|clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )

    def test_clean(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'clean', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build node_modules package-lock.json
'''
        )

    def test_superclean(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'superclean', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build node_modules package-lock.json
docker rmi -f node:16-slim python:3
'''
        )

    def test_commit(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'package.js'], ''),
            (['src', 'tests', 'test.js'], '')
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

    def test_commit_overrides(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
include Makefile.base

AVA_ARGS = --bogus-ava-arg
C8_ARGS = --bogus-c8-arg
ESLINT_ARGS = --bogus-eslint-arg
JSDOC_ARGS = --bogus-jsdoc-arg
'''
            ),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'package.js'], ''),
            (['src', 'tests', 'test.js'], '')
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v --bogus-ava-arg 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint --bogus-eslint-arg -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ --bogus-jsdoc-arg src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 --bogus-c8-arg \\
\tnpx ava -v --bogus-ava-arg 'src/tests/**/*.js'
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v --bogus-ava-arg 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint --bogus-eslint-arg -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ --bogus-jsdoc-arg src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 --bogus-c8-arg \\
\tnpx ava -v --bogus-ava-arg 'src/tests/**/*.js'
'''
            )

    def test_no_docker(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'package.js'], ''),
            (['src', 'tests', 'test.js'], '')
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', 'NO_DOCKER=1', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
npx ava -v 'src/tests/**/*.js'
npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', 'NO_DOCKER=1', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
npx ava -v 'src/tests/**/*.js'
npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

    def test_test(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'test', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'test', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
'''
            )

    def test_cover(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'cover', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'cover', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
'''
            )

    def test_lint(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'lint', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'lint', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
'''
            )

    def test_doc(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'package.js'], ''),
            (['src', 'tests', 'test.js'], '')
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'doc', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'doc', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
'''
            )

    def test_gh_pages(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'myPackage.js'], ''),
            (['src', 'tests', 'testMyPackage.js'], '')
        ])
        with test_files as test_dir:
            output = subprocess.check_output(['make', 'gh-pages', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8')
            output = re.sub(r'/tmp[^\s]+?\.gh-pages', '/tmp.gh-pages', output, flags=re.MULTILINE)
            self.assert_make_output(
                output,
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
if [ ! -d ../tmp.gh-pages ]; then git clone -b gh-pages `git config --get remote.origin.url` ../tmp.gh-pages; fi
cd ../tmp.gh-pages && git pull
rsync -rv --delete --exclude=.git/ build/doc/ ../tmp.gh-pages
touch ../tmp.gh-pages/.nojekyll
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            output = subprocess.check_output(['make', 'gh-pages', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8')
            output = re.sub(r'/tmp[^\s]+?\.gh-pages', '/tmp.gh-pages', output, flags=re.MULTILINE)
            self.assert_make_output(
                output,
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
if [ ! -d ../tmp.gh-pages ]; then git clone -b gh-pages `git config --get remote.origin.url` ../tmp.gh-pages; fi
cd ../tmp.gh-pages && git pull
rsync -rv --delete --exclude=.git/ build/doc/ ../tmp.gh-pages
touch ../tmp.gh-pages/.nojekyll
'''
            )

    def test_gh_pages_none(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
GHPAGES_SRC :=
include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'gh-pages', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
make: Nothing to be done for 'gh-pages'.
'''
            )

    def test_publish(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE),
            (['src', 'package', 'package.js'], ''),
            (['src', 'tests', 'test.js'], '')
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'publish', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q node:16-slim)" = "" ]; then docker pull -q node:16-slim; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm install --save-exact --save-dev \\
\tava@'X.X.X' \\
\tc8@'X.X.X' \\
\teslint@'X.X.X' \\
\tjsdoc@'X.X.X' \\
\twindow@'X.X.X'
mkdir -p build/
touch build/npm.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm login && docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm publish && docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm logout
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'npm.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'publish', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx eslint -c .eslintrc.cjs -f unix .eslintrc.cjs src/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx jsdoc --pedantic -d build/doc/ -c jsdoc.json README.md src/package/
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npx c8 --all --include 'src/**/*.js' --temp-dir build/tmp --report-dir build/coverage \\
\t--check-coverage --reporter html --reporter text --branches 100 --lines 100 \\
\tnpx ava -v 'src/tests/**/*.js'
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm login && docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm publish && docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` -e HOME=`pwd`/build node:16-slim npm logout
'''
            )

    def test_changelog(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'changelog', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q python:3)" = "" ]; then docker pull -q python:3; fi
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3 python3 -m venv build/venv-changelog
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3 build/venv-changelog/bin/pip install -U pip setuptools wheel simple-git-changelog
touch build/venv-changelog.build
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3 build/venv-changelog/bin/simple-git-changelog
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'venv-changelog.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'changelog', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -u`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3 build/venv-changelog/bin/simple-git-changelog
'''
            )

    def test_changelog_no_docker(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'changelog', 'NO_DOCKER=1', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
python3 -m venv build/venv-changelog
build/venv-changelog/bin/pip install -U pip setuptools wheel simple-git-changelog
touch build/venv-changelog.build
build/venv-changelog/bin/simple-git-changelog
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build'))
            Path(os.path.join(test_dir, 'build', 'venv-changelog.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'changelog', 'NO_DOCKER=1', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
build/venv-changelog/bin/simple-git-changelog
'''
            )
