FROM python:3.10-slim-bullseye
MAINTAINER Opentrons Engineering <engineering@opentrons.com>

ENV BUILDENV_ROOT=/build-environment
ENV POETRY_HOME=/build-environment/poetry
ENV POETRY_VERSION=1.2.1
ENV PATH=$PATH:/build-environment/poetry/bin
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV HOME=/build-environment

RUN apt update && apt install -y curl wget file git
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN mkdir /build-environment
COPY support/run.sh /build-environment/

# TODO: This should be a release version of the SDK, but one does not
# exist yet.
RUN \
    cd /build-environment \
    && wget https://opentrons-buildroot-ci.s3.amazonaws.com/439bccec-fff5-4501-9074-f463408da59a/opentrons-buildroot/arm-buildroot-linux-gnueabihf_sdk-buildroot.tar.gz \
    && tar xf ./arm-buildroot-linux-gnueabihf_sdk-buildroot.tar.gz \
    && cd arm-buildroot-linux-gnueabihf_sdk-buildroot \
    && ./relocate-sdk.sh

RUN mkdir -p /${POETRY_HOME}/poetry \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry self add "poetry-dynamic-versioning[plugin]" \
    && poetry self add 'poethepoet[poetry_plugin]'

COPY README.md pyproject.toml poetry.lock /build-environment/tools/
COPY builder /build-environment/tools/builder/

RUN \
    cd /build-environment/tools \
    && poetry install \
    && poetry build \
    && pip install ./dist/builder-*.whl

RUN   cd /build-environment && rm -rf ./tools && rm -rf ${POETRY_HOME}

VOLUME /build-environment/python-package-index
WORKDIR /build-environment

ENTRYPOINT ["/build-environment/run.sh", "-m", "builder.container", "--package-repo-base=/build-environment/python-package-index", "--buildroot-sdk-base=/build-environment/arm-buildroot-linux-gnueabihf_sdk-buildroot"]
