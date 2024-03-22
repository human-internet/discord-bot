#!/bin/bash

# Script to start the docker container
# usage
# 1. ./start.sh dev to start the development container
# 2. ./start.sh dev -d to start the development container unattached
# 3. sudo ./start.sh dev to start the development container as sudo or the root user

sudo_s=''

if [ -z "$1" ]
then
  echo "Please specify a parameter: dev or prod"
else
  if [ "$EUID" -eq 0 ]
  then echo "Running as Sudo ..."
    sudo_s='sudo'
  fi

  if [ "$1" = 'dev' ]
  then
    $sudo_s docker compose -f docker-compose.dev.yml up "$2"
  else
    $sudo_s docker compose -f docker-compose.prod.yml up "$2"
  fi
fi

#docker compose up -d
