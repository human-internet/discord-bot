#!/bin/bash

# Script to start the docker container
# usage
# 1. ./app.sh start dev to start the development container
# 2. ./app.sh stop dev to stop the development container
# 3. ./app.sh start dev -d to start the development container unattached
# 4. sudo ./app.sh start dev to start the development container as sudo or the root user

sudo_s=''
compose_file='docker-compose.dev.yml'

if [ -z "$1" ]
then
  echo "Please specify an action: start or stop"
else
  if [ -z "$2" ]
  then
    echo "Please specify an environment: dev or prod"
  else
    if [ "$EUID" -eq 0 ]
    then echo "Running as Sudo ..."
      sudo_s='sudo'
    fi

    if [ "$2" = 'prod' ]
    then
      echo "running production container"
      compose_file='docker-compose.prod.yml'
    else
      echo "running development container"
    fi

    if [ "$1" = 'start' ]
    then
      if [ -z "$3" ]
      then
        $sudo_s docker compose -f "$compose_file" up
      else
        $sudo_s docker compose -f "$compose_file" up "$3"
      fi
    else
      $sudo_s docker compose -f "$compose_file" down
    fi
  fi
fi