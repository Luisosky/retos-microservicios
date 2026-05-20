#!/bin/bash
# Ajusta el grupo del socket de Docker a la GID que Jenkins ya tiene en su grupo "docker"
# (necesario porque Docker Desktop en Windows expone el socket como root:root)
set -e

if [ -S /var/run/docker.sock ]; then
  SOCK_GID="$(stat -c '%g' /var/run/docker.sock)"
  DOCKER_GROUP_GID="$(getent group docker | cut -d: -f3 || true)"
  if [ -n "$DOCKER_GROUP_GID" ] && [ "$SOCK_GID" != "$DOCKER_GROUP_GID" ]; then
    chgrp "$DOCKER_GROUP_GID" /var/run/docker.sock || true
  fi
  chmod 660 /var/run/docker.sock || true
fi

# Pasa el control al entrypoint original como usuario jenkins
exec gosu jenkins /usr/local/bin/jenkins.sh "$@"
