#!/bin/sh
# The current directory is a mounted volume, and is owned by the
# user running Docker on the host machine under linux (inc docker-machine).
#
# We don't want to trample all over the contents of this directory
# with files owned by root. So create a new user with the same UID,
# and drop privileges before running any commands.

# Get the numeric user ID of the current directory.
uid=$(ls -nd . | awk '{ print $3 }')

# Create an `mailme` user with that ID, and the current directory
# as its home directory.
if [[ $uid -eq 0 ]]; then
    # Don't try and create a user with uid 0 since it will fail.
    # Works around issue with docker for mac running containers
    # as root and not the user. Instead we just create the mailme
    # user since files will still be owned by the host's user
    # due to the way osxfs works.
    useradd -Md $(pwd) mailme
else
    useradd -Md $(pwd) -u $uid mailme
fi

echo "Starting with user: 'mailme' uid: $(id -u mailme)"

# Switch to that user and execute our actual command.
exec su mailme -c 'exec "$@"' sh -- "$@"
