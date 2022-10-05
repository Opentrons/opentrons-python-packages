# Build Tools

This subdirectory holds the local build tools we use for building the python packages. They are responsible for build orchestration and kicking off everything.

This tooling uses [poetry](python-poetry.org) with some plugins:
- [poetry-dynamic-versioning](https://pypi.org/project/poetry-dynamic-versioning/). to take versions from git
- [poe-the-poet](https://pypi.org/project/poethepoet/) to run tasks like test

You don't need to install these to _use_ the tooling - docker takes care of that - but you do need to install them to _change_ the tooling.

You do need to install docker for your preferred platform.

## Setting up to develop the build tools

Install poetry:

``` shell
curl -sSL https://install.python-poetry.org | python3 -
```

Install required plugins:

``` shell
          poetry self add "poetry-dynamic-versioning[plugin]"
          poetry self add "poethepoet[poetry_plugin]"
```

Set up the local environment:

``` shell
poetry install
```

## Using Poetry

Because we use poe, we can get away without having a wrapping makefile for dev tasks.

You can

- *set up*: using `poetry install`
- *lint*: using `poetry poe lint`
- *format*: using `poetry poe format`
- *test*: using `poetry poe test`
- *try a build*: using `poetry poe run-build`

## Testing Build Tools

The top-level `./build` script entrypoint is going to mostly try to download the latest release of the build tools docker container rather than use your local stuff. It also lives in a top level directory which is annoying to use. To test locally you can use the poetry entrypoint `poetry poe run-build`.

## How does this all work, anyway?

The core of the problem this package solves is building python packages for arm7hf on an x86_64 machine - cross compiling them. To do this it takes a lot of cues and support from buildroot.

We need a stable environment for the compilation, and we'll be messing with shell settings, so we do the work in docker. That means we have code that has to run in docker (container side) and code that has to run outside of docker, to manage docker (host-side).

### Host side

The host-side code is in `builder/host` and `builder/common`. The job of this code is to build or pull docker containers, and then run a docker container with correct flags. That's not a lot, and that's good, because that means we can have approximately 0 dependencies locally. This is why you can run `build-packages` with just python without having to do poetry setup.

### Container side

The container side code has to actually build all the packages. This duplicates some of the functionality of buildroot. Its job is to
1. Find the package and run its `build.py` (in `builder/package_build/orchestrate.py`)
2. Make sure we have everything we need to build the package, such as 
   - package sources (`builder/package_build/download.py`)
   - package build dependencies (`builder/package_build/build_wheel.py`)
   - an activated buildroot sdk
   - an activated python virtual environment with the build dependencies
   - correct environments for forcing python to cross-compile
3. Actually run the build and harvest the results (also `build_wheel.py`)

The most complex part of this is making sure there's a correct environment to build things. The environment is important because it's the only way to pass certain options to the wheel builder (like the platform it should compile for) and provide cross compilation tools. This is done by having a long-running interactive shell that we communicate with in `builder/package_build/shell_environment.py`. 
