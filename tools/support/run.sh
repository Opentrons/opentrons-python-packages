#!/bin/bash
# This is a script that executes in the docker container. It will not work
# if you run it outside the container, and it's a bad idea to try
gid=`stat -c %g /build-environment/python-package-index/README.md`
uid=`stat -c %u /build-environment/python-package-index/README.md`
groupadd -g $gid builder
useradd -l -u $uid -g builder builder
chown -R $uid:$gid /build-environment/arm-buildroot-linux-gnueabihf_sdk-buildroot

exec runuser -u builder -- /usr/bin/env python3 $@
