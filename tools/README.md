# Build Tools

This subdirectory holds the local build tools we use for building the python packages. They are responsible for build orchestration and kicking off everything.

This tooling uses [poetry](python-poetry.org) with some plugins:
- [poetry-dynamic-versioning](https://pypi.org/project/poetry-dynamic-versioning/). to take versions from git
- [poe-the-poet](https://pypi.org/project/poethepoet/) to run tasks like test

You don't need to install these to _use_ the tooling - docker takes care of that - but you do need to install them to _change_ the tooling.

You do need to install docker for your preferred platform.

## Using Poetry

Because we use poe, we can get away without having a wrapping makefile for dev tasks.

You can

- *set up*: using `poetry install`
- *lint*: using `poetry poe lint`
- *format*: using `poetry poe format`
- *test*: using `poetry poe test`
- *try a build*: using `poetry run builder.host.run`
