#!/bin/bash
# This is a script that executes in the docker container. It will not work
# if you run it outside the container, and it's a bad idea to try

# we want to make sure that a) we are able to read the files in the volume, and
# that b) when we modify them we leave the host able to modify them (without sudo)
# as well. to accomplish (a), we need to be inside the permission set of the files
# in the volume, which is best accomplished by making ourselves its owner. to
# accomplish (b), we need to make sure that we don't add files that are under our
# own user and group.
#
# We can do this by
# - figuring out the numeric owner of the files in the volume
# - if necessary, making a new user with that uid. this is necessary on linux hosts
#   where the files in the volume keep their host-side owners while we run as root.
#   on osx, the volume mount hides the difference in users, and files will present
#   inside the container as owned by root, and outside as owned by the user even
#   if we make new files as root inside the container.
# - if we made a new user, chown everything to the new name - files continue to be
#   easily accessible on the host side, because we've used the same uid and gid
# - if we made a new user, run the command as that user

# what numeric group id and user id owns README.md in the volume?
gid=`stat -c %g /build-environment/python-package-index/README.md`
uid=`stat -c %u /build-environment/python-package-index/README.md`

# does root - our current user - own them?
if [[ "$uid" -ne "0" ]] ; then
    echo 'Changing ownership of SDK files'
    # a non-root user owns these files. let's make ourselves a user. we'll use the same
    # UID and GID so everything stays consistent with the host. we can give the
    # user whatever name we want.
    groupadd -g $gid builder
    useradd -l -u $uid -g builder builder
    preamble="runuser -u builder --"
    echo 'Ownership changed, will run as builder'
else
    # if this is on a mac host or a linux host that is running in a root-owned directory
    # for some reason (never do this) then root owns them, and we don't really need to
    # do anything special
    preamble=""
    echo 'No ownership changes necessary'
fi
# use exec here because this script is the container entrypoint (PID1) and we need to
# keep PID1 running for the container to keep running
echo 'Executing build'
exec ${preamble} /usr/bin/env python3 $@
