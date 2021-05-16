# JavaScript Build

**JavaScript Build** is a lightweight GNU Make-based build system for best-practice JavaScript
package development. JavaScript Build performs the following functions:

- Use the [official Docker Node image](https://hub.docker.com/_/node) to run tests, etc.
- Run unit tests with [AVA](https://www.npmjs.com/package/ava)
- Determine unit test coverage using [c8](https://www.npmjs.com/package/c8)
- Perform static code analysis using [eslint](https://www.npmjs.com/package/eslint)
- Generate documentation using [jsdoc](https://www.npmjs.com/package/jsdoc)
- Publish application or documentation to [GitHub Pages](https://pages.github.com/)
- Publish the package to [npm](https://docs.npmjs.com/cli/v6/commands/npm-publish)


## Contents

- [Project Setup](#project-setup)
- [Make Targets](#make-targets)
- [Make Options](#make-options)
- [Make Variables](#make-variables)
- [Extending JavaScript Build](#extending-javascript-build)


## Project Setup

The basic structure of a JavaScript Build project is as follows:

```
.
|-- .gitignore
|-- Makefile
|-- README.md
`-- src
    |-- package-name
    |   |-- packageName.js
    `-- tests
        `-- testPackageName.js
```

The basic JavaScript Build "Makefile" is as follows:

``` make
# Download JavaSript Build
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell if which wget; then wget -q $(1); else curl -Os $(1); fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/javascript-build/main/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/javascript-build/main/jsdoc.json))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/javascript-build/main/package.json))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/javascript-build/main/.eslintrc.cjs))

# Include JavaScript Build
include Makefile.base

clean:
	rm -rf Makefile.base jsdoc.json package.json .eslintrc.cjs
```

Note that the makefile automatically downloads "Makefile.base", "jsdoc.json", "package.json", and
".eslintrc.cjs" from JavaScript Build. JavaScript Build continually updates its development
dependencies to the latest stable versions.


## Make Targets

JavaScript Build exposes build commands as "phony" make targets. Make targets are executed as follows:

```
make <target>
```

The following targets are available:

### commit

Execute the [test](#test), [lint](#lint), [doc](#doc), and [cover](#cover) targets. This target
should be run prior to any commit.

### test

Run the unit tests in the "src/tests" directory.

To run a single unit test, use the "TEST" make variable:

```
make test TEST='My Test'
```

### lint

Run eslint on JavaScript source files under the "src" directory.

### doc

Run jsdoc on JavaScript source files under the "src" directory. The HTML documentation index is
located at "build/doc/index.html".

### cover

Run unit tests with coverage. By default, "make cover" fails if coverage is less than 100%. The HTML
coverage report index is located at "build/coverage/index.html".

The "TEST" make variable is supported as described in the [test](#test) target above.

### clean

Delete all development artifacts.

### superclean

Delete all development artifacts and downloaded docker images.

### gh-pages

Publish the application or documentation to GitHub Pages. The `gh-pages` target depends on the
`commit` target. By default the "src" directory is published (excluding "tests").

The repository is git-cloned (or pulled) to the "../\<package-name>.gh-pages" directory, the
"gh-pages" branch is checked-out, and the "GHPAGES_SRC" make variable is rsync-ed there. Afterward,
review the changes, commit, and push to publish.

To create a "gh-pages" branch in your repository, enter the following shell commands:

```
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "initializing gh-pages branch"
git push origin gh-pages
```

### publish

Publish the package to npm.


## Make Options

To view the commands of any make target without executing, use the "-n" make argument:

```
make -n test
```

To run targets in parallel, use the "-j" make argument. This can significantly decrease the time of
the [commit](#commit) target.

```
make -j commit
```


## Make Variables

JavaScript Build exposes several make variables that can be modified in your makefile following the
base makefile include. For example, to publish the built documentation to GitHub Pages:

```
GHPAGES_SRC := build/doc/
```

The following variables are supported:

- `NODE_IMAGE` - The [node docker image](https://hub.docker.com/_/node/).

- `AVA_VERSION` - The [AVA](https://www.npmjs.com/package/ava) package version.

- `AVA_ARGS` - The AVA tool's command line arguments. Default is "".

- `C8_VERSION` - The [c8](https://www.npmjs.com/package/c8) package version.

- `C8_ARGS` - The c8 tool's command line arguments. Default is "".

- `ESLINT_VERSION` - The [eslint](https://www.npmjs.com/package/eslint) package version.

- `ESLINT_ARGS` - The eslint tool's command line arguments. Default is "".

- `JSDOC_VERSION` - The [jsdoc](https://www.npmjs.com/package/jsdoc) package version.

- `JSDOC_ARGS` - The jsdoc tool's command line arguments. Default is "-c jsdoc.json src".

- `WINDOW_VERSION` - The [window](https://www.npmjs.com/package/window) package version.

- `GHPAGES_SRC` - The gh-pages target's source directories and files. Directories must end with a
  slash ("/"). Default all directories in the "src" directory, excluding the "tests" directory.

- `NO_DOCKER` - Use the system node instead of docker. This is intended to be used from the command line:

```
make commit NO_DOCKER=1
```


## Extending JavaScript Build

All of the JavaScript Build [targets](#make-targets) may be extended either by adding additional
commands or adding a target dependency. Add additional commands to execute when a target (and all
its dependencies) is complete:

```
commit:
	@echo 'Build succeeded!'
```

Add a target dependency when you want the new dependency to execute in parallel (for [parallel
builds](#make-options)):

```
.PHONY: other-stuff
other-stuff:
    # do stuff...

commit: other-stuff
```
