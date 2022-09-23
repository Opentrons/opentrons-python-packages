FROM python:3.10-slim-bullseye
MAINTAINER Opentrons Engineering <engineering@opentrons.com>

ARG HOST_USER_ID=1000
ARG HOST_GROUP_ID=1000


ENV BUILDENV_ROOT=/build-environment
ENV POETRY_HOME=/build-environment/poetry
ENV POETRY_VERSION=1.2.1
ENV PATH=$PATH:/build-environment/poetry/bin
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV HOME=/build-environment

RUN apt update && apt install -y curl wget file
RUN mkdir -p /${POETRY_HOME}/poetry \
    && chown -R ${HOST_USER_ID} //build-environment
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
USER ${HOST_USER_ID}:${HOST_GROUP_ID}

WORKDIR /build-environment

VOLUME /build-environment/python-package-index

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry self add "poetry-dynamic-versioning[plugin]"
RUN poetry self add 'poethepoet[poetry_plugin]'

# TODO: This should be a release version of the SDK, but one does not
# exist yet.
RUN \
    cd /build-environment \
    && wget https://opentrons-buildroot-ci.s3.amazonaws.com/439bccec-fff5-4501-9074-f463408da59a/opentrons-buildroot/arm-buildroot-linux-gnueabihf_sdk-buildroot.tar.gz \
    && tar xf ./arm-buildroot-linux-gnueabihf_sdk-buildroot.tar.gz \
    && cd arm-buildroot-linux-gnueabihf_sdk-buildroot \
    && ./relocate-sdk.sh

ADD . .
RUN cd /build-environment \
   && poetry install

ENTRYPOINT ["poetry", "run", "run-build-internal", "--package-repo-base=/build-environment/python-package-index", "--buildroot-sdk-base=/build-environment/arm-buildroot-linux-gnueabihf_sdk-buildroot"]
