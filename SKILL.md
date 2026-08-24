---
name: javascript-build
description: >
  Develop a downstream javascript-build package (Makefile includes Makefile.base).
  Use when running make test, lint, cover, or commit; adding tests; or changing
  that Makefile. Do not use when editing the javascript-build repository itself.
---

# javascript-build (downstream)

This skill is the build workflow for **packages that include** javascript-build. Package-specific behavior stays in the consumer `AGENTS.md`. Human reference for every target and variable is `README.md` in the same directory as this skill. Do not use this skill when changing `Makefile.base` itself — that is javascript-build's `AGENTS.md`.

Load this file from `../javascript-build/SKILL.md` if that file exists, otherwise from [https://raw.githubusercontent.com/craigahobbs/javascript-build/main/SKILL.md](https://raw.githubusercontent.com/craigahobbs/javascript-build/main/SKILL.md). If neither is available, `make help` and the consumer `Makefile` are enough for day-to-day work; do not invent a second toolchain.

## Identify

The consumer `Makefile` downloads `Makefile.base`, `eslint.config.js`, and `jsdoc.json` on first run, copies from `../javascript-build` when that tree exists, and `include`s the downloaded makefile. Those downloads are gitignored; `make clean` deletes them. Do not commit or hand-edit them. Do not rewrite the WGET stub.

Layout: sources in `lib/`, tests in `test/`, metadata in `package.json`.

## Commands

Run from the consumer repo root. `make` installs c8, eslint, jsdoc (and jsdom if `USE_JSDOM` is set) via `npm install --save-dev` and records `build/npm.build`. Extra packages belong in `package.json`, not a one-off `npm install`.

| Target | Purpose |
| --- | --- |
| `make test` | `node --test` on `test/` |
| `make lint` | eslint on `eslint.config.js`, `lib/`, and `test/` |
| `make cover` | c8 coverage; **fails under 100%** unless the Makefile overrides `C8_ARGS` |
| `make commit` | `test` + `lint` + `doc` + `cover` — the quality gate |
| `make clean` | `build/`, `node_modules/`, `package-lock.json` (consumer stubs also remove the downloads) |
| `make superclean` | `clean` plus pulled container images |

One test (also works with `make cover`):

```
make test TEST='My Test'
```

`TEST=` is passed to `node --test --test-name-pattern`. It is a name pattern, not a file path.

`make -n <target>` prints the commands without running them. `make -j commit` is supported.

Default `make` uses the system Node. Containers: `make commit USE_DOCKER=1` or `USE_PODMAN=1` (`NODE_IMAGE`).

HTML coverage: `build/coverage/index.html`.

Extended recipes that need `node_modules` should depend on `build/npm.build` and prefix commands with `$(NODE_SHELL)` so they work under Docker/podman.

### Only when asked

- `make changelog` — rewrites `CHANGELOG.md` from git
- `make publish` — npm (depends on `commit`)
- `make gh-pages` — rsync `GHPAGES_SRC` to `../<repo>.gh-pages`

Version for packages is `version` in `package.json`. Bump it only as part of a release.

## Local overrides

After this skill, read the consumer `Makefile` and `AGENTS.md`. Common knobs (full catalog in the README):

- `USE_JSDOM` — add jsdom as a development dependency
- `ESLINT_ARGS` — eslint paths (default `lib/ test/`; often appended after include)
- `C8_ARGS` — c8 flags (default includes `--100`)
- `GHPAGES_SRC` — must be set **before** `include Makefile.base`
- `NODE_IMAGE` — container image for `USE_DOCKER` / `USE_PODMAN`

Do not lower the coverage gate, skip `cover`, or leave untested branches. `/* c8 ignore */` only for version/platform-dependent code the consumer already uses that way.

## Do not

- Add jest, mocha, vitest, ava, prettier, or another task runner
- Switch the Makefile from npm to yarn or pnpm
- Add TypeScript, CI configs, or Makefile-stub rewrites unless asked
- Treat downloaded `Makefile.base` / `eslint.config.js` / `jsdoc.json` as project source
