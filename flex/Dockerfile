# Use the official Python 3.10 image for the target platform.
# The --platform argument will be honored by Buildx.
FROM --platform=$BUILDPLATFORM python:3.10-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Prevent services from starting during package installation.
RUN echo '#!/bin/sh\nexit 101' > /usr/sbin/policy-rc.d && chmod +x /usr/sbin/policy-rc.d

# Install build dependencies and the AArch64 cross-compiler.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        swig \
        libpcsclite-dev \
        git \
        gcc-aarch64-linux-gnu && \
    rm -rf /var/lib/apt/lists/* && \
    rm /usr/sbin/policy-rc.d

# Set the cross-compiler environment variables so that C extensions are built for ARM64.
ENV CC=aarch64-linux-gnu-gcc
ENV CXX=aarch64-linux-gnu-g++

# Upgrade pip and install the build backend.
RUN pip install --upgrade pip && pip install build

# Set the working directory and copy the external pyscard source.
WORKDIR /app
COPY pyscard-src/ .

# Build the wheel; the output will be placed in /app/dist.
RUN python -m build

# Exit immediately after the build.
CMD ["/bin/true"]
