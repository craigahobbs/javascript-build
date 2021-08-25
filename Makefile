# Licensed under the MIT License
# https://github.com/craigahobbs/javascript-build/blob/main/LICENSE


.PHONY: help
help:
	@echo 'usage: make [changelog|clean|commit|superclean|test]'


.PHONY: commit
commit: test


.PHONY: clean
clean:
	rm -rf build/ test-actual/


.PHONY: superclean
superclean: clean


.PHONY: test
test:
	rm -rf test-actual/
	@echo Tests completed - all passed


# Test rule function - name, make args
define TEST_RULE
.PHONY: test-$(strip $(1))
test-$(strip $(1)):
	@echo 'Testing "$(strip $(1))"...'
	mkdir -p test-actual/
	($(MAKE) -C tests/$(strip $(1))/ -n --no-print-directory$(if $(strip $(2)), $(strip $(2)))) \
		| sed -E "s/^(make\[)[0-9]+(\].*: Nothing to be done for )[\`']/\1X\2'/" \
		> test-actual/$(strip $(1)).txt
	diff test-actual/$(strip $(1)).txt test-expected/$(strip $(1)).txt
	rm test-actual/$(strip $(1)).txt

test: test-$(strip $(1))
endef


# Un-export base makefile variables
unexport NO_DOCKER


# Tests
$(eval $(call TEST_RULE, changelog, changelog))
$(eval $(call TEST_RULE, changelog-2, changelog))
$(eval $(call TEST_RULE, changelog-no-docker, changelog))
$(eval $(call TEST_RULE, clean, clean))
$(eval $(call TEST_RULE, commit, commit))
$(eval $(call TEST_RULE, commit-2, commit))
$(eval $(call TEST_RULE, cover, cover))
$(eval $(call TEST_RULE, cover-2, cover))
$(eval $(call TEST_RULE, doc, doc))
$(eval $(call TEST_RULE, doc-2, doc))
$(eval $(call TEST_RULE, gh-pages, gh-pages))
$(eval $(call TEST_RULE, gh-pages-2, gh-pages))
$(eval $(call TEST_RULE, help))
$(eval $(call TEST_RULE, lint, lint))
$(eval $(call TEST_RULE, lint-2, lint))
$(eval $(call TEST_RULE, publish, publish))
$(eval $(call TEST_RULE, publish-2, publish))
$(eval $(call TEST_RULE, superclean, superclean))
$(eval $(call TEST_RULE, test, test))
$(eval $(call TEST_RULE, test-2, test))
$(eval $(call TEST_RULE, test-no-docker, test NO_DOCKER=1))
$(eval $(call TEST_RULE, test-no-docker-2, test NO_DOCKER=1))


.PHONY: changelog
changelog: build/venv.build
	build/venv/bin/simple-git-changelog


build/venv.build:
	python3 -m venv build/venv
	build/venv/bin/pip -q install --progress-bar off -U pip setuptools
	build/venv/bin/pip -q install --progress-bar off simple-git-changelog
	touch $@
