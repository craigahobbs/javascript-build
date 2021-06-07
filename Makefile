# Licensed under the MIT License
# https://github.com/craigahobbs/javascript-build/blob/main/LICENSE

# Download Python Build's pylintrc (for unit test static analysis)
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell if which wget; then wget -q $(1); else curl -Os $(1); fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/pylintrc))

PYLINT_VERSION ?= 2.8.*

.PHONY: help
help:
	@echo 'usage: make [changelog|clean|commit|lint|superclean|test]'

.PHONY: commit
commit: test lint

.PHONY: clean
clean:
	rm -rf build pylintrc __pycache__

.PHONY: superclean
superclean: clean

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
