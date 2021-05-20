# Licensed under the MIT License
# https://github.com/craigahobbs/javascript-build/blob/main/LICENSE

PYLINT_VERSION ?= 2.8.*

.PHONY: help
help:
	@echo 'usage: make [changelog|clean|commit|lint|test]'

.PHONY: commit
commit: test lint

.PHONY: clean
clean:
	rm -rf build __pycache__

.PHONY: test
test:
	python3 -m unittest -v tests.py

.PHONY: lint
lint: build/venv-lint.build
	build/venv-lint/bin/pylint tests.py

build/venv-lint.build:
	python3 -m venv build/venv-lint
	build/venv-lint/bin/pip install -U pip setuptools wheel pylint=="$(PYLINT_VERSION)"
	touch $@

.PHONY: changelog
changelog:
	make -f Makefile.base changelog NO_DOCKER=1
