#!/bin/bash
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
    $sudo_s docker compose -f docker-compose.dev.yml down
  else
    $sudo_s docker compose -f docker-compose.prod.yml down
  fi
fi

#docker compose up -d
