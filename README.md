# javascript-build

**javascript-build** is a lightweight GNU Make-based build system for best-practice JavaScript
package development.

- Uses the system Node or the official Node container image
- Run unit tests with [node --test](https://nodejs.org/api/test.html)
- Code coverage using [c8](https://www.npmjs.com/package/c8)
  - 100% code coverage enforced (configurable)
- Static code analysis using [eslint](https://www.npmjs.com/package/eslint)
- Package documentation using [jsdoc](https://www.npmjs.com/package/jsdoc)
- Publish the package to [npm](https://www.npmjs.com/)
- Publish application or documentation to [GitHub Pages](https://pages.github.com/)


## Contents

- [Project Setup](#project-setup)
- [Make Targets](#make-targets)
- [Make Options](#make-options)
- [Make Variables](#make-variables)
- [Extending javascript-build](#extending-javascript-build)
- [Make Tips and Tricks](#make-tips-and-tricks)


## Project Setup

The basic structure of a javascript-build project is as follows:

~~~
.
|-- .gitignore
|-- Makefile
|-- README.md
|-- lib
|   `-- packageName.js
`-- test
    `-- testPackageName.js
~~~

The basic javascript-build "Makefile" is as follows:

~~~ make
# Download javascript-build
JAVASCRIPT_BUILD_DIR ?= ../javascript-build
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
$$(shell [ -f $(JAVASCRIPT_BUILD_DIR)/$(notdir $(1)) ] && cp $(JAVASCRIPT_BUILD_DIR)/$(notdir $(1)) . || $(call WGET_CMD, $(1)))
endif
endef
WGET_CMD = if command -v wget >/dev/null 2>&1; then wget -q -c $(1); else curl -f -Os $(1); fi
$(eval $(call WGET, https://craigahobbs.github.io/javascript-build/Makefile.base))
$(eval $(call WGET, https://craigahobbs.github.io/javascript-build/jsdoc.json))
$(eval $(call WGET, https://craigahobbs.github.io/javascript-build/eslint.config.js))

# Include javascript-build
include Makefile.base

clean:
	rm -rf Makefile.base jsdoc.json eslint.config.js
~~~

Note that the makefile automatically downloads "Makefile.base", "jsdoc.json", and "eslint.config.js"
from javascript-build. It continually updates its development dependencies to the
latest stable versions.

Here is a typical javascript-build project ".gitignore" file:

~~~
/build/
/node_modules/
/Makefile.base
/eslint.config.js
/jsdoc.json
/package-lock.json
~~~

Notice that "Makefile.base", "eslint.config.js", "jsdoc.json", and are ignored because
they are downloaded by the Makefile.


## Make Targets

javascript-build exposes build commands as "phony" make targets. For example, to run all pre-commit
targets, use the `commit` target:

~~~
make commit
~~~

The following targets are available:

### commit

Execute the [test](#test), [lint](#lint), [doc](#doc), and [cover](#cover) targets. This target
should be run prior to any commit.

### test

Run the unit tests in the "test" directory.

To run a single unit test, use the "TEST" make variable:

~~~
make test TEST='My Test'
~~~

### lint

Run eslint on JavaScript source files under the "lib" directory.

### doc

Run jsdoc on JavaScript source files under the "lib" directory. The HTML documentation index is
located at "build/doc/index.html".

### cover

Run unit tests with coverage. By default, "make cover" fails if coverage is less than 100%. The HTML
coverage report index is located at "build/coverage/index.html".

The "TEST" make variable is supported as described in the [test](#test) target above.

### clean

Delete all development artifacts.

### superclean

Delete all development artifacts and downloaded images.

### changelog

Create and update the project's changelog file.

### publish

Publish the package to npm.

### gh-pages

Publish the application or project documentation to GitHub Pages. It first executes the `clean` and
`commit` targets to produce a clean build.

The repository is then git-cloned (or pulled) to the "../\<repository-name>.gh-pages" directory, the
"gh-pages" branch is checked-out, and the directories and files defined by the "GHPAGES_SRC" make
variable are rsync-ed there. Afterward, review the changes, commit, and push to publish.

To create a "gh-pages" branch, enter the following shell commands:

~~~
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "initializing gh-pages branch"
git push origin gh-pages
~~~


## Make Options

To view the commands of any make target without executing, use the "-n" make argument:

~~~
make -n test
~~~

To run targets in parallel, use the "-j" make argument. This can significantly decrease the time of
the [commit](#commit) target.

~~~
make -j commit
~~~


## Make Variables

javascript-build exposes several make variables that can be modified in your makefile following the
base makefile include. For example, to change the Node image:

~~~ make
include Makefile.base

NODE_IMAGE := node:15
~~~

The following variables are supported:

- `NODE_IMAGE` - The node image.

- `NODE_TEST_ARGS` - The `node --test` command line arguments. Default is "--test-reporter spec test/".

- `C8_VERSION` - The [c8](https://www.npmjs.com/package/c8) package version.

- `C8_ARGS` - The c8 tool's command line arguments. Default is "--100 --all --allowExternal --src lib/ --src test/".

- `ESLINT_VERSION` - The [eslint](https://www.npmjs.com/package/eslint) package version.

- `ESLINT_ARGS` - The eslint tool's command line arguments. Default is "lib/ test/".

- `JSDOC_VERSION` - The [jsdoc](https://www.npmjs.com/package/jsdoc) package version.

- `JSDOC_ARGS` - The jsdoc tool's command line arguments. Default is "-c jsdoc.json -r README.md lib/".

- `JSDOM_VERSION` - The [jsdom](https://www.npmjs.com/package/jsdom) package version.

- `USE_JSDOM` - If set, [jsdom](https://www.npmjs.com/package/jsdom) is added as a development dependency.


### Pre-Include Make Variables

The following make variables must be defined prior to the inclusion of the base makefile. This is
because they modify the make targets that javascript-build generates on include. For example, to
override the gh-pages source directories and files:

~~~ make
GHPAGES_SRC := lib/my-static-application/

include Makefile.base
~~~

- `GHPAGES_SRC` - The gh-pages target's source directories and files. Directories must end with a
  slash ("/"). Default is "build/doc/".


### Other Make Variables

- `USE_PODMAN` - Use [podman](https://podman.io/) and test with the official Node image.

~~~
make commit USE_PODMAN=1
~~~


## Extending javascript-build

All of the javascript-build [targets](#make-targets) may be extended either by adding additional
commands or adding a target dependency. Add additional commands to execute when a target (and all
its dependencies) is complete:

~~~ make
commit:
	@echo 'Build succeeded!'
~~~

Add a target dependency when you want the new dependency to execute in parallel (for
[parallel builds](#make-options)):

~~~ make
.PHONY: other-stuff
other-stuff:
    # do stuff...

commit: other-stuff
~~~


## Make Tips and Tricks

### Embed JavaScript in a Makefile

JavaScript can be embedded in a makefile by first defining the JavaScript script, exporting the
script, and executing the script with Node's "-e" argument. Make variables can even be incorporated
into the JavaScript script. Here's an example:

~~~ make
TITLE := Hello, World!
COUNT := 3

define JAVASCRIPT_SCRIPT
console.log('$(TITLE)');
for (let x = 1; x < $(COUNT) + 1; x++) {
    console.log(`x = $${x}`);
}
endef
export JAVASCRIPT_SCRIPT

.PHONY: javascript-script
javascript-script:
	node --input-type=module -e "$$JAVASCRIPT_SCRIPT"
~~~

Running make yields the following output:

~~~
Hello, World!
x = 1
x = 2
x = 3
~~~
