# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

javascript-build is a GNU Make-based build system for JavaScript packages. This repo contains no
JavaScript package itself — the **products are `Makefile.base`, `eslint.config.js`, and
`jsdoc.json`**, which downstream projects' Makefiles download from
`https://craigahobbs.github.io/javascript-build/`. GitHub Pages serves these files directly from
the repo (hence `.nojekyll` and `index.html` at the root; `index.html` renders the README via
MarkdownUp). The root Makefile's `gh-pages` target is a deliberate no-op override.

Downstream Makefiles prefer copying from a local `../javascript-build` checkout over downloading
(see the `WGET` macro in README.md), so local edits here can be tested from a sibling project.

## Commands

- `make test` (or `make commit`) — run all tests
- `make test-<name>` — run a single test, e.g. `make test-commit` (names come from the
  `TEST_RULE` calls in `Makefile`)
- `make -j commit` — run tests in parallel
- `make changelog` — update CHANGELOG.md via simple-git-changelog (Python venv in `build/`)
- `make clean` — remove `build/` and `test-actual/`

## How Testing Works

Tests are dry-run snapshot comparisons — nothing is actually installed or executed:

1. Each `tests/<name>/Makefile` sets every version variable to a placeholder (`NODE_IMAGE := node:X`,
   `C8_VERSION := ~X.Y`, ...) and then does `include ../../Makefile.base`.
2. The `TEST_RULE` macro in the root `Makefile` runs `make -n <target>` in that directory,
   normalizes make's "Nothing to be done" lines with sed, and diffs the output against
   `test-expected/<name>.txt`.
3. `-2` test variants (e.g. `tests/commit-2/`) have a committed `build/npm.build` sentinel file so
   the dry-run exercises the incremental path (npm install already done).

Consequences:

- **Any change to a command in `Makefile.base` requires updating the matching
  `test-expected/*.txt` files** — including the `-2`, `-use-docker`, and `-use-podman` variants.
- Dependency version bumps (e.g. `ESLINT_VERSION`) do *not* change expected output, because test
  Makefiles override all versions with `~X.Y` placeholders. The maintenance pattern in git history
  is: bump versions in `Makefile.base`, then `make changelog` and update CHANGELOG.md.
- To add a test: create `tests/<name>/Makefile`, add `test-expected/<name>.txt`, and register it
  in the root `Makefile` with `$(eval $(call TEST_RULE, <name>, <target and vars>))`.
- The root `Makefile` un-exports `USE_DOCKER`/`USE_PODMAN` and forces `OS := Unknown` so the host
  environment can't leak into expected output; keep new tests host-independent the same way.
