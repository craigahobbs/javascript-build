# CLAUDE.md

Notes for coding agents working **in this repository**. Downstream packages that *include* javascript-build should follow [SKILL.md](SKILL.md), not this file.

javascript-build is a GNU Make build system. The makefiles and shared configs *are* the product — there is no JavaScript package here. This repo's own `Makefile` is a snapshot-test harness; it does not `include Makefile.base`.

## Deliverables

| File | Role |
| --- | --- |
| `Makefile.base` | Build system consumers `include`. Targets: `help`, `test`, `lint`, `doc`, `cover`, `commit`, `publish`, `changelog`, `gh-pages`, `clean`, `superclean` |
| `eslint.config.js` | Shared ESLint config (no snapshot tests; consumers re-download it) |
| `jsdoc.json` | Shared JSDoc config (no snapshot tests; consumers re-download it) |
| `SKILL.md` | Agent playbook for **downstream** packages |
| `README.md` | Human reference for targets and variables |

Consumer stubs wget `Makefile.base` / `eslint.config.js` / `jsdoc.json` from GitHub Pages, or copy them from `../javascript-build` when that tree exists. Downstream agents load `SKILL.md` from `../javascript-build/SKILL.md` if that file exists, otherwise from `https://raw.githubusercontent.com/craigahobbs/javascript-build/main/SKILL.md`. This repo's `make gh-pages` is a no-op; GitHub Pages serves these files from the repo root. Do not assume a make target publishes Pages.

`index.html` is a MarkdownUp shell for the README. Leave it unless the user asks.

## Commands

| Target | Purpose |
| --- | --- |
| `make test` | Run every snapshot fixture |
| `make test-<name>` | One fixture (`tests/<name>/`, e.g. `make test-commit`) |
| `make commit` | `test` only |
| `make clean` | `build/` and `test-actual/` |
| `make changelog` | Rewrite `CHANGELOG.md` via a local simple-git-changelog venv |

Do not run `make changelog` unless asked. There is no `cover` / `lint` / `publish` in *this* Makefile.

## Tests

Snapshots of `make -n` (dry-run command text), not of execution.

1. Fixture `tests/<name>/Makefile` sets placeholder versions (`NODE_IMAGE := node:X`, `C8_VERSION := ~X.Y`, ...) and `include ../../Makefile.base`.
2. `TEST_RULE` in the top-level Makefile runs `make -C tests/<name>/ -n --no-print-directory …`, rewrites `make[N]` → `make[X]` and the opening backtick → `'` in "Nothing to be done" lines (so output matches GNU Make 3.81 and 4.x), and diffs `test-actual/<name>.txt` against `test-expected/<name>.txt`. `make test` stops at the first diff; use `make -k test` to see every failure.
3. Checked-in empty markers skip install recipes in the dry run:
   - `build/npm.build` — npm install already done
   - `build/venv-changelog.build` — changelog venv already created
4. `-2` fixtures pair with the unmarked fixture. For host tests, unmarked shows install (`tests/commit/`) and `-2` has the marker (`tests/commit-2/`). For `USE_DOCKER` / `USE_PODMAN`, unmarked has the marker and `-2` shows image pull plus install. Fixtures without a `-2` (changelog, clean, help, superclean, test-use-jsdom) carry no marker.
5. On failure, `test-actual/<name>.txt` is left in place. If the change is intentional, copy it to `test-expected/<name>.txt` in the same commit. Never commit `test-actual/`.
6. To add a test: fixture Makefile (+ markers as needed), `$(eval $(call TEST_RULE, <name>, <goal and vars>))` in the top-level Makefile, and `test-expected/<name>.txt`.
7. The top-level Makefile sets `OS := Unknown` (a guard; `Makefile.base` has no OS-specific code today) and unexports `USE_DOCKER` / `USE_PODMAN` so environment values don't leak into fixtures. Do not remove that. Never pass `USE_DOCKER=` / `USE_PODMAN=` on the `make test` command line — command-line variables reach the sub-make and break every host fixture. This repo's own `make changelog` uses `build/venv/` and `VENV_BIN` (`bin` vs `Scripts`); do not delete that Windows branch as unused.

Fixtures set `NODE_IMAGE := node:X`, and fixtures that run npm install also set the `*_VERSION` pins to `~X.Y`. Changing the default `NODE_IMAGE` or pinned versions in `Makefile.base` does not update snapshots; it still needs a README update when user-facing. `PYTHON_IMAGE` is **not** overridden — changing its default changes the `changelog-use-{docker,podman}` snapshots.

`test-use-jsdom` is the pass-through for `USE_JSDOM`. New variables that appear in recipes should show up in a snapshot that prints them. Currently unsnapshotted: `TEST=`, `superclean` under docker/podman, and `GHPAGES_SRC` / `*_ARGS` overrides — add a fixture if you change those paths.

## `Makefile.base`

- System Node by default. `USE_DOCKER=1` / `USE_PODMAN=1` sets `NODE_SHELL` (and `PYTHON_SHELL` for changelog) to `docker run` / `podman run`.
- `build/npm.build` is the npm install marker. Recipes that need `node_modules` depend on it.
- `commit` is `test` + `lint` + `doc` + `cover`. `publish` and `gh-pages` depend on `commit` so parallel `make -j publish` cannot upload before tests finish. Do not drop that.
- Each public target is `x: _x` with the recipe on `_x`, so consumers can extend `x`. Keep that for new targets, and add them to the `_help` usage string (snapshotted in `help.txt`).
- `GHPAGES_SRC` is read at include time (`ifneq`); empty disables the `gh-pages` target. `NODE_SHELL` / `PYTHON_SHELL` are `:=`, so `NODE_IMAGE` / `PYTHON_IMAGE` reach `docker run` only if set before the `include`. Fixtures always set variables before `include`, so snapshots won't catch expansion-timing changes.
- `USE_JSDOM` appends jsdom to the npm install line.
- Pinned versions (`C8_VERSION`, `ESLINT_VERSION`, …) sit near the top of `Makefile.base`. Test fixtures override them, so bumps do not change snapshots.
- `NODE_TEST_ARGS` embeds a `node -e` that selects `test/` vs `test/**/*.js` by Node version. Changing that string updates snapshots.
- Recipe bodies: `$(NODE_SHELL)` is empty on the host and a container prefix otherwise. Keep commands written as `$(NODE_SHELL) node …` / `$(NODE_SHELL) npx …`.

GNU Make (`makefile-gmake`). Keep the MIT license header.

## Docs

| Change | Also update |
| --- | --- |
| User-facing target, variable, or stub Makefile | `README.md` and the matching snapshot(s) |
| Downstream agent workflow (`make test`, `TEST=`, coverage gate, `USE_JSDOM`, …) | `SKILL.md` |
| Snapshot command text | `test-expected/<name>.txt` (same commit) |

Do not copy the README variable catalog into `SKILL.md` or this file.

## Do not

- Apply [SKILL.md](SKILL.md) here (`make cover`, jest bans, `lib/` / `test/` layout). That skill is for consumers.
- Add a JavaScript package, jest, or a second test runner.
- Rewrite consumer WGET stubs in the README unless the download contract changes.
- Hand-edit `CHANGELOG.md`; use `make changelog` when asked.
