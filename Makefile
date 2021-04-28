# Licensed under the MIT License
# https://github.com/craigahobbs/javascript-build/blob/main/LICENSE

BUILD := build
PYLINT_VERSION ?= 2.8.2

.PHONY: help
help:
	@echo 'usage: make [clean|commit|lint|test]'

.PHONY: commit
commit: test lint

.PHONY: clean
clean:
	rm -rf $(BUILD) __pycache__

.PHONY: test
test:
	python3 -m unittest -v tests.py

.PHONY: lint
lint: $(BUILD)/venv-lint.build
	$(BUILD)/venv-lint/bin/pylint tests.py

$(BUILD)/venv-lint.build:
	python3 -m venv $(BUILD)/venv-lint
	$(BUILD)/venv-lint/bin/pip install -U pip setuptools wheel pylint==$(PYLINT_VERSION)
	touch $@
