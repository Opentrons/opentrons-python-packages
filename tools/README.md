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
